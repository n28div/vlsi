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
      * cx - column occupied by circuit c
      * cy - row occupied by circuit c
    """
    # build cboard
    self.cboard = np.array([[[z3.Bool(f"cb_{c}_{i}_{j}") for j in range(self.WIDTH)] for i in range(self.HEIGHT)] for c in range(self.N)])
    # cx
    self.cx = np.array([[z3.Bool(f"cx_{c}_{j}") for j in range(self.WIDTH)] for c in range(self.N)])
    # cy
    self.cy = np.array([[z3.Bool(f"cy_{c}_{i}") for i in range(self.HEIGHT)] for c in range(self.N)])

  def _idxs_positions(self):
    """
    Returns:
        List[Tuple[int, int]]: left-bottom index of rectangle placings
    """
    super()._idxs_positions()

    idxs = list()

    for c in range(self.N):
      for i in range(self.HEIGHT):
        if self.solver.model().evaluate(self.cy[c, i]):
          for j in range(self.WIDTH):
            if self.solver.model().evaluate(self.cx[c, j]):
              idxs.append((j, i))
              break
          break

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

  def cx_cy_leftbottom_constraint(self) -> z3.BoolRef:
    """
    Ensure that only one bottom left index is set
    """
    constraints = list()

    for c in range(self.N):
      constraints.append(self._exactly_n(self.cx[c], 1))
      constraints.append(self._exactly_n(self.cy[c], 1))

    return z3.And(constraints)

  def channeling_constraint(self) -> z3.BoolRef:
    """
    Only channel if position is in bound
    """
    constraints = list()

    for c in range(self.N):
      for i in range(self.HEIGHT - self.cheight[c] + 1):
        for j in range(self.WIDTH - self.cwidth[c] + 1):
          constraints.append(z3.And(self.cy[c, i], self.cx[c, j])
                              ==
                              z3.And([self.cboard[c, i + u, j + v] for u in range(self.cheight[c]) for v in range(self.cwidth[c])]))

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

  def post_constraints(self):
    """
    Post constraints on the model
    """
    self.solver.add(
      self.cx_cy_leftbottom_constraint(),
      self.bound_constraint(),
      self.channeling_constraint(),
      self.overlapping_constraint(),
      self.placement_constraint()
    )
