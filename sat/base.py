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
    # build cboard
    self.cboard = np.array([[[z3.Bool(f"cb_{c}_{i}_{j}") for j in range(self.WIDTH)] for i in range(self.HEIGHT_UB)] for c in range(self.N)])
    # cx
    self.cx = np.array([[z3.Bool(f"cx_{c}_{j}") for j in range(self.WIDTH)] for c in range(self.N)])
    # cy
    self.cy = np.array([[z3.Bool(f"cy_{c}_{i}") for i in range(self.HEIGHT_UB)] for c in range(self.N)])
    # allowed_height
    self.a_h = np.array([z3.Bool(f"a_{i}") for i in range(self.HEIGHT_UB)])

  def post_dynamic_constraints(self):
    """
    Method used to post static dynamic on the model 
    e.g. those contraints that do depend on the height that is being tried
    
    Raises:
        NotImplementedError: If not overriden raises not implemented error
    """
    pass
  

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
    self.HEIGHT = height

    # check if model has been solved once
    #if self._solved_once:
    #  self.solver.pop()

    # post dynamic constraints
    self.setup_time = time.perf_counter()

    if height < self.HEIGHT_UB:
      # a_h is 0-indexed so this is actually removing previous height from being used
      self.solver.add(z3.Not(self.a_h[height]))
    
    #self.solver.push()
    self.post_dynamic_constraints()
    self.setup_time = time.perf_counter() - self.setup_time

    # search for a solution
    self.solved_time = time.perf_counter()
    self.solver.check()
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
