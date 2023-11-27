from typing import Any, List
import couchdb
import redis
import json
import sys

sys.path.append('../../config')
import config

couchdb_url = config.COUCHDB_URL

class Repository:
    def __init__(self):
        self.redis = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
        self.couch = couchdb.Server(couchdb_url)

    # get all function_name for every node seems to solve the problem of KeyError Exception in manager.py, line 103
    def get_current_node_functions(self, ip: str, mode: str) -> List[str]:
        db = self.couch[mode]
        functions = []
        for item in db:
            functions.append(db[item]['function_name'])
        return functions

    def get_foreach_functions(self, db_name) -> List[str]:
        db = self.couch[db_name]
        for item in db:
            doc = db[item]
            if 'foreach_functions' in doc:
                return doc['foreach_functions']

    def get_merge_functions(self, db_name) -> List[str]:
        db = self.couch[db_name]
        for item in db:
            doc = db[item]
            if 'merge_functions' in doc:
                return doc['merge_functions']

    def get_start_functions(self, db_name) -> List[str]:
        db = self.couch[db_name]
        for item in db:
            doc = db[item]
            if 'start_functions' in doc:
                return doc['start_functions']

    def get_all_addrs(self, db_name) -> List[str]:
        db = self.couch[db_name]
        for item in db:
            doc = db[item]
            if 'addrs' in doc:
                return doc['addrs']

    def get_function_info(self, function_name: str, mode: str) -> Any:
        db = self.couch[mode]
        for item in db.find({'selector': {'function_name': function_name}}):
            return item
        
    # get function ip and to info per request
    def get_function_ip_to(self, request_id: str) -> Any:
        key = request_id + '_schedule.json'
        func_ip_to_dict = json.loads(self.redis[key].decode())
        return func_ip_to_dict
    
    # get function ip and to info per request for specific function
    def get_function_ip_to_specific(self, request_id: str, function_name: str) -> Any:
        key = request_id + '_schedule.json'
        func_ip_to_dict = json.loads(self.redis[key].decode())
        return func_ip_to_dict[function_name]

    def create_request_doc(self, request_id: str) -> None:
        if request_id in self.couch['results']:
            doc = self.couch['results'][request_id]
            self.couch['results'].delete(doc)
        self.couch['results'][request_id] = {}

    def get_keys(self, request_id: str) -> Any:
        keys = dict()
        doc = self.couch['results'][request_id]
        for k in doc:
            if k != '_id' and k != '_rev' and k != '_attachments':
                keys[k] = doc[k]
        return keys

    # fetch result from couchdb/redis
    def fetch_from_mem(self, redis_key, content_type):
        if content_type == 'application/json':
            redis_value = self.redis[redis_key].decode()
            return json.loads(redis_value)
        else:
            return self.redis[redis_key]

    def fetch_from_db(self, request_id, key):
        db = self.couch['results']
        f = db.get_attachment(request_id, filename=key, default='no attachment')
        if f != 'no attachment':
            return f.read()
        else:
            filename = key + '.json'
            f = db.get_attachment(request_id, filename=filename, default='no attachment')
            return json.load(f)

    def fetch(self, request_id, key):
        print('fetching...', key)
        redis_key_1 = request_id + '_' + key
        redis_key_2 = request_id + '_' + key + '.json'
        value = None
        if redis_key_1 in self.redis:
            value = self.fetch_from_mem(redis_key_1, 'bytes')
        elif redis_key_2 in self.redis:
            value = self.fetch_from_mem(redis_key_2, 'application/json')
        else:  # if not
            value = self.fetch_from_db(request_id, key)
        print('fetched value: ', value)
        return value
    
    def clear_mem(self, request_id):
        keys = self.redis.keys()
        for key in keys:
            key_str = key.decode()
            if key_str.startswith(request_id):
                self.redis.delete(key)

    def clear_db(self, request_id):
        db = self.couch['results']
        db.delete(db[request_id])

    def log_status(self, workflow_name, request_id, status):
        log_db = self.couch['log']
        log_db.save({'request_id': request_id, 'workflow': workflow_name, 'status': status})
    
    def save_latency(self, log):
        latency_db = self.couch['workflow_latency']
        latency_db.save(log)