from typing import Dict, Union, List
from glob import glob
from minizinc import Instance, Model, Solver, Result
from utils.plot import plot_vlsi, plot_multi_vlsi
from natsort import natsorted
import sys, os
import wandb

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


def determine_hbound(n: int, cwidth: List[int], cheight: List[int],
                     heightacc: int, widthacc: int, it: int, count: int) -> int:
  """Determines a somewhat smart boundary on the height parameter, tries to fit the
  lower row of the board with as much height as possible

  Args:
    n: amount of pieces to be tried
    cwidth: list of widths of pieces to be tried
    cheight: list of heights of pieces to be tried
    heightacc: accumulator for height of pieces that are placed
    widthacc: accumulator for remaining width to place pieces
    it: iterator
    count: amount of pieces placed at bottom row
  """
  #check if current it fits
  if(it==n):
    return heightacc

  if(widthacc <= 0):
    return heightacc
  #if yes, max (fit, no fit)
  #if no, (no fit)
  if(widthacc-cwidth[it]>=0):
                #fit
    if(count>0):
      #for every piece added after the first piece, calculate leftover height
      h_added = cheight[it]
    else:
      h_added = 0
    return max(determine_hbound(n, cwidth, cheight, heightacc+h_added, widthacc-cwidth[it], it+1, count+1),
                #don't fit
               determine_hbound(n, cwidth, cheight, heightacc, widthacc, it+1, count))
  else:
    return (determine_hbound(n, cwidth, cheight, heightacc, widthacc, it+1, count))


def report_result(data: Dict[str, Union[int, List[int]]], result: Result, plot_intermediate=False, **kwargs):
  """Reports to the user the result from a minizinc run

  Args: 
    data (Dict[str, Union[int, List[int]]]): Input data for the minizinc instance
    result (Result): Result object from minizinc instance
    **kwargs: Additional arguments passed to plot_vlsi function
  """
  stat = result.statistics
  print("Instance solved")
  print("Took: %ss to find %d solutions" % (stat["solveTime"].total_seconds(), stat["nSolutions"]))
  print("Nodes: %d - failures %d" % (stat["nodes"], stat["failures"]))

  if plot_intermediate:
    solution_x = [result[i, "x"] for i in range(len(result))]
    solution_y = [result[i, "y"] for i in range(len(result))]
    plot_multi_vlsi(data["cwidth"], data["cheight"], solution_x, solution_y, **kwargs)
  else:
    solution_x = result[-1, "x"]
    solution_y = result[-1, "y"]
    plot_vlsi(data["cwidth"], data["cheight"], solution_x, solution_y, **kwargs)

  return stat["solveTime"].total_seconds(), stat["nSolutions"], stat["nodes"], stat["failures"]


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
    parser.add_argument("--plot", "-p", action="store_true", help="Plot final result. Defaults to false.")
    parser.add_argument("--plot-all", "-pall", action="store_true", help="Plot all results. Defaults to false.")
    parser.add_argument("--solver", "-solver", "-s", nargs=1, type=str, default="chuffed", choices=["chuffed", "gecode"],
                        help="Solver that Minizinc will use. Defaults to Chuffed.")
                        

    # parse CLI arguments
    args = parser.parse_args()
    # use specified models or use all models if left empty
    models = args.models if len(args.models) > 0 else enumerate_models()
    # load specified instances or load all instances if left empty
    instances = args.instances if len(args.instances) > 0 else enumerate_instances()
    # TODO: Solver config
    gecode = Solver.lookup(args.solver)
    
    # execute each model
    for m in models:
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
        data = txt2dict(i)
        #create model new everytime so we can change parameter value
        mzn_model = Model(m)
        mzn_instance = Instance(gecode, mzn_model)
        # set data variables on instance
        for k, v in data.items():
          mzn_instance[k] = v

        # run model
        result = mzn_instance.solve(intermediate_solutions=True)

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

        instance_num += 1
      
      if args.wandb:
        #finish run with this model, select next model
        run.finish()
      #reset counter for custom step
      instance_num = 1


  except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
