import sys
import parse_yaml
import queue
import component
import repository
import yaml
import networkx as nx
import matplotlib.pyplot as plt

sys.path.append('../../config')
import config

mem_usage = 0
max_mem_usage = 0
group_ip = {}
group_scale = {}

def init_graph(workflow, group_set, node_info):
    global group_ip, group_scale
    ip_list = list(node_info.keys())
    in_degree_vec = dict()
    q = queue.Queue()
    for name in workflow.start_functions:
        q.put(workflow.nodes[name])
        group_set.append((name, ))
    while q.empty() is False:
        node = q.get()
        for next_node_name in node.next:
            if next_node_name not in in_degree_vec:
                in_degree_vec[next_node_name] = 1
                q.put(workflow.nodes[next_node_name])
                group_set.append((next_node_name, ))
            else:
                in_degree_vec[next_node_name] += 1
    for s in group_set:
        group_ip[s] = ip_list[hash(s) % len(ip_list)]
        group_scale[s] = workflow.nodes[s[0]].scale
        node_info[group_ip[s]] -= workflow.nodes[s[0]].scale
    return in_degree_vec


def find_set(node, group_set):
    for node_set in group_set:
        if node in node_set:
            return node_set
    return None


def topo_search(workflow: component.workflow, in_degree_vec, group_set):
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
            if next_node_name in find_set(prev_name, group_set):
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

def mergeable(node1, node2, group_set, workflow: component.workflow, write_to_mem_nodes, node_info):
    global mem_usage, max_mem_usage, group_ip, group_scale
    node_set1 = find_set(node1, group_set)

    # same set?
    if node2 in node_set1: # same set
        return False
    node_set2 = find_set(node2, group_set)

    # group size no larger than GROUP_LIMIT
    if len(node_set1) + len(node_set2) > config.GROUP_LIMIT:
        return False

    # meet scale requirement?
    new_node_info = node_info.copy()
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
        print('Hit scale threshold', node_set1_scale, node_set2_scale)
        return False

    # check memory limit    
    if node1 not in write_to_mem_nodes:
        current_mem_usage = workflow.nodes[node1].nextDis[0] * config.NETWORK_BANDWIDTH
        if mem_usage + current_mem_usage > max_mem_usage: # too much memory consumption
            print('Hit memory consumption threshold')
            return False
        mem_usage += current_mem_usage
        write_to_mem_nodes.append(node1)

    # merge sets & update scale
    new_group_set = (*node_set1, *node_set2)

    group_set.append(new_group_set)
    group_ip[new_group_set] = best_fit_addr
    node_info[best_fit_addr] -= node_set1_scale + node_set2_scale
    group_scale[new_group_set] = node_set1_scale + node_set2_scale

    node_info[group_ip[node_set1]] += node_set1_scale
    node_info[group_ip[node_set2]] += node_set2_scale
    group_set.remove(node_set1)
    group_set.remove(node_set2) 
    group_ip.pop(node_set1)
    group_ip.pop(node_set2)
    group_scale.pop(node_set1)
    group_scale.pop(node_set2)
    return True

def merge_path(crit_vec, group_set, workflow: component.workflow, write_to_mem_nodes, node_info):
    for edge in crit_vec:
        if mergeable(edge[1][0], edge[0], group_set, workflow, write_to_mem_nodes, node_info):
            return True
    return False


def get_longest_dis(workflow, dist_vec):
    dist = 0
    node_name = ''
    for name in workflow.nodes:
        if dist_vec[name][0] > dist:
            dist = dist_vec[name][0]
            node_name = name
    return dist, node_name


def grouping(workflow: component.workflow, node_info):

    # initialization: get in-degree of each node
    group_set = list()
    critical_path_functions = set()
    write_to_mem_nodes = []
    in_degree_vec = init_graph(workflow, group_set, node_info)
    print("node_info:", node_info)
    print("group set:", group_set)
    print("group ip:", group_ip)
    print("group scale:", group_scale)

    while True:

        # break if every node is in same group
        if len(group_set) == 1:
            break

        # topo dp: find each node's longest dis and it's predecessor
        dist_vec, prev_vec = topo_search(workflow, in_degree_vec.copy(), group_set)
        crit_length, tmp_node_name = get_longest_dis(workflow, dist_vec)
        print('crit_length: ', crit_length)

        # find the longest path, edge descent sorted
        critical_path_functions.clear()
        crit_vec = dict()
        while tmp_node_name not in workflow.start_functions:
            crit_vec[tmp_node_name] = prev_vec[tmp_node_name]
            tmp_node_name = prev_vec[tmp_node_name][0]
        crit_vec = sorted(crit_vec.items(), key=lambda c: c[1][1], reverse=True)
        for k, v in crit_vec:
            critical_path_functions.add(k)
            critical_path_functions.add(v[0])

        # if can't merge every edge of this path, just break
        if not merge_path(crit_vec, group_set, workflow, write_to_mem_nodes, node_info):
            break
    return group_set, critical_path_functions

# define the output destination at function level, instead of one per key/file
def get_type(workflow, node, group_detail):
    not_in_same_set = False
    in_same_set = False
    for next_node_name in node.next:
        next_node = workflow.nodes[next_node_name]
        node_set = find_set(next_node.name, group_detail)
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

def get_max_mem_usage(workflow: component.workflow):
    global max_mem_usage
    for name in workflow.nodes:
        if not name.startswith('virtual'):
            max_mem_usage += (1 - config.RESERVED_MEM_PERCENTAGE - workflow.nodes[name].mem_usage) * config.CONTAINER_MEM * workflow.nodes[name].split_ratio
    return max_mem_usage


def save_grouping_config(workflow: component.workflow, node_info, info_dict, info_raw_dict, critical_path_functions):
    repo = repository.Repository(workflow.workflow_name)
    repo.save_function_info(info_dict, workflow.workflow_name + '_function_info')
    repo.save_function_info(info_raw_dict, workflow.workflow_name + '_function_info_raw')
    repo.save_basic_input(workflow.global_input, workflow.workflow_name + '_workflow_metadata')
    repo.save_start_functions(workflow.start_functions, workflow.workflow_name + '_workflow_metadata')
    repo.save_foreach_functions(workflow.foreach_functions, workflow.workflow_name + '_workflow_metadata')
    repo.save_merge_functions(workflow.merge_functions, workflow.workflow_name + '_workflow_metadata')
    repo.save_all_addrs(list(node_info.keys()), workflow.workflow_name + '_workflow_metadata')
    repo.save_critical_path_functions(critical_path_functions, workflow.workflow_name + '_workflow_metadata')

# def query(workflow: component.workflow, group_detail: List):
#     total = 0
#     merged = 0
#     for name, node in workflow.nodes.items():
#         for next_node_name in node.next:
#             total = total + 1
#             merged_edge = False
#             for s in group_detail:
#                 if name in s and next_node_name in s:
#                     merged_edge = True
#             if merged_edge:
#                 merged = merged + 1
#     return merged, total

def get_grouping_config(workflow: component.workflow, node_info_dict):

    global max_mem_usage, group_ip

    # grouping algorithm
    max_mem_usage = get_max_mem_usage(workflow)
    print("max_mem_usage:", max_mem_usage / (1024 * 1024), "MB")
    group_detail, critical_path_functions = grouping(workflow, node_info_dict)
    print("functions:", len(workflow.nodes), "groups:", len(group_detail))
    print("group_set:", group_detail)
    
    # print(query(workflow, group_detail))

    # building function info: both optmized and raw version
    ip_list = list(node_info_dict.keys())
    function_info_dict = {}
    function_info_raw_dict = {}
    for node_name in workflow.nodes:
        node = workflow.nodes[node_name]
        to = get_type(workflow, node, group_detail)
        ip = group_ip[find_set(node_name, group_detail)]
        function_info = {'function_name': node.name, 'runtime': node.runtime, 'to': to, 'ip': ip,
                         'parent_cnt': workflow.parent_cnt[node.name], 'conditions': node.conditions}
        function_info_raw = {'function_name': node.name, 'runtime': node.runtime, 'to': 'DB', 'ip': ip_list[hash(node.name) % len(ip_list)],
                             'parent_cnt': workflow.parent_cnt[node.name], 'conditions': node.conditions}
        function_input = dict()
        function_input_raw = dict()
        for arg in node.input_files:
            function_input[arg] = {'size': node.input_files[arg]['size'],
                                   'function': node.input_files[arg]['function'],
                                   'parameter': node.input_files[arg]['parameter'],
                                   'type': node.input_files[arg]['type']}
            function_input_raw[arg] = {'size': node.input_files[arg]['size'],
                                       'function': node.input_files[arg]['function'],
                                       'parameter': node.input_files[arg]['parameter'],
                                       'type': node.input_files[arg]['type']}
        function_output = dict()
        function_output_raw = dict()
        for arg in node.output_files:
            function_output[arg] = {'size': node.output_files[arg]['size'], 'type': node.output_files[arg]['type']}
            function_output_raw[arg] = {'size': node.output_files[arg]['size'], 'type': node.output_files[arg]['type']}
        function_info['input'] = function_input
        function_info['output'] = function_output
        function_info['next'] = node.next
        function_info_raw['input'] = function_input_raw
        function_info_raw['output'] = function_output_raw
        function_info_raw['next'] = node.next
        function_info_dict[node_name] = function_info
        function_info_raw_dict[node_name] = function_info_raw
    
    # if successor contains 'virtual', then the destination of storage should be propagated
    for name in workflow.nodes:
        for next_name in workflow.nodes[name].next:
            if next_name.startswith('virtual'):
                if function_info_dict[next_name]['to'] != function_info_dict[name]['to']:
                    function_info_dict[name]['to'] = 'DB+MEM'

    return node_info_dict, function_info_dict, function_info_raw_dict, critical_path_functions

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('usage: python3 grouping.py <workflow_name>, ...')

    # get node info
    node_info_list = yaml.load(open('node_info.yaml'), Loader=yaml.FullLoader)
    node_info_dict = {}
    for node_info in node_info_list['nodes']:
        node_info_dict[node_info['worker_address']] = node_info['scale_limit'] * 0.8
    
    print("node info dict:", node_info_dict)
        
    workflow_pool = sys.argv[1:]
    for workflow_name in workflow_pool:
        workflow = parse_yaml.parse(workflow_name)

        # topo = list(nx.topological_sort(workflow.dag))
        # out = {}

        # # print(topo)
        
        # for i in range(len(topo)):
        #     adj_raw = list(workflow.dag.successors(topo[i]))

        #     if len(adj_raw) <= 1:
        #         adj = adj_raw
        #     else:
        #         adj = sorted(adj_raw, key=lambda x : topo.index(x))
            
        #     out[topo[i]] = adj

        # # chain decomposition
        # iter = 1
        # id = {}
        # Z = []
        # V = [1 for i in range(len(topo))]
        # for i in range(len(topo)):
        #     id[topo[i]] = 0

        # while max(V) > 0:
        #     Zi = []
        #     pt = V.index(1)
        #     x = topo[pt]
        #     Zi.append(x)

        #     flag = True
        #     while flag == True:
        #         if len(out[x]) > 0:
        #             find = False
        #             for y in out[x]:
        #                 y_pt = topo.index(y)
        #                 if y_pt > pt and V[y_pt] == 1:
        #                     Zi.append(y)
        #                     x = y
        #                     find = True
        #                     break
        #             if find == True:
        #                 continue
        #             else:
        #                 flag = False
        #         else:
        #             flag = False

        #     print("Z", iter, ":", Zi)

        #     Z.append(Zi)
        #     for z in Zi:
        #         V[topo.index(z)] = 0
        #         id[z] = iter

        #     iter += 1

        for layer, nodes in enumerate(nx.topological_generations(workflow.dag)):
            # `multipartite_layout` expects the layer as a node attribute, so add the
            # numeric layer value as a node attribute
            for node in nodes:
                workflow.dag.nodes[node]["layer"] = layer

        # Compute the multipartite_layout using the "layer" node attribute
        pos = nx.multipartite_layout(workflow.dag, subset_key="layer")
        node_labels = nx.get_node_attributes(workflow.dag,'runtime')
        edge_labels = nx.get_edge_attributes(workflow.dag,'time')

        plt.figure(figsize=(60,60)) 
        nx.draw(workflow.dag, pos=pos, with_labels=False)
        nx.draw_networkx_labels(workflow.dag, pos=pos, labels = node_labels)
        nx.draw_networkx_edge_labels(workflow.dag, pos=pos, edge_labels = edge_labels)
        plt.show()
        plt.savefig(str("dag_graphs_runtime/" + workflow_name + "_time" + ".png"))
        
        # for start in workflow.start_functions:
        #     print("successors of", start, ":", list(workflow.dag.successors(start)))


        # print("workflow:", workflow.workflow_name, "grouping start...")
        # node_info, function_info, function_info_raw, critical_path_functions = get_grouping_config(workflow, node_info_dict)
        # print("node_info:", node_info)
        # for key, value in function_info.items():
        #     print("function name:", key, "ip:", value['ip'])
        # save_grouping_config(workflow, node_info, function_info, function_info_raw, critical_path_functions)