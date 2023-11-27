import numpy as np
import pandas as pd

# workflow_pool = ['cycles', 'epigenomics', 'genome', 'soykb', 'video', 'illgal_recognizer', 'fileprocessing', 'wordcount']
workflow_pool = ['cycles', 'epigenomics', 'genome', 'soykb']

mode = "FaaSFlow"

files_count = 3
df_list = []

for i in range(files_count):
    df = pd.read_csv(mode + str(i+1)  + '.csv')
    df_list.append(df)

avg_list = []
tail_list = []

for i in range(len(df_list)):
    avg_list.append(list(df_list[i]['avg_latency']))
    tail_list.append(list(df_list[i]['tail_latency']))

avg_avg = []
avg_tail = []

for i in range(len(workflow_pool)):
    sum_avg = 0
    sum_tail = 0
    for j in range(len(avg_list)):
        sum_avg += avg_list[j][i]
        sum_tail += tail_list[j][i]
    avg_avg.append(sum_avg / len(avg_list))
    avg_tail.append(sum_tail / len(avg_list))
    
print(avg_avg)
print(avg_tail)

df = pd.DataFrame({'workflow': workflow_pool, 'avg_latency': avg_avg, 'tail_latency': avg_tail})
df.to_csv(f'{mode}_avg.csv')