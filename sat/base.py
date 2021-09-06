from os import stat
from typing import Dict, Any, List, Tuple
import z3
from z3.z3 import Int

class SatModel(object):
  """
  Sat model implementing some common logic between solvers such as input interface, output interface etc.
  """

  def __init__(self, width: int, cwidth: List[int], cheight: List[int]):
    """Initialize solver and attributes

    Args:
        width (int): Boards width
        cwidth (List[int]): Width of each circuit
        cheight (List[int]): Height of each circuit
    """    
    self.N = len(cwidth)
    self.WIDTH = width
    self.cwidth = cwidth
    self.cheight = cheight
    
    self.solver = z3.Solver()

  def setup(self):
    """
    Method used to setup the model, creating needed variables and posting required constraints
    Raises:
        NotImplementedError: If not overriden raises not implemented error
    """
    raise NotImplementedError

  def post_constraints(self):
    """Method used to post constraints on the model
    Raises:
        NotImplementedError: If not overriden raises not implemented error
    """
    raise NotImplementedError
  
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

  def solve(self, height: int, *args, **kwargs):
    """
    Solve the model

    Args:
        height (int): Height of the board
    """
    # Setup the encoding
    self.HEIGHT = height
    self.setup()
    
    # Post the constraints
    self.post_constraints()

    # Search for feasible solution
    self.solver.check()

  def _idxs_positions(self) -> List[Tuple[int, int]]:
    """
    Raises:
        RuntimeError: Instance has not been solved
    Returns:
        List[Tuple[int, int]]: left-bottom index of rectangle placings
    """
    if not self.solved:
      raise RuntimeError("Model not solved!")

    pos = [(x, y) for y in range(self.HEIGHT) for x in range(self.WIDTH) for c in range(self.N) if self.solver.model().evaluate(self.iboard[c][y][x])]
    return pos

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



  """
  @property
  def statistics(self) -> Dict[str, Any]:
    if self.solved:
  """