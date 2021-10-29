import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np

naive_model = pd.read_csv(r"csv/sat/NaiveModel.csv", header=0, index_col=0, sep=",")
naive_model = naive_model[["total_time"]]
naive_model[naive_model > 300] = 300
naive_model_rot = pd.read_csv(r"csv/sat/NaiveModelRot.csv", header=0, index_col=0, sep=",")
naive_model_rot = naive_model_rot[["total_time"]]
naive_model_rot[naive_model_rot > 300] = 300
symmetry_model = pd.read_csv(r"csv/sat/SymmetryModel.csv", header=0, index_col=0, sep=",")
symmetry_model = symmetry_model[["total_time"]]
symmetry_model[symmetry_model > 300] = 300
symmetry_model_rot = pd.read_csv(r"csv/sat/SymmetryModelRot.csv", header=0, index_col=0, sep=",")
symmetry_model_rot = symmetry_model_rot[["total_time"]]
symmetry_model_rot[symmetry_model_rot > 300] = 300

print(symmetry_model_rot)

nm = naive_model["total_time"].tolist()
nmrot = naive_model_rot["total_time"].tolist()
sm = symmetry_model["total_time"].tolist()
smrot = symmetry_model_rot["total_time"].tolist()
ins = range(1,41)
_ins = np.arange(len(ins))

plt.bar(ins, nm, label="Naive Model",)
plt.xlabel("instance number")
plt.ylabel("time (s)")
plt.legend()
plt.show()

plt.bar(ins, nmrot, label="Naive Model with rotations")
plt.xlabel("instance number")
plt.ylabel("time (s)")
plt.legend()
plt.show()

plt.bar(ins, sm, label="Symmetry Model")
plt.xlabel("instance number")
plt.ylabel("time (s)")
plt.legend()
plt.show()

plt.bar(ins, smrot, label="Symmetry Model with rotations")
plt.xlabel("instance number")
plt.ylabel("time (s)")
plt.legend()
plt.show()

combined = pd.DataFrame(np.c_[nm, nmrot], index=ins)
combined.columns = ["Naive Model", "Naive Model with Rotations"]
ax = combined.plot(kind="bar", width=0.75, legend=True)
ax.set_xlabel("instance number")
ax.set_ylabel("time (s)")
plt.show()

combined2 = pd.DataFrame(np.c_[sm, smrot], index=ins)
combined2.columns = ["Symmetry Model", "Symmetry Model with Rotations"]
ax2 = combined2.plot(kind="bar", width=0.75, legend=True)
ax2.set_xlabel("instance number")
ax2.set_ylabel("time (s)")
plt.show()

combined3 = pd.DataFrame(np.c_[nm, sm], index=ins)
combined3.columns = ["Naive Model", "Symmetry Model"]
ax = combined3.plot(kind="bar", width=0.75, legend=True)
ax.set_xlabel("instance number")
ax.set_ylabel("time (s)")
plt.show()

combined4 = pd.DataFrame(np.c_[nmrot, smrot], index=ins)
combined4.columns = ["Naive Model with Rotations", "Symmetry Model with Rotations"]
ax2 = combined4.plot(kind="bar", width=0.75, legend=True)
ax2.set_xlabel("instance number")
ax2.set_ylabel("time (s)")
plt.show()

