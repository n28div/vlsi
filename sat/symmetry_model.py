import typing
import z3
import numpy as np
from .naive_model import NaiveModel
from itertools import chain, combinations
from typing import List

def z3_bEq(a: z3.BoolRef, b: z3.BoolRef) -> z3.BoolRef:
  """
  Boolean equality
  """
  return a == b

def z3_bLe(a: z3.BoolRef, b: z3.BoolRef) -> z3.BoolRef:
  """
  Implement when a boolean is less or equal than another one
  """
  return z3.Implies(a, b)
  
class SymmetryModel(NaiveModel):
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


  def _lex_lesseq(self, a, b) -> z3.BoolRef:
    """
    Less eq constraint implementation
    from https://digitalcommons.iwu.edu/cgi/viewcontent.cgi?article=1022&context=cs_honproj
    """
    # base case: we arrived at the end of both list, they should be ordered otherwise we would have ended before
    constraints = list()

    constraints.append(z3_bLe(a[0], b[0]))
    
    for i in range(len(a) - 1):
      constraints.append(
        z3.Implies(
          z3.And([a[j] == b[j] for j in range(i + 1)]),
          z3_bLe(a[i + 1], b[i + 1])
        )
      )
    
    return z3.And(constraints)

  def symmetry_breaking(self):
    constraints = list()

    flat = [self.iboard[i][j] for i in range(self.HEIGHT_UB) for j in range(self.WIDTH)]
    hor_flat = [self.iboard[i][j] for i in range(self.HEIGHT_UB) for j in reversed(range(self.WIDTH))]
    ver_flat = [self.iboard[i][j] for i in reversed(range(self.HEIGHT_UB)) for j in range(self.WIDTH)]
    hor_ver_flat = [self.iboard[i][j] for i in reversed(range(self.HEIGHT_UB)) for j in reversed(range(self.WIDTH))]

    constraints.append(self._lex_lesseq(flat, hor_flat))
    constraints.append(self._lex_lesseq(flat, ver_flat))
    constraints.append(self._lex_lesseq(flat, hor_ver_flat))    

    return z3.And(constraints)

  def post_static_constraints(self):
    """
    Post constraints on the model
    """
    super().post_static_constraints()
    self.solver.add(
      self.iboard_channeling_constraint(),
      self.symmetry_breaking()
    )