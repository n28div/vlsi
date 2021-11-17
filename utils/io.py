from typing import Dict, Union, List, Tuple

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

def save_solution(path:str, data: Dict[str, Union[int, List[int]]], positions: List[Tuple[int, int]]):
  """
  Save solution into appropriate format

  Args:
      path (str): Path of file were solution in written
      data (Dict[str, Union[int, List[int]]]): Data of instance being solved
      result (Result): Result coming from the minizinc interface
  """
  highest_idx = positions.index(max(positions, key=lambda x: x[1]))
  height = positions[highest_idx][1] + data["cheight"][highest_idx]

  with open(path, "w") as f:
    f.write(f"{data['WIDTH']} {height}\n")
    f.write(f"{data['N']}\n")

    for (x, y), h, w in zip(positions, data["cheight"], data["cwidth"]):
      f.write(f"{w} {h} {x} {y}\n")
