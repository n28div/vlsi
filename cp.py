from typing import Dict, Union, List, Tuple
from glob import glob
from minizinc import Instance, Model, Solver, Result, model
from utils.plot import plot_vlsi, plot_multi_vlsi
from natsort import natsorted
import sys, os
from datetime import timedelta
import csv
from utils.io import txt2dict, save_solution
import re

def enumerate_models() -> List[str]:
  """
  Enumerate implemented models.

  Returns: List[str]: List of implemented models, sorted by number
  """

  return [x for x in natsorted(glob("cp/*.mzn")) if "hbound" not in x]


def enumerate_instances() -> List[str]:
  """
  Enumerate input instances

  Returns: List[str]: List of available instances, sorted by number
  """
  return natsorted(glob("instances/*.txt"))


def report_result(data: Dict[str, Union[int, List[int]]], result: Result, show=False, plot_intermediate=False, **kwargs):
  """Reports to the user the result from a minizinc run

  Args: 
    data (Dict[str, Union[int, List[int]]]): Input data for the minizinc instance
    result (Result): Result object from minizinc instance
    **kwargs: Additional arguments passed to plot_vlsi function
  """
  stat = result.statistics

  time = stat["time"].total_seconds()
  nSolutions = stat["nSolutions"] if "nSolutions" in stat else 0
  # nodes and failures are not available if execution is stopped by timeout
  if "nodes" in stat and "failures" in stat:
    print("Instance solved")
    nodes = stat["nodes"]
    failures = stat["failures"]
  else:
    print("Instance not fully solved")
    nodes = -1
    failures = -1

  if len(result) > 0:
    max_y =  max(result.solution[-1].y)
    max_y_idx = result.solution[-1].y.index(max_y)
    height = max_y + data["cheight"][max_y_idx]
    print("Height: %d" % height)
    print("Took: %ss to find %d solutions" % (time, nSolutions))
    print("Nodes: %s - failures: %s" % (nodes, failures))

    if show:
      has_rotations = hasattr(result.solution[-1], "rotated")
      solution_x = result.solution[-1].x
      solution_y = result.solution[-1].y

      if has_rotations:
        rotated = result.solution[-1].rotated
      else:
        rotated = [False for _ in range(len(data["cwidth"]))]
    
      plot_vlsi(data["cwidth"], data["cheight"], solution_x, solution_y, rotations=rotated, show=show, **kwargs)
  else:
    print("No partial solutions available")

  return time, nSolutions, nodes, failures

if __name__ == "__main__":
  try:

    import argparse
    # define CLI arguments
    parser = argparse.ArgumentParser(description="Run minizinc vlsi solving method")
    parser.add_argument("--models", "-m", nargs="*", type=str,
                        required=True, help="Model(s) to use. Leave empty to use all.")
    parser.add_argument("--instances", "-i", nargs="*", type=str,
                        required=True, help="Instances(s) to load. Leave empty to use all.")
    parser.add_argument("--csv", "-csv", nargs=1, type=str, help="Save csv files in specified directory.")
    parser.add_argument("--output", "-o", nargs=1, type=str, help="Save results files in specified directory.")
    parser.add_argument("--plot", "-p", action="store_true", help="Plot final result. Defaults to false.")
    parser.add_argument("--solver", "-solver", "-s", nargs=1, type=str, default=["chuffed"], choices=["chuffed", "gecode"],
                        help="Solver that Minizinc will use. Defaults to Chuffed.")
    parser.add_argument("--free-search", "-f", action="store_true", help="Perform free search. Defaults to false.")
    parser.add_argument("--timeout", "-timeout", "-t", type=int, default=300,
                        help="Execution time contraint in seconds. Defaults to 300s (5m).")
                        
    # parse CLI arguments
    args = parser.parse_args()
    # use specified models or use all models if left empty
    models = args.models if len(args.models) > 0 else enumerate_models()
    # load specified instances or load all instances if left empty
    instances = args.instances if len(args.instances) > 0 else enumerate_instances()
    # TODO: Solver config
    solver = Solver.lookup(args.solver[0])

    # execute each model
    for m in models:
      if args.csv is not None:
        if not os.path.exists(args.csv[0]):
          os.mkdir(args.csv[0])

        f = open(os.path.join(args.csv[0], os.path.basename(m) + ".csv"), "w")
        csv_writer = csv.writer(f)
        csv_writer.writerow(["instance nr", "time", "solutions", "nodes", "failures"])

      if args.output is not None:
        if not os.path.exists(args.output[0]):
          os.mkdir(args.output[0])

      #counter for custom step
      for i in instances:
        instance_num = re.findall(r'(\d+)', i)[0]

        print("%s %s %s %s %s" % ("-" * 5, m, "-" * 3, i, "-" * 5))

        data = txt2dict(i)
        #create model new everytime so we can change parameter value
        mzn_model = Model(m)
        mzn_instance = Instance(solver, mzn_model)
        # set data variables on instance
        for k, v in data.items():
          mzn_instance[k] = v

        # run model
        result = mzn_instance.solve(intermediate_solutions=True, 
                                    timeout=timedelta(seconds=args.timeout),
                                    free_search=args.free_search,
                                    optimisation_level=1)

        #show report results
        res = report_result(data, result, title="%s | %s" % (m, i), show=args.plot)
        solved_time = res[0]
        solutions = res[1]
        nodes = res[2]
        failures = res[3]
        
        if args.csv is not None:
          csv_writer.writerow([instance_num, solved_time, solutions, nodes, failures])
        
        if args.output is not None and solutions > 0:
          path = os.path.join(args.output[0], f"ins-{instance_num}.txt")
          x = result.solution[-1].x
          y = result.solution[-1].y
          save_solution(path, data, list(zip(x, y)))
                  
      if args.csv is not None:
        f.close()
      

  except KeyboardInterrupt:
    f.close()

    print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
