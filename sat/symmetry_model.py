import typing
import z3
import numpy as np
from .naive_model import NaiveModel
from itertools import chain, combinations
from typing import List

class SymmetryModel(NaiveModel):
  """
  Symmetry breaking model implementation
  """
  def horizontal_symmetry(self):

    constraints = list()
    for c in range(self.N):
      for i in range(self.WIDTH):
        z3.Xor(self.cx[c, i], self.cx[c, self.WIDTH-self.cwidth[c] - i])
    return z3.And(constraints)

  def vertical_symmetry(self):

    constraints = list()
    for c in range(self.N):
      for i in range(self.HEIGHT):
        z3.Xor(self.cy[c, i], self.cy[c, self.HEIGHT-self.cheight[c] - i])
    return z3.And(constraints)

  def post_constraints(self):
    """
    Post constraints on the model
    """
    super().post_constraints()
    
    self.solver.add(
      self.horizontal_symmetry(),
      self.vertical_symmetry(),
    )
