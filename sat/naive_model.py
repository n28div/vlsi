import typing
import z3
from .base import SatModel
from itertools import chain, combinations
from typing import List

class NaiveModel(SatModel):
  """
  Naive model implementation

  Each circuits gets a whole WIDTHxHEIGHT board representation
  Fixed width and not overlapping circuits constraints are posted.
  """

  def setup(self):
    """
    Builds boards encodings:
      * cboard - occupation of each circuit
    """
    # build board
    self.iboard = [[[z3.Bool(f"ib_{c}_{i}_{j}") for j in range(self.WIDTH)] for i in range(self.HEIGHT)] for c in range(self.N)]
    # build cboard
    self.cboard = [[[z3.Bool(f"cb_{c}_{i}_{j}") for j in range(self.WIDTH)] for i in range(self.HEIGHT)] for c in range(self.N)]
    
  def bound_constraint(self) -> z3.BoolRef:
    """
    Bound values of iboard to keep circuits in board.

    Args:
        c (int): Circuit of boolean
        i (int): Row of boolean
        j (int): Column of boolean
    Returns:
        z3.BoolRef: Constraint to be placed on solver
    """
    constraints = list()
    
    for c in range(self.N):
      for i in range(self.HEIGHT):
        for j in range(self.WIDTH):
          if j + self.cwidth[c] > self.WIDTH or i + self.cheight[c] > self.HEIGHT:
            constraints.append(z3.Not(self.iboard[c][i][j]))
    
    return z3.And(constraints)
          
   
  def _at_most_one(self, vars: List) -> z3.BoolRef:
    """
    Constraint that at most one variable is true.
    Args:
        vars (List): Variables
    Returns:
        z3.BoolRef: Constraint
    """
    return z3.And([z3.Not(z3.And(v1, v2)) for v1, v2 in combinations(vars, 2)])

  def placement_constraint(self) -> z3.BoolRef:
    """
    For each circuit in indexes one and only one index can be true

    Args:
        c (int): Circuit of boolean
        i (int): Row of boolean
        j (int): Column of boolean
    Returns:
        z3.BoolRef: Constraint to be placed on solver
    """
    constraints = list()

    for c in range(self.N):
      flattened_ib = list(chain(*self.iboard[c]))
      at_least_one = z3.Or(flattened_ib)
      at_most_one = self._at_most_one(flattened_ib)
      constraints.append(z3.And(at_least_one, at_most_one))
    
    return z3.And(constraints)
  
  def overlapping_constraint(self) -> z3.BoolRef:
    """
    Overlapping constraint between two circuits. Only one circuit can be at index (i,j).
    
    Args:
        c (int): Circuit of boolean
        i (int): Row of boolean
        j (int): Column of boolean
    Returns:
        z3.BoolRef: Constraint to be placed on solver
    """
    constraints = list()
    
    for c in range(self.N):
      for i in range(self.HEIGHT):
        for j in range(self.WIDTH):
          if i + self.cheight[c] < self.HEIGHT and j + self.cwidth[c] < self.WIDTH:
            constraints.append(
              z3.Implies(self.iboard[c][i][j], z3.And([self.iboard[c][i + u][j + v] for u in range(self.cheight[c]) for v in range(self.cwidth[c])]))
            )

    return z3.And(constraints)
     
  def post_constraints(self):
    """
    Post constraints on the model
    """         
    self.solver.add(
      self.bound_constraint(),
      self.placement_constraint(),
      self.overlapping_constraint(),
    )
