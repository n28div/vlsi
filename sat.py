from sat import NaiveModel, SymmetryModel, MaybeSymmetryModel
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


def enumerate_models() -> List[str]:
  """
  Enumerate implemented models.

  Returns: List[str]: List of implemented models, sorted by number
  """
  return [NaiveModel, SymmetryModel]


def enumerate_instances() -> List[str]:
  """
  Enumerate input instances

  Returns: List[str]: List of available instances, sorted by number
  """
  return natsorted(glob("instances/*.txt"))


def txt2dict(path: str) -> Dict[str, Union[int, List[int]]]:
  """Converts txt input file to dict.
  
  Args: path (str): Input file
  Returns: Dict[str, Union[int, List[int]]]: Key is the variable, value is the variable's value
  """
  d = dict()

  with open(path) as txt:
    content = txt.readlines()

    # 1st line - board width
    d["WIDTH"] = int(content[0].strip())
    # 2nd line - number of circuits
    d["N"] = int(content[1].strip())

    # following line contains width and height of each circuit separated by a space
    cdim = content[2:]
    d["cwidth"] = list(map(lambda d: int(d.split(" ")[0]), cdim))
    d["cheight"] = list(map(lambda d: int(d.split(" ")[1]), cdim))

  return d


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
      
      for i in instances:
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
          solved_time = end_t - start_t

          print(f"Solved with h={best_h} in {solved_time:04f} seconds")
          plot_vlsi(data["cwidth"], data["cheight"], best_x, best_y, show=args.plot)
        
          if args.csv is not None:
            csv_writer.writerow([i, solved_time, solver.time["init"], best_x, best_y])
          
      if args.csv is not None:
        f.close()
      

  except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
