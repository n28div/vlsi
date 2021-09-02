from typing import List
import z3

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
    self.status = self.solver.check()
    
    if self.status == z3.sat:
      self.result = self.solver.model()

    return self.status == z3.sat
