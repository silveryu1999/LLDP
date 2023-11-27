import yaml
import component
import sys
import networkx as nx

sys.path.append('../../config')
import config

yaml_file_addr = config.WORKFLOW_YAML_ADDR

def parse(workflow_name):
    data = yaml.load(open(yaml_file_addr[workflow_name]), Loader=yaml.FullLoader)
    global_input = dict()
    start_functions = []
    nodes = dict()
    parent_cnt = dict()
    foreach_functions = set()
    merge_funtions = set()
    total = 0
    dag = nx.DiGraph()

    if 'global_input' in data:
        for key in data['global_input']:
            parameter = data['global_input'][key]['value']['parameter']
            global_input[parameter] = data['global_input'][key]['size']
    functions = data['functions']
    parent_cnt[functions[0]['name']] = 0
    for function in functions:
        name = function['name']
        source = function['source']
        runtime = function['runtime']

        input_files = dict()
        output_files = dict()
        next = list()
        nextDis = list()
        nextBytes = list()
        send_byte = 0
        if 'input' in function:
            for key in function['input']:
                input_files[key] = {'function': function['input'][key]['value']['function'],
                                    'parameter': function['input'][key]['value']['parameter'],
                                    'size': function['input'][key]['size'], 'arg': key,
                                    'type': function['input'][key]['type']}
        if 'output' in function:
            for key in function['output']:
                output_files[key] = {'size': function['output'][key]['size'], 'type': function['output'][key]['type']}
                send_byte += function['output'][key]['size']
        send_time = send_byte / config.NETWORK_BANDWIDTH
        conditions = list()
        if 'next' in function:
            foreach_flag = False
            if function['next']['type'] == 'switch':
                conditions = function['next']['conditions']
            elif function['next']['type'] == 'foreach':
                foreach_flag = True
            for n in function['next']['nodes']:
                if name in foreach_functions:
                    merge_funtions.add(n)
                if foreach_flag:
                    foreach_functions.add(n)
                next.append(n)
                nextDis.append(send_time)
                nextBytes.append(send_byte)
                if n not in parent_cnt:
                    parent_cnt[n] = 1
                else:
                    parent_cnt[n] = parent_cnt[n] + 1

                dag.add_edge(name, n, bytes=send_byte, time=send_time)

        current_function = component.function(name, [], next, nextDis, nextBytes, source, runtime,
                                              input_files, output_files, conditions)

        if 'scale' in function:
            current_function.set_scale(function['scale'])
        if 'mem_usage' in function:
            current_function.set_mem_usage(function['mem_usage'])
        if 'split_ratio' in function:
            current_function.set_split_ratio(function['split_ratio'])

        dag.add_node(name, runtime = runtime)

        total = total + 1
        nodes[name] = current_function

    for name in nodes:
        if name not in parent_cnt or parent_cnt[name] == 0:
            parent_cnt[name] = 0
            start_functions.append(name)
        for next_node in nodes[name].next:
            nodes[next_node].prev.append(name)

    topo = list(nx.topological_sort(dag))
    out = {}
    for i in range(len(topo)):
        adj_raw = list(dag.successors(topo[i]))

        if len(adj_raw) <= 1:
            adj = adj_raw
        else:
            adj = sorted(adj_raw, key=lambda x : topo.index(x))
            
        out[topo[i]] = adj

    workflow = component.workflow(workflow_name, start_functions, nodes, global_input, total, parent_cnt, foreach_functions, merge_funtions, dag, topo, out)

    return workflow
