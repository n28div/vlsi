from os import stat
from typing import Dict, Any, List, Tuple
import z3
from z3.z3 import Int, Not
import time
import numpy as np

class SatModel(object):
  """
  Sat model implementing some common logic between solvers such as input interface, output interface etc.
  """

  def __init__(self, width: int, cwidth: List[int], cheight: List[int], lb: int, ub: int):
    """Initialize solver and attributes

    Args:
        width (int): Boards width
        cwidth (List[int]): Width of each circuit
        cheight (List[int]): Height of each circuit
        lb (int): Height lower bound
        ub (int): Height upper bound
    """    
    self.N = len(cwidth)
    self.WIDTH = width

    self.cwidth = cwidth
    self.cheight = cheight
    
    self.HEIGHT_LB = lb
    self.HEIGHT_UB = ub
    
    # build the board representation
    self.setup()
    self.solver = z3.Solver()

    #self.solver.set("timeout", 300)
    self._solved_once = False
    self.init_time = time.perf_counter()
    self.post_static_constraints()
    self.init_time = time.perf_counter() - self.init_time

    self.solved_time = -1
    self.setup_time = 0

  def setup(self):
    """
    Builds boards encodings:
      * cboard - occupation of each circuit
      * cx - column occupied by circuit c
      * cy - row occupied by circuit c

    Board is built as high as upper bounds goes so that it can be reused.
    """

    # cx
    #self.cx = z3.IntVector('x', self.N)
    self.cx = np.array([z3.Int(f"cx_{i}") for i in range(self.N)])
    # cy
    #self.cy = z3.IntVector('y', self.N)
    self.cy = [z3.Int(f"cy_{i}") for i in range(self.N)]

    #self.cwidth = [z3.Int(f"cx_{i}") for i in range(self.N)]
    #self.cheight = [z3.Int(f"cy_{i}") for i in range(self.N)]
    #for i in range(self.N):
    #  self.solver.add(self.cwidth[i] == self.cwidth_z3[i])
    #  self.solver.add(self.cheight[i] == self.cheight_z3[i])

    self.HEIGHT = z3.Int('HEIGHT')


  def post_static_constraints(self):
    """
    Method used to post static constraints on the model 
    e.g. those contraints that do not depend on the height that is being tried
    
    Raises:
        NotImplementedError: If not overriden raises not implemented error
    """
    pass
  
  @property
  def solved(self) -> bool:
    """
    Returns:
        bool: instance has been solved or not
    """
    try:
      self.solver.model()
      return True
    except:
      return False

  def solve(self, height: int):
    """
    Solve the model

    Args:
        height (int): Height of the board
    """
    # setup time is time spent setting up before actually solving
    self.setup_time = 0
    # set the current height

    # post dynamic constraints
    self.setup_time = time.perf_counter()
    
    self.setup_time = time.perf_counter() - self.setup_time

    # search for a solution
    self.solved_time = time.perf_counter()
    self.solver.add(self.HEIGHT <= height)
    issat = self.solver.check()
    print(issat)
    self.solved_time = time.perf_counter() - self.solved_time
    
    self._solved_once = True

  def _idxs_positions(self) -> List[Tuple[int, int]]:
    """
    Raises:
        RuntimeError: Instance has not been solved
    Returns:
        List[Tuple[int, int]]: left-bottom index of rectangle placings
    """
    if not self.solved:
      raise RuntimeError("Model not solved!")

  @property
  def x(self) -> List[int]:
    """
    Returns:
        List[int]: Rectangles left bottom index x-positions
    """
    return [p[0] for p in self._idxs_positions()]

  @property
  def y(self) -> List[int]:
    """
    Returns:
        List[int]: Rectangles left bottom index y-positions
    """
    return [p[1] for p in self._idxs_positions()]

  @property
  def positions(self) -> Tuple[List[int], List[int]]:
    """
    Returns:
        Tuple[List[int], List[int]]: Rectangles left-bottom x and y positions
    """
    return self.x, self.y

  @property
  def time(self) -> Dict:
    """
    Returns:
      Dict: Time taken to solve the instance, split into constraint posting and actual solving
    """
    return {
      "init": self.init_time,
      "solve": self.solved_time,
      "setup": self.setup_time
    }
