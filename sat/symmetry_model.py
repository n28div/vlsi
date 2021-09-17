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
  def _lex_lesseq(self, a, b) -> z3.BoolRef:
    """
    Less eq constraint implementation:

    given two arrays of boolean of same size, x1 and x2, then 
    for each element of x1 and x2, say x1[t] and x2[t] then
    x1 is lex_lesseq than x2 if either (~x1[t]) /\ x2[t]) \/ lex_lesseq(x1, x2) with t = t+1

    inspired by https://stackoverflow.com/questions/68557254/z3py-symmetry-breaking-constraint-by-lexicographic-order
    """
    # base case: we arrived at the end of both list, they should be ordered otherwise we would have ended before
    constraints = list()

    constraints.append(
        z3.Or(z3_bLe(a[0], b[0]), z3.And(z3_bLe(a[0], b[0]), z3_bLe(a[1], b[1])))
    )
    for i in range(1, len(a) - 1):
      # (a[i] == b[i]) -> (a[i + 1] <= b[i + 1])
      constraints.append(
        z3.Or(
          z3_bLe(a[i], b[i]),
          z3.Implies(
            z3.And([z3_bEq(a[j], b[j]) for j in range(0, i)]), 
            z3_bLe(a[i + 1], b[i + 1])
          )
        )
      )
    
    return z3.And(constraints)

  def symmetry_breaking(self):
    constraints = list()

    for c in range(self.N):
      flat = [self.cboard[c][i][j] for j in range(self.WIDTH) for i in range(self.HEIGHT_UB)]
      hor_flat = [self.cboard[c][i][j] for j in reversed(range(self.WIDTH)) for i in range(self.HEIGHT_UB)]
      #ver_flat = [self.cboard[c][i][j] for j in range(self.WIDTH) for i in reversed(range(self.HEIGHT))]
      
      constraints.append(self._lex_lesseq(flat, hor_flat))
      #constraints.append(self._lex_lesseq(flat, hor_flat))  
  
    return z3.And(constraints)

  def post_static_constraints(self):
    """
    Post constraints on the model
    """
    super().post_static_constraints()
    self.solver.add(self.symmetry_breaking())