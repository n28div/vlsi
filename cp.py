from typing import Dict, Union, List
from glob import glob
from minizinc import Instance, Model, Solver, Result

def enumerate_models() -> List[str]:
  """
  Enumerate implemented models.

  Returns: List[str]: List of implemented models
  """
  return glob("cp/*.mzn")

def enumerate_instances() -> List[str]:
  """
  Enumerate input instances

  Returns: List[str]: List of available instances
  """
  return glob("instances/*.txt")

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

def report_result(result: Result):
  """Reports to the user the result from a minizinc run

  Args: result (Result): Result object from minizinc instance
  """
  stat = result.statistics

  seconds = stat["solveTime"].microseconds / 10**6

  print("Instance solved")
  print("Took: %fs to find %d solutions" % (seconds, stat["nSolutions"]))
  print("Nodes: %d - failures %d" % (stat["nodes"], stat["failures"]))


if __name__ == "__main__":
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
    mzn_model = Model(m)
    mzn_instance = Instance(gecode, mzn_model)

    for i in instances:
      data = txt2dict(i)
      # set data variables on instance
      for k, v in data.items():
        mzn_instance[k] = v
      
      # run model
      result = mzn_instance.solve(intermediate_solutions=True)

      report_result(result)
