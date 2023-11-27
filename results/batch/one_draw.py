import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

fig = plt.figure()

x = np.arange(8)
bar_width = 0.25
tick_label = ["Cyc","Epi","Gen","Soy","Vid","IR","FP","WC"]

dir = "6rpm_50MB"

faasflow_df = pd.read_csv(dir + "/" + 'FaaSFlow_avg.csv')
random_df = pd.read_csv(dir + "/" + 'Random_avg.csv')
palette_df = pd.read_csv(dir + "/" + 'Palette_avg.csv')

# draw avg latency
ax1 = fig.add_subplot(1, 1, 1)

y_1 = list(faasflow_df['median_latency'])
y_2 = list(random_df['median_latency'])
y_3 = list(palette_df['median_latency'])

t_1 = list(faasflow_df['tail_latency'])
t_2 = list(random_df['tail_latency'])
t_3 = list(palette_df['tail_latency'])

y1_err = [t_1[i] - y_1[i] for i in range(len(y_1))]
y2_err = [t_2[i] - y_2[i] for i in range(len(y_2))]
y3_err = [t_3[i] - y_3[i] for i in range(len(y_3))]

y1_error = [np.zeros_like(y1_err)+0.5, y1_err]
y2_error = [np.zeros_like(y2_err)+0.5, y2_err]
y3_error = [np.zeros_like(y3_err)+0.5, y3_err]

ax1.set_ylim(0,20)
ax1.set_title("median and 99%-ile latency")
#FFFED5#76180E#F7903D#59A95A#4D85BD
ax1.bar(x-bar_width, y_1, bar_width, color="#FFFED5", align="center", yerr=y1_error, zorder=2, capsize=4, error_kw=dict(capsize = 4, capthick=1, zorder=1), label="FaaSFlow", edgecolor='black', linewidth=1)
ax1.bar(x, y_3, bar_width, color="#F7903D", align="center", yerr=y3_error, zorder=2, capsize=4, error_kw=dict(capsize = 4, capthick=1, zorder=1), label="Palette", edgecolor='black',linewidth=1)
ax1.bar(x+bar_width, y_2, bar_width, color="#4D85BD", align="center", yerr=y2_error, zorder=2, capsize=4, error_kw=dict(capsize = 4, capthick=1, zorder=1), label="Random", edgecolor='black', linewidth=1)
ax1.set_xticklabels(tick_label)
ax1.set_ylabel('Latency (s)')
ax1.legend()
plt.xticks(x, tick_label,rotation=0)

plt.suptitle("batch_" + dir)
fig.savefig("3compare.pdf")