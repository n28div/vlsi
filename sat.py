from z3.z3 import Select
from sat import NaiveModel
from typing import Dict, Union, List
from glob import glob
from utils.plot import plot_vlsi, plot_multi_vlsi
from utils.determine_hbound import  greedy_height
from natsort import natsorted
import sys, os
import wandb
from datetime import timedelta
import csv
import time
import numpy as np



def enumerate_models() -> List[str]:
  """
  Enumerate implemented models.

  Returns: List[str]: List of implemented models, sorted by number
  """
  return natsorted(glob("cp/*.mzn"))


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


#def report_result(data: Dict[str, Union[int, List[int]]], result: Result, show=False, plot_intermediate=False, **kwargs):
#  """Reports to the user the result from a minizinc run
#
#  Args: 
#    data (Dict[str, Union[int, List[int]]]): Input data for the minizinc instance
#    result (Result): Result object from minizinc instance
#    **kwargs: Additional arguments passed to plot_vlsi function
#  """
#  stat = result.statistics
#
#  time = stat["time"].total_seconds()
#  nSolutions = stat["nSolutions"] if "nSolutions" in stat else 0
#  # nodes and failures are not available if execution is stopped by timeout
#  if "nodes" in stat and "failures" in stat:
#    print("Instance solved")
#    nodes = stat["nodes"]
#    failures = stat["failures"]
#  else:
#    print("Instance not fully solved")
#    nodes = -1
#    failures = -1
#
#  max_y =  max(result.solution[-1].y)
#  max_y_idx = result.solution[-1].y.index(max_y)
#  height = max_y + data["cheight"][max_y_idx]
#  print("Height: %d" % height)
#  print("Took: %ss to find %d solutions" % (time, nSolutions))
#  print("Nodes: %s - failures: %s" % (nodes, failures))
#
#  if show:
#    if plot_intermediate:
#      solution_x = [r.x for r in result.solution]
#      solution_y = [r.y for r in result.solution]
#      plot_multi_vlsi(data["cwidth"], data["cheight"], solution_x, solution_y, show=show, **kwargs)
#    else:    
#      solution_x = result.solution[-1].x
#      solution_y = result.solution[-1].y
#
#      if hasattr(result.solution[-1], "rotated"):
#        rotation = result.solution[-1].rotated
#        cwidth = [ch if r else cw for r, cw, ch in zip(rotation, data["cwidth"], data["cheight"])]        
#        cheight = [cw if r else ch for r, cw, ch in zip(rotation, data["cwidth"], data["cheight"])]        
#      else:
#        cwidth = data["cwidth"]
#        cheight = data["cheight"]
#    
#      plot_vlsi(cwidth, cheight, solution_x, solution_y, show=show, **kwargs)
#
#  return time, nSolutions, nodes, failures


if __name__ == "__main__":
  try:

    import argparse
    # define CLI arguments
    parser = argparse.ArgumentParser(description="Run minizinc vlsi solving method")
    #parser.add_argument("--models", "-m", nargs="*", type=str,
    #                    required=True, help="Model(s) to use. Leave empty to use all.")
    parser.add_argument("--instances", "-i", nargs="*", type=str,
                        required=True, help="Instances(s) to load. Leave empty to use all.")
    #parser.add_argument("--wandb", "-wandb", action="store_true", help="Log data using wandb.")
    #parser.add_argument("--csv", "-csv", nargs=1, type=str, help="Save csv files in specified directory.")
    #parser.add_argument("--plot", "-p", action="store_true", help="Plot final result. Defaults to false.")
    #parser.add_argument("--plot-all", "-pall", action="store_true", help="Plot all results. Defaults to false.")
    #parser.add_argument("--timeout", "-timeout", "-t", type=int, default=300,
    #                    help="Execution time contraint in seconds. Defaults to 300s (5m).")
                        
    # parse CLI arguments
    args = parser.parse_args()
    # use specified models or use all models if left empty
    #models = args.models if len(args.models) > 0 else enumerate_models()
    models = [NaiveModel]
    # load specified instances or load all instances if left empty
    instances = args.instances if len(args.instances) > 0 else enumerate_instances()
    
    # execute each model
    for model in models:
      #if args.csv is not None:
      #  if not os.path.exists(args.csv[0]):
      #    os.mkdir(args.csv[0])

      #  f = open(os.path.join(args.csv[0], os.path.basename(m) + ".csv"), "w")
      #  csv_writer = csv.writer(f)
      #  csv_writer.writerow(["instance nr", "time", "solutions", "nodes", "failures"])

      #if args.wandb:
      #  run = wandb.init(project='vlsi', entity='fatlads', tags=[m])
      #  run.name = m
      #  #custom x-axis
      #  wandb.define_metric("instance number")
      #  #set variables for which this metric holds
      #  wandb.define_metric("*", step_metric='instance number')
      #  config = wandb.config
      
      #counter for custom step
      instance_num = 1
      for i in instances:
        print("%s %s %s %s %s" % ("-" * 5, model, "-" * 3, i, "-" * 5))

        best_x = []
        best_y = []
        solving = True
        data = txt2dict(i)

        h_array = np.array(data["cheight"])
        w_array = np.array(data["cwidth"])
        idx = np.argsort(h_array)

        h_array = np.array(h_array)[idx]
        w_array = np.array(w_array)[idx]
        lower_bound = int(np.dot(h_array,w_array)/data["WIDTH"])
        h_sorted = h_array.tolist()
        w_sorted = w_array.tolist()


        w_sorted.reverse()
        h_sorted.reverse()
        upper_bound = greedy_height(data["N"], data["WIDTH"], w_sorted, h_sorted, 0 , 0 , 0, 1)
        solving_start = time.perf_counter()

        for h in range(upper_bound, lower_bound-1, -1):
          #create model new everytime so we can change parameter value
          solver = model(data["WIDTH"], data["cwidth"], data["cheight"])
          # run model
          solver.solve(height=h)
          if solver.solved:
            best_x = solver.x
            best_y = solver.y
          else:
            break

        solving_end = time.perf_counter()
        print(f"Solving took {solving_end - solving_start:04f} seconds")
        plot_vlsi(data["cwidth"], data["cheight"], best_x, best_y, show=True)
        #print(solver.positions)
        #pprint([[solver.model.evaluate(solver.board[i][j]) for j in range(solver.WIDTH)] for i in range(solver.HEIGHT)])

        #print(solver.positions)
        #print(solver.solver.statistics())
        import pprint
        for c in range(solver.N):
          print("Circuit ", c)
          #pprint([[solver.model.evaluate(solver.iboard[c][i][j]) for j in range(solver.WIDTH)] for i in range(solver.HEIGHT)])
          #pprint.pprint([[solver.solver.model().evaluate(solver.cboard[c][i][j]) for j in range(solver.WIDTH)] for i in range(solver.HEIGHT)])
          #pprint.pprint([solver.solver.model().evaluate(solver.cy[c][i]) for i in range(solver.HEIGHT)])
          #pprint.pprint([solver.solver.model().evaluate(solver.cx[c][j]) for j in range(solver.WIDTH)])
          #print(solver.result.evaluate(solver.board))

        #show report results
        #res = report_result(data, result, title="%s | %s" % (m, i), show=args.plot, plot_intermediate=args.plot_all)
        #solved_time = res[0]
        #solutions = res[1]
        #nodes = res[2]
        #failures = res[3]
        #
        #if args.wandb:
        #  #log results
        #  wandb.log({
        #    "time taken": solved_time,
        #    "solutions": solutions,
        #    "nodes": nodes,
        #    "failures": failures,
        #    "instance number": instance_num
        #  })
        #
        #if args.csv is not None:
        #  csv_writer.writerow([instance_num, solved_time, solutions, nodes, failures])
        #
        #instance_num += 1
      
      #if args.wandb:
      #  #finish run with this model, select next model
      #  run.finish()
      #if args.csv is not None:
      #  f.close()
      #reset counter for custom step
      instance_num = 1


  except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)