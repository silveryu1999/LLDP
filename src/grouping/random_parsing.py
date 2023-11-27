import sys
import parse_yaml
import queue
import component
import repository
import yaml
import random

sys.path.append('../../config')
import config

def random_parsing(workflow: component.workflow, node_info):
    func_ip = {}
    ip_list = list(node_info.keys())
    function_info_dict = {}
    function_info_raw_dict = {}
    for func_name in workflow.nodes.keys():
        # group_ip[func_name] = ip_list[hash(func_name) % len(ip_list)]
        func_ip[func_name] = ip_list[random.randint(0, len(ip_list) - 1)]

    for func_name in workflow.nodes.keys():
        func = workflow.nodes[func_name]
        to = get_type(workflow, func_name, func, func_ip)
        print(func_name, "to type:", to)
        ip = func_ip[func_name]
        function_info = {'function_name': func.name, 'runtime': func.runtime, 'to': to, 'ip': ip,
                         'parent_cnt': workflow.parent_cnt[func.name], 'conditions': func.conditions}
        function_info_raw = {'function_name': func.name, 'runtime': func.runtime, 'to': 'DB', 'ip': ip,
                             'parent_cnt': workflow.parent_cnt[func.name], 'conditions': func.conditions}
        function_input = dict()
        function_input_raw = dict()
        for arg in func.input_files:
            function_input[arg] = {'size': func.input_files[arg]['size'],
                                   'function': func.input_files[arg]['function'],
                                   'parameter': func.input_files[arg]['parameter'],
                                   'type': func.input_files[arg]['type']}
            function_input_raw[arg] = {'size': func.input_files[arg]['size'],
                                       'function': func.input_files[arg]['function'],
                                       'parameter': func.input_files[arg]['parameter'],
                                       'type': func.input_files[arg]['type']}
        function_output = dict()
        function_output_raw = dict()
        for arg in func.output_files:
            function_output[arg] = {'size': func.output_files[arg]['size'], 'type': func.output_files[arg]['type']}
            function_output_raw[arg] = {'size': func.output_files[arg]['size'], 'type': func.output_files[arg]['type']}
        function_info['input'] = function_input
        function_info['output'] = function_output
        function_info['next'] = func.next
        function_info_raw['input'] = function_input_raw
        function_info_raw['output'] = function_output_raw
        function_info_raw['next'] = func.next
        function_info_dict[func_name] = function_info
        function_info_raw_dict[func_name] = function_info_raw

    # if successor contains 'virtual', then the destination of storage should be propagated
    for name in workflow.nodes:
        for next_name in workflow.nodes[name].next:
            if next_name.startswith('virtual'):
                if function_info_dict[next_name]['to'] != function_info_dict[name]['to']:
                    function_info_dict[name]['to'] = 'DB+MEM'

    return function_info_dict, function_info_raw_dict, func_ip

def get_type(workflow, func_name, func, func_ip):
    not_in_same_node = False
    in_same_node = False
    for next_func_name in func.next:
        if func_ip[func_name] != func_ip[next_func_name]:
            not_in_same_node = True
        else:
            in_same_node = True
    if not_in_same_node and in_same_node:
        return 'DB+MEM'
    elif in_same_node:
        return 'MEM'
    else:
        return 'DB'
    
def save_grouping_config(workflow: component.workflow, node_info, info_dict, info_raw_dict):
    repo = repository.Repository(workflow.workflow_name)
    repo.save_function_info(info_dict, workflow.workflow_name + '_function_info')
    repo.save_function_info(info_raw_dict, workflow.workflow_name + '_function_info_raw')
    repo.save_basic_input(workflow.global_input, workflow.workflow_name + '_workflow_metadata')
    repo.save_start_functions(workflow.start_functions, workflow.workflow_name + '_workflow_metadata')
    repo.save_foreach_functions(workflow.foreach_functions, workflow.workflow_name + '_workflow_metadata')
    repo.save_merge_functions(workflow.merge_functions, workflow.workflow_name + '_workflow_metadata')
    repo.save_all_addrs(list(node_info.keys()), workflow.workflow_name + '_workflow_metadata')

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('usage: python3 grouping.py <workflow_name>, ...')

    # get node info
    node_info_list = yaml.load(open('node_info.yaml'), Loader=yaml.FullLoader)
    node_info_dict = {}
    for node_info in node_info_list['nodes']:
        node_info_dict[node_info['worker_address']] = node_info['scale_limit'] * 0.8

    # print("node info dict:", node_info_dict)

    workflow_pool = sys.argv[1:]
    for workflow_name in workflow_pool:
        workflow = parse_yaml.parse(workflow_name)
        print("Workflow:", workflow.workflow_name, "DAG Parsing Start...")

        function_info_dict, function_info_raw_dict, func_ip = random_parsing(workflow, node_info_dict)
        print("func ip:", func_ip)

        save_grouping_config(workflow, node_info_dict, function_info_dict, function_info_raw_dict)



