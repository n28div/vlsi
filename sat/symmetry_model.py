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
  
  def _lex_lesseq(self, a, b) -> z3.BoolRef:
    """
    Less eq constraint implementation:

    given two arrays of boolean of same size, x1 and x2, then 
    for each element of x1 and x2, say x1[t] and x2[t] then
    x1 is lex_lesseq than x2 if either (~x1[t]) /\ x2[t]) \/ lex_lesseq(x1, x2) with t = t+1

    inspired by https://stackoverflow.com/questions/68557254/z3py-symmetry-breaking-constraint-by-lexicographic-order
    """
    # base case: we arrived at the end of both list, they should be ordered otherwise we would have ended before
    if len(a) == 0:
      return True
    else:
      return z3.Or(z3.And(z3.Not(a[0]), b[0]), self._lex_lesseq(a[1:], b[1:]))

  def horizontal_symmetry(self):
    return z3.And([self._lex_lesseq(self.cx[c], np.flip(self.cx[c])) for c in range(self.N)])

  def vertical_symmetry(self):
    return z3.And([self._lex_lesseq(self.cy[c], np.flip(self.cy[c])) for c in range(self.N)])

  def post_constraints(self):
    """
    Post constraints on the model
    """
    super().post_constraints()
    
    self.solver.add(
      self.horizontal_symmetry(),
      self.vertical_symmetry(),
    )
