import glob
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
plt.style.use('seaborn')
from sys import argv

experiments = {
    #"colab_csv/naive_model.mzn.csv": ("Naive model", "tab:blue"),
    #"colab_csv/naive_boundaries.mzn.csv": ("Naive boundaries model", "tab:orange"),
    #"colab_csv/smart_boundaries.mzn.csv": ("Smart boundaries model", "tab:green"),
    #"colab_csv/implicit_2.mzn.csv": ("Implicit constraints", "tab:red"),
    #"colab_csv/geometric_symmetry.mzn.csv": ("Geometrical symmetry breaking", "tab:purple"),
    #"colab_csv/value_symmetry.mzn.csv": ("Value symmetry breaking", "tab:brown"),
    #"colab_csv/search_parameter.mzn.csv": ("Search annotations", "tab:pink"),
    #"colab_csv/stuckey_way.mzn.csv": ("Cumulative constraints", "tab:olive"),
}

fig, ax = plt.subplots(figsize=(15, 6))
max_val = -np.inf
min_val = np.inf

for filename, (title, color) in experiments.items():
    data = np.loadtxt(filename, skiprows=1, delimiter=",")
    data[data[:, 3] < 0, 1] = 300
    data[data < 0] = np.NaN
    
    x = list(range(data.shape[0]))
    y = data[:, 1]

    ax.plot(x, y, "o", label=title, color=color)
    ax.stem(x, y, markerfmt=" ", linefmt="grey")
    ax.set_xlabel("Instance")
    ax.set_xticks(range(y.shape[0]))
    ax.set_xticklabels(range(1, y.shape[0] + 1), rotation=90)
    ax.set_ylabel("Time taken (s)")
    ax.set_yscale("log")
    ax.minorticks_off()
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower left", ncol=2)

    if np.nanmax(y) > max_val:
        max_val = np.nanmax(y)
    if np.nanmin(y) < min_val:
        min_val = np.nanmin(y)    

ticks = np.geomspace(min_val, max_val, num=15)
ax.set_yticks(ticks)

if len(argv) > 1:
    plt.savefig(argv[1])
else:
    plt.show()