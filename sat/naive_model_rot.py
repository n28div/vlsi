import typing
import z3
import numpy as np
from .base import SatModel
from itertools import chain, combinations
from typing import List

class NaiveModelRot(SatModel):
  """
  Naive model implementation

  Each circuits gets a whole WIDTHxHEIGHT board representation
  Fixed width and not overlapping circuits constraints are posted.
  """
  ROTATIONS = True

  def setup(self):
    """
    Builds board encoding
      * cboard - occupation of each circuit
      * cx - column occupied by circuit c
      * cy - row occupied by circuit c

    Board is built as high as upper bounds goes so that it can be reused.
    """
    # build cboard
    self.cboard = np.array([[[z3.Bool(f"cb_{c}_{i}_{j}") for j in range(self.WIDTH)] for i in range(self.HEIGHT_UB)] for c in range(self.N)])
    # cx
    self.cx = np.array([[z3.Bool(f"cx_{c}_{j}") for j in range(self.WIDTH)] for c in range(self.N)])
    # cy
    self.cy = np.array([[z3.Bool(f"cy_{c}_{i}") for i in range(self.HEIGHT_UB)] for c in range(self.N)])
    # allowed_height
    self.a_h = np.array([z3.Bool(f"a_{i}") for i in range(self.HEIGHT_UB)])
    # array that dictates which components have been rotated
    self.rot = np.array([z3.Bool(f"r_{i}") for i in range(self.N)])


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

  @property
  def rotations(self):
    rot = [self.solver.model().evaluate(self.rot[c]) for c in range(self.N)]
    rot = [r if type(r) is bool else False for r in rot]
    return rot

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
        constraints.append(z3.Implies(self.cy[c, i], self.a_h[i]))

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
      for i in range(self.HEIGHT_UB):
        for j in range(self.WIDTH):
          placed = z3.And(self.cy[c, i], self.cx[c, j])
          if (i < self.HEIGHT_UB - self.cheight[c] + 1) and (j < self.WIDTH - self.cwidth[c] + 1):
            filled = z3.And([self.cboard[c, i + u, j + v] for u in range(self.cheight[c]) for v in range(self.cwidth[c])])
            constraints.append(placed == filled)
          
          #if (i + self.cwidth[c] - 1 < self.HEIGHT_UB) and (j + self.cheight[c] - 1 < self.WIDTH):
          #  filled = z3.And([self.cboard[c, i + u, j + v] for u in range(self.cwidth[c]) for v in range(self.cheight[c])])
          #  constraints.append(placed == filled)
          

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
      not_rot = z3.Not(self.rot[c])
      rot = self.rot[c]

      if self.cwidth[c] < self.cheight[c]:
        min_dim = self.cwidth[c]
        min_width = True
      else:
        min_dim = self.cwidth[c]
        min_width = False

      for i in range(self.HEIGHT_UB):
        # circuit can be placed on a certain row only if all rows to the circuits height are allowed
        # having enough room vertically is a necessary condition to place a circuit in a row
        for i in range(self.HEIGHT_UB - min_dim + 1):
          constraints.append(
            z3.Implies(self.cy[c, i], z3.And([self.a_h[i + h] for h in range(min_dim)]))
          )

        # circuit cannot be placed on index that would bring it out of the board
        for i in range(min_dim + 1, self.HEIGHT_UB):
        
          if i + self.cheight[c] < self.HEIGHT_UB:
            fill = z3.And([self.a_h[i + h] for h in range(self.cheight[c])])
            constraints.append(
              z3.Implies(self.cy[c, i], z3.And(not_rot, fill))
            )
          elif i + self.cwidth[c] < self.HEIGHT_UB:
            # check if position i is possible only because circuit is rotated
            fill = z3.And([self.a_h[i + h] for h in range(self.cwidth[c])])
            constraints.append(
              z3.Implies(self.cy[c, i], z3.And(rot, fill))
            )
          else:
            constraints.append(z3.Not(self.cy[c, i]))
    
      #for i in range(self.WIDTH - 1):
      #  # check if position i is possible only because circuit is not rotated
      #  if i + self.cwidth[c] + 1 < self.WIDTH:
      #    constraints.append(z3.Implies(self.cx[c, i], not_rot))
      #  elif i + self.cheight[c] + 1 < self.WIDTH: 
      #    # check if position i is possible only because circuit is rotated
      #    constraints.append(z3.Implies(self.cx[c, i], rot))
      #  else:
      #    constraints.append(z3.Not(self.cx[c, i]))
    
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
      #self.overlapping_constraint(),
      self.channeling_constraint()
    )