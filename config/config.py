COUCHDB_URL = 'http://openwhisk:openwhisk@192.168.3.100:5984/'
REDIS_HOST = '127.0.0.1' # it serves to connect with the local redis, so it should be 127.0.0.1
REDIS_PORT = 6379 # it follows the same configuration as created redis by docker (e.g., -p 6379:6379)
REDIS_DB = 0
GATEWAY_ADDR = '192.168.3.100:7000' # need to update as your private_ip
MASTER_HOST = '192.168.3.100:8000' # need to update as your private_ip
WORKFLOW_YAML_ADDR = {'fileprocessing': '/home/yujiazhao/FaaSFlow/benchmark/fileprocessing/flat_workflow.yaml',
                  'illgal_recognizer': '/home/yujiazhao/FaaSFlow/benchmark/illgal_recognizer/flat_workflow.yaml',
                  'video': '/home/yujiazhao/FaaSFlow/benchmark/video/flat_workflow.yaml',
                  'wordcount': '/home/yujiazhao/FaaSFlow/benchmark/wordcount/flat_workflow.yaml',
                  'cycles': '/home/yujiazhao/FaaSFlow/benchmark/generator/cycles/flat_workflow_runtime.yaml',
                  'epigenomics': '/home/yujiazhao/FaaSFlow/benchmark/generator/epigenomics/flat_workflow_runtime.yaml',
                  'genome': '/home/yujiazhao/FaaSFlow/benchmark/generator/genome/flat_workflow_runtime.yaml',
                  'soykb': '/home/yujiazhao/FaaSFlow/benchmark/generator/soykb/flat_workflow_runtime.yaml',
                  'montage': '/home/yujiazhao/FaaSFlow/benchmark/generator/montage/flat_workflow_runtime.yaml',
                  'srasearch': '/home/yujiazhao/FaaSFlow/benchmark/generator/srasearch/flat_workflow_runtime.yaml',
                  'seismology': '/home/yujiazhao/FaaSFlow/benchmark/generator/seismology/flat_workflow_runtime.yaml', 
                  'blast': '/home/yujiazhao/FaaSFlow/benchmark/generator/blast/flat_workflow_runtime.yaml', 
                  'bwa': '/home/yujiazhao/FaaSFlow/benchmark/generator/bwa/flat_workflow_runtime.yaml'}
# NETWORK_BANDWIDTH = 128 * 1024 * 1024 / 4 # 128MB/s / 4 when it's unlimited
NETWORK_BANDWIDTH = 50 * 1024 * 1024 / 4 # 50MB/s / 4
NET_MEM_BANDWIDTH_RATIO = 15 # mem_time = net_time / 15
CONTAINER_MEM = 256 * 1024 * 1024 # 256MB
NODE_MEM = 256 * 1024 * 1024 * 1024 # 256G
RESERVED_MEM_PERCENTAGE = 0.2
GROUP_LIMIT = 100
RPMs = {'genome-25': [2, 4, 6, 8], 'genome-50': [2, 4, 6, 8, 10], 'genome-75': [2, 4, 6, 8, 10], 'genome-100': [2, 4, 6, 8, 10],
'video-25': [4, 8, 16, 24], 'video-50': [8, 16, 24, 32, 40], 'video-75': [8, 16, 24, 32, 40], 'video-100': [8, 16, 24, 32, 40]}
FUNCTION_INFO_ADDRS = {'genome': '../../benchmark/generator/genome', 'epigenomics': '../../benchmark/generator/epigenomics',
                                                'soykb': '../../benchmark/generator/soykb', 'cycles': '../../benchmark/generator/cycles',
                                                'montage': '../../benchmark/generator/montage',
                                                'srasearch': '../../benchmark/generator/srasearch', 'seismology': '../../benchmark/generator/seismology',
                                                'blast': '../../benchmark/generator/blast', 'bwa': '../../benchmark/generator/bwa',
                                                'fileprocessing': '../../benchmark/fileprocessing', 'wordcount': '../../benchmark/wordcount',
                                                'illgal_recognizer': '../../benchmark/illgal_recognizer', 'video': '../../benchmark/video'}
DATA_MODE = 'optimized' # raw, optimized
CONTROL_MODE = 'WorkerSP' # WorkerSP, MasterSP
CLEAR_DB_AND_MEM = True
