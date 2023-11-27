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
TEST_PER_WORKFLOW = 3 * 60

def run_workflow(workflow_name, request_id, spawn_rate, parse_mode):
    print('----firing workflow----', request_id)
    global latencies, ticket, running, timeout
    ticket = ticket - 1
    running = running + 1
    if ticket > 0 and timeout < 3:
        gevent.spawn_later(spawn_rate, run_workflow, workflow_name, str(uuid.uuid4()), spawn_rate, parse_mode)
    url = 'http://' + config.GATEWAY_ADDR + '/run'
    data = {'workflow':workflow_name, 'request_id': request_id, 'parse_mode': parse_mode}
    try:
        rep = requests.post(url, json=data, timeout=600)
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
    if len(latencies) % 2 == 1:
        mid = int((len(latencies) - 1) / 2)
    else:
        mid = int(len(latencies) / 2) - 1
    if len(latencies) < 100:
        return latencies[-1], latencies[mid], latencies[0]
    else:
        tail = int(len(latencies) / 100)
        return latencies[-tail], latencies[mid], latencies[0]

def analyze(datamode):
    global RPM, BANDWIDTH, ticket, running, timeout, latencies
    # workflow_pool = ['cycles', 'epigenomics', 'genome', 'soykb', 'video', 'illgal_recognizer', 'fileprocessing', 'wordcount']
    workflow_pool = ['genome']
    # parse_mode = ['Random', 'Robin', 'Palette+CH', 'Palette+LAC', 'Palette+LAF' ,'FaaSFlow']
    parse_mode = 'Random'

    all_latencies = {}
    tail_latencies = []
    avg_latencies = []
    median_latencies = []
    min_latencies = []
    for workflow in workflow_pool:
        print(f'----analyzing {workflow}, using mode {parse_mode}, prewarming----')

        # prewarm to achieve stable throughput
        ticket = 3
        running = 0
        timeout = 0
        # start a new test after 5 seconds, so that a new container will be created
        gevent.spawn(run_workflow, workflow, str(uuid.uuid4()), 5, parse_mode)
        gevent.sleep(5)

        while True:
            if running == 0 and timeout != 0: # timeout
                break
            if ticket == 0 and running == 0: # finished running
                break
            gevent.sleep(5)
        if timeout == 3:    
            tail_latencies.append('timeout')
            clear_url = 'http://' + config.GATEWAY_ADDR + '/clear_container'
            data = {'workflow': workflow}
            requests.post(clear_url, json=data)
            gevent.sleep(5)
            continue


        gevent.sleep(10)

        print(f'----prewarming done, now start analyzing----')
        # avg and tail latency analysis
        ticket = RPM * TEST_PER_WORKFLOW / 60
        running = 0
        timeout = 0
        latencies = []
        gevent.spawn(run_workflow, workflow, str(uuid.uuid4()), 60 / RPM, parse_mode)
        gevent.sleep(5)
        while True:
            if running == 0 and timeout != 0: # timeout
                break
            if ticket == 0 and running == 0: # finished running
                break
            gevent.sleep(5)
        if timeout != 0:
            tail_latencies.append('timeout')
            clear_url = 'http://' + config.GATEWAY_ADDR + '/clear_container'
            data = {'workflow': workflow}
            requests.post(clear_url, json=data)
            gevent.sleep(5)
            continue

        all_latencies[workflow] = latencies

        tail_latency, mid_latency, min_latency = analyze_workflow()
        
        tail_latencies.append(tail_latency)

        avg_latency = sum(latencies) / len(latencies)
        avg_latencies.append(avg_latency)

        median_latencies.append(mid_latency)
        min_latencies.append(min_latency)

        print(f'{workflow} min latency: {min_latency}')
        print(f'{workflow} median latency: {mid_latency}')
        print(f'{workflow} avg latency: {avg_latency}')
        print(f'{workflow} tail latency: {tail_latency}')

        clear_url = 'http://' + config.GATEWAY_ADDR + '/clear_container'
        data = {'workflow': workflow}
        requests.post(clear_url, json=data)
        gevent.sleep(5)
    
    df = pd.DataFrame({'workflow': workflow_pool, 'min_latency': min_latencies, 'median_latency': median_latencies, 'avg_latency': avg_latencies, 'tail_latency': tail_latencies})
    # df.to_csv(f'{datamode}_{RPM}rpm_{BANDWIDTH}MB_avg_tail.csv')
    df.to_csv(parse_mode + '.csv')

    df2 = pd.read_csv(parse_mode + '_raw_all.csv')
    # df2 = pd.DataFrame()
    for workflow in workflow_pool:
        if workflow in df2.columns:
            df2[workflow] = all_latencies[workflow]
        else:
            df2.insert(df2.shape[1], workflow, all_latencies[workflow])
    df2.to_csv(parse_mode + '_raw_all.csv')


if __name__ == '__main__':
    repo.clear_couchdb_results()
    repo.clear_couchdb_workflow_latency()
    opts, args = getopt.getopt(sys.argv[1:],'',['datamode='])
    for name, value in opts:
        if name == '--datamode':
            datamode = value
    analyze(datamode)
        