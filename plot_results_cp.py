import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np

search_parameter = pd.read_csv(r"csv/cp/search_parameter.csv", header=0, index_col=0)
search_parameter = search_parameter[["time"]]
stuckey_way = pd.read_csv(r"csv/cp/stuckey_way.csv", header=0, index_col=0)
stuckey_way = stuckey_way[["time"]]
rotations = pd.read_csv(r"csv/cp/rotations.csv", header=0, index_col=0)
rotations = rotations[["time"]]
print(rotations)

sp = search_parameter["time"].tolist()
sw = stuckey_way["time"].tolist()
rot = rotations["time"].tolist()
ins = range(1,41)
_ins = np.arange(len(ins))

plt.bar(ins, sp, label="search_parameter",)
plt.xlabel("instance number")
plt.ylabel("time (s)")
plt.legend()
plt.show()

plt.bar(ins, sw, label="stuckey_way")
plt.xlabel("instance number")
plt.ylabel("time (s)")
plt.legend()
plt.show()

plt.bar(ins, rot, label="rotations")
plt.xlabel("instance number")
plt.ylabel("time (s)")
plt.legend()
plt.show()

combined = pd.DataFrame(np.c_[sp, sw], index=ins)
combined.columns = ["search_parameter", "stuckey_way"]
ax = combined.plot(kind="bar", width=0.75, legend=True)
ax.set_xlabel("instance number")
ax.set_ylabel("time (s)")
plt.show()

combined2 = pd.DataFrame(np.c_[sp, rot], index=ins)
combined2.columns = ["search_parameter", "rotations"]
ax2 = combined2.plot(kind="bar", width=0.75, legend=True)
ax2.set_xlabel("instance number")
ax2.set_ylabel("time (s)")
plt.show()


combined3 = pd.DataFrame(np.c_[sp, sw, rot], index=ins)
combined3.columns = ["search_parameter", "stuckey_way", "rotations"]
ax3 = combined3.plot(kind="bar", width=0.75, legend=True)
ax3.set_xlabel("instance number")
ax3.set_ylabel("time (s)")
plt.show()
