import time
import string
import random
import compute_pi

def main():
    input_res = store.fetch(store.input.keys())
    for k in input_res.keys():
        print(k)
    output_res = {}
    for (k, v) in store.output.items():
        result = 'a' * v['size']
        output_res[k] = result
    # factor = 1000/3
    # factor = 300
    factor = 400
    cpu_work = int(factor * store.runtime)
    cost = compute_pi.compute_terrible_pi(cpu_work)

    # time.sleep(store.runtime)
    store.put(output_res, {})
