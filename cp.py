from typing import Dict, Union, List
from glob import glob
from minizinc import Instance, Model, Solver, Result, model
from utils.plot import plot_vlsi, plot_multi_vlsi
from natsort import natsorted
import sys, os
import wandb
from datetime import timedelta
import csv

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

  max_y =  max(result.solution[-1].y)
  max_y_idx = result.solution[-1].y.index(max_y)
  height = max_y + data["cheight"][max_y_idx]
  print("Height: %d" % height)
  print("Took: %ss to find %d solutions" % (time, nSolutions))
  print("Nodes: %s - failures: %s" % (nodes, failures))

  if show:
    if plot_intermediate:
      solution_x = [r.x for r in result.solution]
      solution_y = [r.y for r in result.solution]
      plot_multi_vlsi(data["cwidth"], data["cheight"], solution_x, solution_y, show=show, **kwargs)
    else:    
      solution_x = result.solution[-1].x
      solution_y = result.solution[-1].y

      if hasattr(result.solution[-1], "rotated"):
        rotation = result.solution[-1].rotated
        cwidth = [ch if r else cw for r, cw, ch in zip(rotation, data["cwidth"], data["cheight"])]        
        cheight = [cw if r else ch for r, cw, ch in zip(rotation, data["cwidth"], data["cheight"])]        
      else:
          cwidth = data["cwidth"]
          cheight = data["cheight"]
      
      plot_vlsi(cwidth, cheight, solution_x, solution_y, show=show, **kwargs)

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
    parser.add_argument("--wandb", "-wandb", action="store_true", help="Log data using wandb.")
    parser.add_argument("--csv", "-csv", nargs=1, type=str, help="Save csv files in specified directory.")
    parser.add_argument("--plot", "-p", action="store_true", help="Plot final result. Defaults to false.")
    parser.add_argument("--plot-all", "-pall", action="store_true", help="Plot all results. Defaults to false.")
    parser.add_argument("--solver", "-solver", "-s", nargs=1, type=str, default="chuffed", choices=["chuffed", "gecode"],
                        help="Solver that Minizinc will use. Defaults to Chuffed.")
    parser.add_argument("--free-search", "-f", action="store_true", help="Perform free search (more efficient on search_parameters). Defaults to false.")
    parser.add_argument("--timeout", "-timeout", "-t", type=int, default=300,
                        help="Execution time contraint in seconds. Defaults to 300s (5m).")
                        
    # parse CLI arguments
    args = parser.parse_args()
    # use specified models or use all models if left empty
    models = args.models if len(args.models) > 0 else enumerate_models()
    # load specified instances or load all instances if left empty
    instances = args.instances if len(args.instances) > 0 else enumerate_instances()
    # TODO: Solver config
    solver = Solver.lookup(args.solver)

    # execute each model
    for m in models:
      if args.csv is not None:
        if not os.path.exists(args.csv[0]):
          os.mkdir(args.csv[0])

        f = open(os.path.join(args.csv[0], os.path.basename(m) + ".csv"), "w")
        csv_writer = csv.writer(f)
        csv_writer.writerow(["instance nr", "time", "solutions", "nodes", "failures"])

      if args.wandb:
        run = wandb.init(project='vlsi', entity='fatlads', tags=[m])
        run.name = m
        #custom x-axis
        wandb.define_metric("instance number")
        #set variables for which this metric holds
        wandb.define_metric("*", step_metric='instance number')
        config = wandb.config
      
      #counter for custom step
      instance_num = 1
      for i in instances:
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
                                    free_search=args.free_search)

        #show report results
        res = report_result(data, result, title="%s | %s" % (m, i), show=args.plot, plot_intermediate=args.plot_all)
        solved_time = res[0]
        solutions = res[1]
        nodes = res[2]
        failures = res[3]
        
        if args.wandb:
          #log results
          wandb.log({
            "time taken": solved_time,
            "solutions": solutions,
            "nodes": nodes,
            "failures": failures,
            "instance number": instance_num
          })

        if args.csv is not None:
          csv_writer.writerow([instance_num, solved_time, solutions, nodes, failures])

        instance_num += 1
      
      if args.wandb:
        #finish run with this model, select next model
        run.finish()
      if args.csv is not None:
        f.close()
      #reset counter for custom step
      instance_num = 1


  except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
