import typing
import z3
import numpy as np
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
    # build cboard
    self.cboard = z3.Array([[[z3.Bool(f"cb_{c}_{i}_{j}") for j in range(self.WIDTH)] for i in range(self.HEIGHT)] for c in range(self.N)])
    # cx
    self.cx = z3.Array('x', z3.IntSort(), z3.IntSort())
    # cy
    self.cy = z3.Array('y', z3.IntSort(), z3.IntSort())

  def _idxs_positions(self):
    """
    Returns:
        List[Tuple[int, int]]: left-bottom index of rectangle placings
    """
    super()._idxs_positions()

    idxs = list()

    for c in range(self.N):
      idxs.append((self.solver.model().evaluate(self.cx[c]), self.solver.model().evaluate(self.cy[c])))

    return idxs

  def _at_most_n(self, vars: List, n: int) -> z3.BoolRef:
    """
    Constraint that at most n variables are true.
    Args:
        vars (List): Variables
        n (int): At most n variables needs to be true
    Returns:
        z3.BoolRef: Constraint
    """
    return z3.And([z3.Not(z3.And(c)) for c in combinations(list(vars), n + 1)])

  def _at_least_n(self, vars: List, n: int) -> z3.BoolRef:
    """
    Constraint that at lest n variables are true.
    Args:
        vars (List): Variables
        n (int): At least n variables needs to be true
    Returns:
        z3.BoolRef: Constraint
    """
    return z3.Or([z3.And(c) for c in combinations(list(vars), n)])

  def _exactly_n(self, vars: List, n: int) -> z3.BoolRef:
    """
    Constraint that exactly n variables are true.
    Args:
        vars (List): Variables
        n (int): n variables needs to be true
    Returns:
        z3.BoolRef: Constraint
    """
    return z3.And(self._at_least_n(vars, n), self._at_most_n(list(vars), n))

  def channeling_constraint(self) -> z3.BoolRef:
    """
    Only channel if position is in bound
    """

    constraints = list()

    for c in range(self.N):
      for i in range(self.cheight[c]):
        for j in range(self.cwidth[c]):
          constraints.append(self.cboard[c, z3.Select(self.cy, c)+i, z3.Select(self.cx, c)+j])
      return z3.And(constraints)

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
      for i in range(self.HEIGHT - self.cheight[c] + 1, self.HEIGHT):
        for j in range(self.WIDTH - self.cwidth[c] + 1, self.WIDTH):
          constraints.append(z3.Not(z3.Or(self.cy[c, i], self.cx[c, j])))

    return z3.And(constraints)

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
      constraints.append(self._exactly_n(self.cy[c, :], 1))
      constraints.append(self._exactly_n(self.cx[c, :], 1))


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

    for i in range(self.HEIGHT):
      for j in range(self.WIDTH):
        constraints.append(self._at_most_n(self.cboard[:, i, j], 1))

    return z3.And(constraints)

  def area_constraint(self) -> z3.BoolRef:
    total_area = 0
    for c in range(self.N):
      total_area += self.cheight[c] * self.cwidth[c]
    board_area = self.WIDTH * self.HEIGHT

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
    self.solver.add(
      #self.bound_constraint(),
      self.channeling_constraint(),
      self.overlapping_constraint(),
      #self.placement_constraint(),
      #self.horizontal_symmetry(),
      #self.vertical_symmetry(),
    )
