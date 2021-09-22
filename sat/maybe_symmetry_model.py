import typing
import z3
import numpy as np
from .naive_model import NaiveModel
from itertools import chain, combinations
from typing import List
  
class MaybeSymmetryModel(NaiveModel):
  """
  Symmetry breaking model implementation
  """
  def setup(self):
    super().setup()
    # build iboard
    self.iboard = np.array([[z3.Bool(f"cb_{i}_{j}") for j in range(self.WIDTH)] for i in range(self.HEIGHT_UB)])
    
  def iboard_channeling_constraint(self) -> z3.BoolRef:
    """
    Only channel if position is in bound
    """
    constraints = list()

    for i in range(self.HEIGHT_UB):
      for j in range(self.WIDTH):
        constraints.append(self.iboard[i, j] == z3.And(z3.Or(list(self.cx[:, j])), z3.Or(list(self.cy[:, i]))))
        
    return z3.And(constraints)

  def post_static_constraints(self):
    """
    Post constraints on the model
    """
    super().post_static_constraints()
    self.solver.add(
      self.iboard_channeling_constraint()
    )