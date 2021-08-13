from typing import Dict, Union, List
from glob import glob
import typing
from matplotlib.pyplot import title
from minizinc import Instance, Model, Solver, Result
from utils.plot import plot_vlsi
from natsort import natsorted
import sys, os

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

def report_result(data: Dict[str, Union[int, List[int]]], result: Result, **kwargs):
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


  solution_x = result[-1, "x"]
  solution_y = result[-1, "y"]
  plot_vlsi(data["cwidth"], data["cheight"], solution_x, solution_y, **kwargs)


if __name__ == "__main__":
  try:
    import argparse
    # define CLI arguments
    parser = argparse.ArgumentParser(description="Run minizinc vlsi solving method")
    parser.add_argument("--models", "-m", nargs="*", type=str,
                        required=True, help="Model(s) to use. Leave empty to use all.")
    parser.add_argument("--instances", "-i", nargs="*", type=str,
                        required=True, help="Instances(s) to load. Leave empty to use all.")

    # parse CLI arguments
    args = parser.parse_args()
    # use specified models or use all models if left empty
    models = args.models if len(args.models) > 0 else enumerate_models()
    # load specified instances or load all instances if left empty
    instances = args.instances if len(args.instances) > 0 else enumerate_instances()
    # TODO: Solver config
    gecode = Solver.lookup("gecode")

    # execute each model
    for m in models:
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

        report_result(data, result, title="%s | %s" % (m, i))
  except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
