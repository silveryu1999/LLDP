import json
import yaml
import queue
import random
import redis
import sys
import copy
from gevent.lock import BoundedSemaphore

sys.path.append('../grouping')
import parse_yaml
from random_parsing import get_type as get_type_to

sys.path.append('../../config')
import config

class Parser:
    def __init__(self, master_ip, ip_addrs, workflow_pool):
        self.redis_list = {}
        self.worker_port = ":8000"
        self.ip_addrs = ip_addrs
        self.workflow_pool = workflow_pool
        self.redis_master = redis.StrictRedis(host=master_ip, port=config.REDIS_PORT, db=config.REDIS_DB)
        for ip in self.ip_addrs:
            self.redis_list[ip] = redis.StrictRedis(host=ip, port=config.REDIS_PORT, db=config.REDIS_DB)

        ########################### parser states here ###########################
        print("init parser states")

        ### workflow struct ###
        self.workflow_dict = {}
        for workflow_name in workflow_pool:
            self.workflow_dict[workflow_name] = parse_yaml.parse(workflow_name)

        ### rr states ###
        self.rr_lock = BoundedSemaphore()
        self.rr_index = 0

        ### palette states ###
        self.color_lock = BoundedSemaphore()
        self.color_table = {}
        self.color_count = [0 for ip in self.ip_addrs]

        ### faasflow states ###
        self.faasflow_lock = BoundedSemaphore()
        self.scale_per_request = {}
        self.node_info_list = yaml.load(open('node_info.yaml'), Loader=yaml.FullLoader)
        self.node_info_dict = {}
        for node_info in self.node_info_list['nodes']:
            self.node_info_dict[node_info['worker_address']] = node_info['scale_limit']

        self.in_degree_vec = {}
        self.group_set = {}
        self.ip_list = list(self.node_info_dict.keys())
        for workflow_name in workflow_pool:
            workflow = self.workflow_dict[workflow_name]
            self.in_degree_vec[workflow_name] = {}
            self.group_set[workflow_name] = []
            q = queue.Queue()
            for name in workflow.start_functions:
                q.put(workflow.nodes[name])
                self.group_set[workflow_name].append((name, ))
            while q.empty() is False:
                node = q.get()
                for next_node_name in node.next:
                    if next_node_name not in self.in_degree_vec[workflow_name]:
                        self.in_degree_vec[workflow_name][next_node_name] = 1
                        q.put(workflow.nodes[next_node_name])
                        self.group_set[workflow_name].append((next_node_name, ))
                    else:
                        self.in_degree_vec[workflow_name][next_node_name] += 1  


        ########################### runtime states here ###########################
        print("init runtime states")

    def write_to_mem(self, request_id, func_ip_to_dict):
        key = request_id + '_schedule.json'
        func_ip_dict_json = json.dumps(func_ip_to_dict)
        self.redis_master[key] = func_ip_dict_json
        for ip in self.ip_addrs:
            self.redis_list[ip][key] = func_ip_dict_json

        return
        
    def random_parsing(self, workflow_name, request_id):
        # random, no info needed
        workflow = self.workflow_dict[workflow_name]
        func_ip = {}

        for func_name in workflow.nodes.keys():
            func_ip[func_name] = self.ip_addrs[random.randint(0, len(self.ip_addrs) - 1)] + self.worker_port

        func_ip_to_dict = {}
        for func_name in workflow.nodes.keys():
            func = workflow.nodes[func_name]
            to = get_type_to(workflow, func_name, func, func_ip)
            func_ip_to_dict[func_name] = {'ip': func_ip[func_name], 'to': to}

        self.write_to_mem(request_id, func_ip_to_dict)
            
        return
    
    def rr_parsing(self, workflow_name, request_id):
        # round robin, no info needed
        workflow = self.workflow_dict[workflow_name]
        func_ip = {}

        for func_name in workflow.nodes.keys():
            self.rr_lock.acquire()
            func_ip[func_name] = self.ip_addrs[self.rr_index] + self.worker_port
            self.rr_index = (self.rr_index + 1) % len(self.ip_addrs)
            self.rr_lock.release()

        func_ip_to_dict = {}
        for func_name in workflow.nodes.keys():
            func = workflow.nodes[func_name]
            to = get_type_to(workflow, func_name, func, func_ip)
            func_ip_to_dict[func_name] = {'ip': func_ip[func_name], 'to': to}

        self.write_to_mem(request_id, func_ip_to_dict)

        return
    
    def palette_parsing(self, workflow_name, request_id, mode):
        # chain decomposition, only edge topo is needed
        # mode
        # 1: consistent hashing (poor LB)
        # 2: color table + color least assigned (better LB) (no locality between DAG invocations)
        # 3: color table + function least assigned (best LB) (no locality between DAG invocations)
        workflow = self.workflow_dict[workflow_name]
        func_ip = {}

        iter = 1
        id = {}
        Z = []
        V = [1 for i in range(len(workflow.topo))]
        for i in range(len(workflow.topo)):
            id[workflow.topo[i]] = 0

        while max(V) > 0:
            Zi = []
            pt = V.index(1)
            x = workflow.topo[pt]
            Zi.append(x)

            flag = True
            while flag == True:
                if len(workflow.out[x]) > 0:
                    find = False
                    for y in workflow.out[x]:
                        y_pt = workflow.topo.index(y)
                        if y_pt > pt and V[y_pt] == 1:
                            Zi.append(y)
                            x = y
                            find = True
                            break
                    if find == True:
                        continue
                    else:
                        flag = False
                else:
                    flag = False

            Z.append(Zi)
            for z in Zi:
                V[workflow.topo.index(z)] = 0
                id[z] = iter

            iter += 1

        if mode == 1:
            for z in Z:
                ip = self.ip_addrs[hash(str(z)) % len(self.ip_addrs)] + self.worker_port
                for func_name in z:
                    func_ip[func_name] = ip
        
        if mode == 2 or mode == 3:
            curr_color_count = [0 for ip in self.ip_addrs]
            for z in Z:
                self.color_lock.acquire()
                target = min(self.color_count)
                ixs = []

                for index, item in enumerate(self.color_count):
                    if item == target:
                        ixs.append(index)

                # break ties arbitrarily
                ix = ixs[random.randint(0, len(ixs) - 1)]
                if mode == 2:
                    self.color_count[ix] += 1
                if mode == 3:
                    self.color_count[ix] += len(z)
                self.color_lock.release()

                ip = self.ip_addrs[ix] + self.worker_port
                if mode == 2:
                    curr_color_count[ix] += 1
                if mode == 3:
                    curr_color_count[ix] += len(z)
                for func_name in z:
                    func_ip[func_name] = ip

            self.color_lock.acquire()
            self.color_table[request_id] = curr_color_count
            self.color_lock.release()
        
        func_ip_to_dict = {}
        for func_name in workflow.nodes.keys():
            func = workflow.nodes[func_name]
            to = get_type_to(workflow, func_name, func, func_ip)
            func_ip_to_dict[func_name] = {'ip': func_ip[func_name], 'to': to}

        self.write_to_mem(request_id, func_ip_to_dict)

        return
    
    def palette_clear(self, request_id):
        # clear palette mode 2&3 states after run
        self.color_lock.acquire()
        curr_color_count = self.color_table[request_id]
        for index, item in enumerate(curr_color_count):
            self.color_count[index] -= item
        del self.color_table[request_id]
        self.color_lock.release()

        return
    
    def minflow_parsing(self, workflow_name, request_id):
        # minflow, only edge info is needed

        return
    
    def faasflow_parsing(self, workflow_name, request_id):
        # grouping, both node and edge info needed
        workflow = self.workflow_dict[workflow_name]
        # func_ip = {}

        self.scale_per_request[request_id] = {}
        for ip in self.ip_list:
            self.scale_per_request[request_id][ip] = 0
        group_ip = {}
        group_scale = {}
        mem_usage = 0
        max_mem_usage = 0
        for name in workflow.nodes:
            max_mem_usage += (1 - config.RESERVED_MEM_PERCENTAGE - workflow.nodes[name].mem_usage) * config.CONTAINER_MEM * workflow.nodes[name].split_ratio

        # in_degree_vec = copy.copy(self.in_degree_vec[workflow_name])
        group_set = copy.copy(self.group_set[workflow_name])
        critical_path_functions = set()
        write_to_mem_nodes = []

        # assign ip to every group randomly
        self.faasflow_lock.acquire()
        for s in group_set:
            # group_ip[s] = self.ip_list[hash(s) % len(self.ip_list)]
            group_ip[s] = self.ip_list[random.randint(0, len(self.ip_list) - 1)]
            group_scale[s] = workflow.nodes[s[0]].scale
            self.node_info_dict[group_ip[s]] -= workflow.nodes[s[0]].scale
            self.scale_per_request[request_id][group_ip[s]] += workflow.nodes[s[0]].scale
        self.faasflow_lock.release()

        while True:
            # break if every node is in same group
            if len(group_set) == 1:
                break

            ############## origin ################

            # topo dp: find each node's longest dis and it's predecessor
            in_degree_vec = copy.copy(self.in_degree_vec[workflow_name])
            dist_vec, prev_vec = self.faasflow_topo_search(workflow, in_degree_vec, group_set)
            crit_length, tmp_node_name = self.faasflow_get_longest_dis(workflow, dist_vec)
            # print('crit_length: ', crit_length)

            critical_path_functions.clear()
            crit_vec = dict()
            while tmp_node_name not in workflow.start_functions:
                crit_vec[tmp_node_name] = prev_vec[tmp_node_name]
                tmp_node_name = prev_vec[tmp_node_name][0]
            crit_vec = sorted(crit_vec.items(), key=lambda c: c[1][1], reverse=True)
            for k, v in crit_vec:
                critical_path_functions.add(k)
                critical_path_functions.add(v[0])

            ############## modified ################

            # topo dp: find each node's longest dis and it's predecessor
            # in_degree_vec = copy.copy(self.in_degree_vec[workflow_name])
            # dist_vec, prev_vec = self.faasflow_topo_search(workflow, in_degree_vec, group_set)

            # Find_Flag = False
            # critical_path_functions.clear()
            # crit_vec = dict()

            # check_nodes = copy.copy(workflow.nodes)

            # while Find_Flag == False:
            #     crit_length, tmp_node_name = self.faasflow_get_longest_dis_modified(check_nodes, dist_vec)

            #     longest_node_name = tmp_node_name
            #     print('crit_length: ', crit_length)

            #     crit_vec_tmp = dict()
            #     while tmp_node_name not in workflow.start_functions:
            #         crit_vec_tmp[tmp_node_name] = prev_vec[tmp_node_name]
            #         tmp_node_name = prev_vec[tmp_node_name][0]

            #     if len(crit_vec_tmp) == 0:
            #         all_in_same_set = False
            #     else:
            #         all_in_same_set = True
            #         for k, v in crit_vec_tmp.items():
            #             set1 = self.faasflow_find_set(k, group_set)
            #             if v[0] not in set1:
            #                 all_in_same_set = False
            #                 break

            #     if all_in_same_set == False:
            #         Find_Flag = True
            #         crit_vec = crit_vec_tmp
            #     else:
            #         check_nodes.pop(longest_node_name)
            #         continue
            
            # crit_vec = sorted(crit_vec.items(), key=lambda c: c[1][1], reverse=True)
            # for k, v in crit_vec:
            #     critical_path_functions.add(k)
            #     critical_path_functions.add(v[0])

            if not self.faasflow_merge_path(crit_vec, group_set, workflow, write_to_mem_nodes, mem_usage, max_mem_usage, group_ip, group_scale, request_id):
                break

        print("group len:", len(group_set))

        func_ip_to_dict = {}
        for func_name in workflow.nodes.keys():
            func = workflow.nodes[func_name]
            to = self.faasflow_get_type(workflow, func, group_set)
            ip = group_ip[self.faasflow_find_set(func_name, group_set)]
            func_ip_to_dict[func_name] = {'ip': ip, 'to': to}

        self.write_to_mem(request_id, func_ip_to_dict)

        return
    
    def faasflow_topo_search(self, workflow, in_degree_vec, group_set):
        dist_vec = dict()  # { name: [dist, max_length] }
        prev_vec = dict()  # { name: [prev_name, length] }
        q = queue.Queue()
        for name in workflow.start_functions:
            q.put(workflow.nodes[name])
            dist_vec[name] = [workflow.nodes[name].runtime, 0]
            prev_vec[name] = []
        while q.empty() is False:
            node = q.get()
            pre_dist = dist_vec[node.name]
            prev_name = node.name
            for index in range(len(node.next)):
                next_node = workflow.nodes[node.next[index]]
                w = node.nextDis[index]
                next_node_name = next_node.name
                if next_node_name in self.faasflow_find_set(prev_name, group_set):
                    w = w / config.NET_MEM_BANDWIDTH_RATIO
                if next_node.name not in dist_vec:
                    dist_vec[next_node_name] = [pre_dist[0] + w + next_node.runtime, max(pre_dist[1], w)]
                    prev_vec[next_node_name] = [prev_name, w]
                elif dist_vec[next_node_name][0] < pre_dist[0] + w + next_node.runtime:
                    dist_vec[next_node_name] = [pre_dist[0] + w + next_node.runtime, max(pre_dist[1], w)]
                    prev_vec[next_node_name] = [prev_name, w]
                elif dist_vec[next_node_name][0] == pre_dist[0] + w + next_node.runtime and max(pre_dist[1], w) > \
                        dist_vec[next_node_name][1]:
                    dist_vec[next_node_name][1] = max(pre_dist[1], w)
                    prev_vec[next_node_name] = [prev_name, w]
                in_degree_vec[next_node_name] -= 1
                if in_degree_vec[next_node_name] == 0:
                    q.put(next_node)
        return dist_vec, prev_vec
    
    def faasflow_find_set(self, node, group_set):
        for node_set in group_set:
            if node in node_set:
                return node_set
        return None
    
    def faasflow_get_longest_dis(self, workflow, dist_vec):
        dist = 0
        node_name = ''
        for name in workflow.nodes:
            if dist_vec[name][0] > dist:
                dist = dist_vec[name][0]
                node_name = name
        return dist, node_name
    
    def faasflow_get_longest_dis_modified(self, nodes, dist_vec):
        dist = 0
        node_name = ''
        for name in nodes:
            if dist_vec[name][0] > dist:
                dist = dist_vec[name][0]
                node_name = name
        return dist, node_name

    def faasflow_merge_path(self, crit_vec, group_set, workflow, write_to_mem_nodes, mem_usage, max_mem_usage, group_ip, group_scale, request_id):
        for edge in crit_vec:
            if self.faasflow_mergeable(edge[1][0], edge[0], group_set, workflow, write_to_mem_nodes, mem_usage, max_mem_usage, group_ip, group_scale, request_id):
                return True
        return False
    
    def faasflow_mergeable(self, node1, node2, group_set, workflow, write_to_mem_nodes, mem_usage, max_mem_usage, group_ip, group_scale, request_id):
        node_set1 = self.faasflow_find_set(node1, group_set)
        
        # same set?
        if node2 in node_set1: # same set
            return False
        node_set2 = self.faasflow_find_set(node2, group_set)

        # group size no larger than GROUP_LIMIT
        if len(node_set1) + len(node_set2) > config.GROUP_LIMIT:
            return False
        
        # meet scale requirement?
        self.faasflow_lock.acquire()

        new_node_info = copy.copy(self.node_info_dict)
        node_set1_scale = group_scale[node_set1]
        node_set2_scale = group_scale[node_set2]
        new_node_info[group_ip[node_set1]] += node_set1_scale
        new_node_info[group_ip[node_set2]] += node_set2_scale
        best_fit_addr, best_fit_scale = None, 10000000
        for addr in new_node_info:
            if new_node_info[addr] >= node_set1_scale + node_set2_scale and new_node_info[addr] < best_fit_scale:
                best_fit_addr = addr
                best_fit_scale = new_node_info[addr]
        if best_fit_addr is None:
            return False
        
        # check memory limit
        if node1 not in write_to_mem_nodes:
            current_mem_usage = workflow.nodes[node1].nextDis[0] * config.NETWORK_BANDWIDTH
            if mem_usage + current_mem_usage > max_mem_usage: # too much memory consumption
                return False
            mem_usage += current_mem_usage
            write_to_mem_nodes.append(node1)
        
        # merge sets & update scale
        new_group_set = (*node_set1, *node_set2)

        group_set.append(new_group_set)
        group_ip[new_group_set] = best_fit_addr
        self.node_info_dict[best_fit_addr] -= node_set1_scale + node_set2_scale
        self.scale_per_request[request_id][best_fit_addr] += node_set1_scale + node_set2_scale
        group_scale[new_group_set] = node_set1_scale + node_set2_scale

        self.node_info_dict[group_ip[node_set1]] += node_set1_scale
        self.scale_per_request[request_id][group_ip[node_set1]] -= node_set1_scale
        self.node_info_dict[group_ip[node_set2]] += node_set2_scale
        self.scale_per_request[request_id][group_ip[node_set2]] -= node_set2_scale
        group_set.remove(node_set1)
        group_set.remove(node_set2)
        group_ip.pop(node_set1)
        group_ip.pop(node_set2)
        group_scale.pop(node_set1)
        group_scale.pop(node_set2)

        self.faasflow_lock.release()

        return True
    
    def faasflow_get_type(self, workflow, node, group_detail):
        not_in_same_set = False
        in_same_set = False
        for next_node_name in node.next:
            next_node = workflow.nodes[next_node_name]
            node_set = self.faasflow_find_set(next_node.name, group_detail)
            if node.name not in node_set:
                not_in_same_set = True
            else:
                in_same_set = True
        if not_in_same_set and in_same_set:
            return 'DB+MEM'
        elif in_same_set:
            return 'MEM'
        else:
            return 'DB'
    
    def faasflow_clear(self, request_id):
        # clear faasflow states, return the scales
        self.faasflow_lock.acquire()
        for ip, scale in self.scale_per_request[request_id].items():
            self.node_info_dict[ip] += scale
        del self.scale_per_request[request_id]
        self.faasflow_lock.release()
        return
    
    def ditto_parsing(self, workflow_name, request_id):
        # grouping, both node and edge info needed
        
        return
    
    def dynamic_parsing(self, workflow_name, request_id):
        # dynamic, runtime state is needed

        return
    
if __name__ == '__main__':
    parser = Parser("192.168.3.100", ["192.168.3.101", "192.168.3.102", "192.168.3.103", "192.168.3.104"],
                ['cycles', 'epigenomics', 'genome', 'soykb'])
    parser.faasflow_parsing("epigenomics", "test-id-12345678")
    parser.faasflow_clear("test-id-12345678")