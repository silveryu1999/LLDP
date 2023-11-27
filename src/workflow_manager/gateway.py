import json
import gevent
from gevent import monkey
monkey.patch_all()
import sys
from flask import Flask, request
from repository import Repository
from parser import Parser
import requests
import time

sys.path.append('../../config')
import config

app = Flask(__name__)
repo = Repository()
parser = Parser("192.168.3.100", ["192.168.3.101", "192.168.3.102", "192.168.3.103", "192.168.3.104"],
                ['cycles', 'epigenomics', 'genome', 'soykb'])

def trigger_function(workflow_name, request_id, function_name):
    # info = repo.get_function_info(function_name, workflow_name + '_function_info')
    
    ip_to_info = repo.get_function_ip_to_specific(request_id, function_name)

    ip = ''
    if config.CONTROL_MODE == 'WorkerSP':
        ip = ip_to_info['ip']
    elif config.CONTROL_MODE == 'MasterSP':
        ip = config.MASTER_HOST
    url = 'http://{}/request'.format(ip)
    data = {
        'request_id': request_id,
        'workflow_name': workflow_name,
        'function_name': function_name,
        'no_parent_execution': True
    }
    requests.post(url, json=data)

def run_workflow(workflow_name, request_id, parse_mode):
    repo.create_request_doc(request_id)

    # allocate works
    start_functions = repo.get_start_functions(workflow_name + '_workflow_metadata')
    start = time.time()
    jobs = []   
    for n in start_functions:
        jobs.append(gevent.spawn(trigger_function, workflow_name, request_id, n))
    gevent.joinall(jobs)
    end = time.time()

    # clear memory and other stuff
    if config.CLEAR_DB_AND_MEM:
        master_addr  = ''
        if config.CONTROL_MODE == 'WorkerSP':
            master_addr = repo.get_all_addrs(workflow_name + '_workflow_metadata')[0]
        elif config.CONTROL_MODE == 'MasterSP':
            master_addr = config.MASTER_HOST
        clear_url = 'http://{}/clear'.format(master_addr)
        requests.post(clear_url, json={'request_id': request_id, 'master': True, 'workflow_name': workflow_name})

        # delete schedule result in master redis
        repo.clear_mem(request_id)
    
    if parse_mode == "Palette+LAC" or parse_mode == "Palette+LAF":
        parser.palette_clear(request_id) # mode 2&3 needed
    if parse_mode == "FaaSFlow":
        parser.faasflow_clear(request_id)
    
    return end - start

@app.route('/run', methods = ['POST'])
def run():
    data = request.get_json(force=True, silent=True)
    workflow = data['workflow']
    request_id = data['request_id']
    logging.info('processing request ' + request_id + '...')

    parse_mode = data['parse_mode']

    # parsing here
    start = time.time()
    if parse_mode == "Random":
        parser.random_parsing(workflow, request_id)
    elif parse_mode == "Robin":
        parser.rr_parsing(workflow, request_id)
    elif parse_mode == "Palette+CH":
        parser.palette_parsing(workflow, request_id, 1)
    elif parse_mode == "Palette+LAC":
        parser.palette_parsing(workflow, request_id, 2)
    elif parse_mode == "Palette+LAF":
        parser.palette_parsing(workflow, request_id, 3)
    elif parse_mode == "FaaSFlow":
        parser.faasflow_parsing(workflow, request_id)
    else:
        print("Warning: No parsing mode specified!")
        return json.dumps({'status': 'ok'})

    cost = time.time() - start
    logging.info('parsing request ' + request_id + ', cost: ' + str(cost))

    repo.log_status(workflow, request_id, 'EXECUTE')
    latency = run_workflow(workflow, request_id, parse_mode)
    repo.log_status(workflow, request_id, 'FINISH')
    return json.dumps({'status': 'ok', 'latency': latency})

@app.route('/clear_container', methods = ['POST'])
def clear_container():
    data = request.get_json(force=True, silent=True)
    workflow = data['workflow']
    addrs = repo.get_all_addrs(workflow + '_workflow_metadata')
    jobs = []
    for addr in addrs:
        clear_url = f'http://{addr}/clear_container'
        jobs.append(gevent.spawn(requests.get, clear_url))
    gevent.joinall(jobs)
    return json.dumps({'status': 'ok'})

from gevent.pywsgi import WSGIServer
import logging
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%H:%M:%S', level='INFO')
    server = WSGIServer((sys.argv[1], int(sys.argv[2])), app)
    server.serve_forever()