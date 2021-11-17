from sat import NaiveModel, SymmetryModel, MaybeSymmetryModel, NaiveModelRot, SymmetryModelRot
from typing import Dict, Union, List
from glob import glob
from utils.plot import plot_vlsi, plot_multi_vlsi
from utils.determine_hbound import  greedy_height
from natsort import natsorted
import sys, os
from datetime import timedelta
import csv
import time
import numpy as np
import argparse
from utils.io import txt2dict, save_solution
import re

def enumerate_models() -> List[str]:
  """
  Enumerate implemented models.

  Returns: List[str]: List of implemented models, sorted by number
  """
  return [NaiveModel, SymmetryModel, MaybeSymmetryModel, NaiveModelRot]


def enumerate_instances() -> List[str]:
  """
  Enumerate input instances

  Returns: List[str]: List of available instances, sorted by number
  """
  return natsorted(glob("instances/*.txt"))


if __name__ == "__main__":
  try:
    sys.setrecursionlimit(3000)
    
    # define CLI arguments
    parser = argparse.ArgumentParser(description="Run minizinc vlsi solving method")
    parser.add_argument("--models", "-m", nargs="*", type=str,
                        required=True, help="Model(s) to use. Leave empty to use all.")
    parser.add_argument("--instances", "-i", nargs="*", type=str,
                        required=True, help="Instances(s) to load. Leave empty to use all.")
    parser.add_argument("--csv", "-csv", nargs=1, type=str, help="Save csv files in specified directory.")
    parser.add_argument("--plot", "-p", action="store_true", help="Plot final result. Defaults to false.")
    parser.add_argument("--output", "-o", nargs=1, type=str, help="Save results files in specified directory.")
    parser.add_argument("--timeout", "-timeout", "-t", type=int, default=300,
                        help="Execution time contraint in seconds. Defaults to 300s (5m).")
                        
    # parse CLI arguments
    args = parser.parse_args()
    # use specified models or use all models if left empty
    models = args.models if len(args.models) > 0 else enumerate_models()
    models = [eval(m) for m in models]
    # load specified instances or load all instances if left empty
    instances = args.instances if len(args.instances) > 0 else enumerate_instances()
    
    # execute each model
    for model in models:
      if args.csv is not None:
        if not os.path.exists(args.csv[0]):
          os.mkdir(args.csv[0])

        f = open(os.path.join(args.csv[0], model.__name__ + ".csv"), "w")
        csv_writer = csv.writer(f)
        csv_writer.writerow(["instance nr", "total_time", "build_time", "x", "y"])
      
      if args.output is not None:
        if not os.path.exists(args.output[0]):
          os.mkdir(args.output[0])

      for i in instances:
        instance_num = re.findall(r'(\d+)', i)[0]
        print("%s %s %s %s %s" % ("-" * 5, model, "-" * 3, i, "-" * 5))

        best_x = []
        best_y = []
        best_h = None
        data = txt2dict(i)

        # sort height and width by height
        sheight = sorted(data["cheight"], reverse=True)
        swidth = [i for _, i in sorted(zip(data["cheight"], data["cwidth"]), reverse=True)]

        upper_bound = greedy_height(data["N"], data["WIDTH"], swidth, sheight)
        lower_bound = int(sum([h * w for h, w in zip(sheight, swidth)]) / data["WIDTH"])
        print(f"Searching height in [{lower_bound}, {upper_bound}]")

        #create model new everytime so we can change parameter value
        solver = model(data["WIDTH"], data["cwidth"], data["cheight"], lower_bound, upper_bound, timeout=args.timeout)
        print(f"Built encoding and constraints in: {solver.time['init']:04f}s")

        start_t = time.perf_counter()
        for h in range(upper_bound, lower_bound - 1, -1):
          # run model
          solver.solve(height=h)
          print(f"{'SAT' if solver.solved else 'UNSAT'}\tHeight = {h:3} [solving: {solver.time['solve']:04f}s setup: {solver.time['setup']:04f}s]")
            
          if solver.solved and solver.remaining_time > 0:
            best_h = h
            best_x = solver.x
            best_y = solver.y
          else:
            break

        end_t = time.perf_counter()

        if best_h is not None:
          rotations = solver.rotations if solver.ROTATIONS else None
          solved_time = end_t - start_t

          print(f"Solved with h={best_h} in {solved_time:04f} seconds")
          plot_vlsi(data["cwidth"], data["cheight"], best_x, best_y, show=args.plot, rotations=rotations)
        
          if args.csv is not None:
            csv_writer.writerow([i, solved_time, solver.time["init"], best_x, best_y])
          
        if args.output is not None and best_h is not None:
          path = os.path.join(args.output[0], f"ins-{instance_num}.txt")
          x = best_x
          y = best_y
          save_solution(path, data, list(zip(x, y)))
          
      if args.csv is not None:
        f.close()
  except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)