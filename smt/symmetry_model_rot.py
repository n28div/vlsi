import typing
import z3
import numpy as np
from .naive_model_rot import NaiveModelRot
from itertools import chain, combinations
from typing import List

def z3_bEq(a, b):
  """
  Boolean equality
  """
  return a == b

def z3_bLe(a, b):
  """
  Implement when a boolean is less or equal than another one
  """
  return a <= b
  
class SymmetryModelRot(NaiveModelRot):
  """
  Symmetry breaking model implementation
  """
  def setup(self):
    super().setup()
    # build flatpos
    self.flatpos = z3.IntVector("flatpos", self.N)
    self.flatpos_hor = z3.IntVector("flatpos_hor", self.N)
    self.flatpos_ver = z3.IntVector("flatpos_ver", self.N)

  def flatten_position(self, i, j):
      return i*self.WIDTH+j

  def channel_flatpos(self):
    constraints = list()

    for i in range(self.N):
      constraints.append(self.flatpos[i] == self.flatten_position(self.cy[i], self.cx[i]))
      constraints.append(
        z3.If(
          self.rotated[i],
          self.flatpos_hor[i] == self.flatten_position(self.cy[i], self.WIDTH - self.cheight[i] - self.cx[i]),
          self.flatpos_hor[i] == self.flatten_position(self.cy[i], self.WIDTH - self.cwidth[i] - self.cx[i])))
        
      constraints.append(
        z3.If(
          self.rotated[i],
          self.flatpos_ver[i] == self.flatten_position(self.HEIGHT - self.cwidth[i] - self.cy[i], self.cx[i]),
          self.flatpos_ver[i] == self.flatten_position(self.HEIGHT - self.cheight[i] - self.cy[i], self.cx[i])
        )
      )
        
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
    constraints.append(self._lex_lesseq(self.flatpos, self.flatpos_hor))
    constraints.append(self._lex_lesseq(self.flatpos, self.flatpos_ver))

    return z3.And(constraints)

  def post_static_constraints(self):
    """
    Post constraints on the model
    """
    super().post_static_constraints()
    self.solver.add(
      self.channel_flatpos(),
      self.symmetry_breaking()
    )