import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np

naive_model = pd.read_csv(r"csv/sat/NaiveModel.csv", header=0, index_col=0)
naive_model = naive_model[["time"]]
naive_model_rot = pd.read_csv(r"csv/sat/NaiveModelRot.csv", header=0, index_col=0)
naive_model_rot = naive_model_rot[["time"]]
symmetry_model = pd.read_csv(r"csv/sat/SymmetryModel.csv", header=0, index_col=0)
symmetry_model = symmetry_model[["time"]]
symmetry_model_rot = pd.read_csv(r"csv/sat/SymmetryModelRot.csv", header=0, index_col=0)
symmetry_model_rot = symmetry_model_rot[["time"]]

print(symmetry_model_rot)

nm = naive_model["time"].tolist()
nmrot = naive_model_rot["time"].tolist()
sm = symmetry_model["time"].tolist()
smrot = symmetry_model_rot["time"].tolist()
ins = range(1,41)
_ins = np.arange(len(ins))

plt.bar(ins, nm, label="search_parameter",)
plt.xlabel("instance number")
plt.ylabel("time (s)")
plt.legend()
plt.show()

plt.bar(ins, nmrot, label="stuckey_way")
plt.xlabel("instance number")
plt.ylabel("time (s)")
plt.legend()
plt.show()

plt.bar(ins, sm, label="rotations")
plt.xlabel("instance number")
plt.ylabel("time (s)")
plt.legend()
plt.show()

plt.bar(ins, smrot, label="rotations")
plt.xlabel("instance number")
plt.ylabel("time (s)")
plt.legend()
plt.show()

combined = pd.DataFrame(np.c_[nm, nmrot], index=ins)
combined.columns = ["search_parameter", "stuckey_way"]
ax = combined.plot(kind="bar", width=0.75, legend=True)
ax.set_xlabel("instance number")
ax.set_ylabel("time (s)")
plt.show()

combined2 = pd.DataFrame(np.c_[sm, smrot], index=ins)
combined2.columns = ["search_parameter", "rotations"]
ax2 = combined2.plot(kind="bar", width=0.75, legend=True)
ax2.set_xlabel("instance number")
ax2.set_ylabel("time (s)")
plt.show()

