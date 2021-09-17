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

  def allowed_height_constraint(self):
    """
    Ensure no placement outside of max height
    """
    constraints = list()

    for c in range(self.N):
      for i in range(self.HEIGHT_UB):
        constraints.append(z3.Implies(self.cy[c][i], self.a_h[i]))

    return z3.And(constraints)


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
      for i in range(self.HEIGHT_UB - self.cheight[c] + 1):
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
      # circuit can be placed on a certain row only if all rows to the circuits height are allowed
      # having enough room vertically is a necessary condition to place a circuit in a row
      for i in range(self.HEIGHT_UB - self.cheight[c] + 1):
        constraints.append(
          z3.Implies(self.cy[c, i], z3.And([self.a_h[i + h] for h in range(self.cheight[c])]))
        )
    
      # circuit cannot be placed on index that would bring it out of the board
      for i in range(self.HEIGHT_UB - self.cheight[c] + 1, self.HEIGHT_UB):
        constraints.append(z3.Not(self.cy[c, i]))

      # a circuit can be placed on a certain column only if it would not go out of the circuit
      for j in range(self.WIDTH - self.cwidth[c] + 1, self.WIDTH):
        constraints.append(z3.Not(self.cx[c, j]))

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

    for i in range(self.HEIGHT_UB):
      for j in range(self.WIDTH):
        constraints.append(self._at_most_n(self.cboard[:, i, j], 1))

    return z3.And(constraints)

  def post_static_constraints(self):
    """
    Post static constraints
    """
    self.solver.add(
      self.allowed_height_constraint(),
      self.cx_cy_leftbottom_constraint(),
      self.placement_constraint(),
      self.bound_constraint(),
      self.overlapping_constraint(),
      self.channeling_constraint()
    )