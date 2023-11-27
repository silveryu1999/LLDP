from gevent import monkey
monkey.patch_all()
import uuid
import requests
import getopt
import sys
sys.path.append('..')
sys.path.append('../../../config')
from repository import Repository
import config
import pandas as pd
import time
import gevent

repo = Repository()
latencies = []
ticket = 0
running = 0
timeout = 0
RPM = 6
BANDWIDTH = 50
TEST_PER_WORKFLOW = 2 * 60

def run_workflow(workflow_name, request_id):
    print('----firing workflow----', request_id)
    global latencies, ticket, running, timeout
    ticket = ticket - 1
    running = running + 1
    if ticket > 0 and timeout < 3:
        gevent.spawn_later(60 / RPM, run_workflow, workflow_name, str(uuid.uuid4()))
    url = 'http://' + config.GATEWAY_ADDR + '/run'
    data = {'workflow':workflow_name, 'request_id': request_id}
    try:
        rep = requests.post(url, json=data, timeout=180)
        e2e_latency = rep.json()['latency']
        latencies.append(e2e_latency)
        print('e2e latency: ', e2e_latency)
    except Exception:
        print(f'{workflow_name} timeout')
        timeout = timeout + 1
    running = running - 1

def analyze_workflow():
    global latencies, timeout
    if timeout >= 3:
        return 'timeout'
    latencies.sort()
    if len(latencies) < 100:
        return latencies[-1]
    else:
        tail = int(len(latencies) / 100)
        return latencies[-tail]

def analyze(datamode):
    global RPM, BANDWIDTH, ticket, running, timeout, latencies
    # workflow_pool = ['cycles', 'epigenomics', 'genome', 'soykb', 'video', 'illgal_recognizer', 'fileprocessing', 'wordcount']
    workflow_pool = ['cycles']
    # tail_latencies = []
    cold_start_latencies = []
    warm_start_latencies = []
    for workflow in workflow_pool:
        print(f'----analyzing {workflow}, cold starting----')

        ticket = 1
        running = 0
        timeout = 0
        latencies = []
        gevent.spawn(run_workflow, workflow, str(uuid.uuid4()))
        gevent.sleep(5)
        while True:
            if running == 0 and timeout != 0: # timeout
                break
            if ticket == 0 and running == 0: # finished running
                break
            gevent.sleep(5)
        if timeout == 1:
            # tail_latencies.append('timeout')
            cold_start_latencies.append('timeout')
            clear_url = 'http://' + config.GATEWAY_ADDR + '/clear_container'
            data = {'workflow': workflow}
            requests.post(clear_url, json=data)
            gevent.sleep(5)
            continue

        cold_start_latencies.append(latencies[0])

        print(f'----analyzing {workflow}, warm starting----')

        # warm start latency analysis
        ticket = 1
        running = 0
        timeout = 0
        latencies = []
        gevent.spawn(run_workflow, workflow, str(uuid.uuid4()))
        gevent.sleep(5)
        while True:
            if running == 0 and timeout != 0: # timeout
                break
            if ticket == 0 and running == 0: # finished running
                break
            gevent.sleep(5)
        if timeout != 0:
            # tail_latencies.append('timeout')
            warm_start_latencies.append('timeout')
            clear_url = 'http://' + config.GATEWAY_ADDR + '/clear_container'
            data = {'workflow': workflow}
            requests.post(clear_url, json=data)
            gevent.sleep(5)
            continue

        warm_start_latencies.append(latencies[0])

        # tail_latency = analyze_workflow()
        # print(f'{workflow} tail latency: {tail_latency}')
        # tail_latencies.append(tail_latency)

        clear_url = 'http://' + config.GATEWAY_ADDR + '/clear_container'
        data = {'workflow': workflow}
        requests.post(clear_url, json=data)
        gevent.sleep(5)

    df = pd.DataFrame({'workflow': workflow_pool, 'cold_start': cold_start_latencies, 'warm_start': warm_start_latencies})
    df.to_csv(f'{datamode}_{BANDWIDTH}MB_cold_and_warm.csv')

if __name__ == '__main__':
    repo.clear_couchdb_results()
    repo.clear_couchdb_workflow_latency()
    opts, args = getopt.getopt(sys.argv[1:],'',['datamode='])
    for name, value in opts:
        if name == '--datamode':
            datamode = value
    analyze(datamode)
        