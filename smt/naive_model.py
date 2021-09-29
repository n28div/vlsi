import typing
import z3
import numpy as np
from .base import SmtModel
from itertools import chain, combinations
from typing import List


class NaiveModel(SmtModel):
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
            idxs.append((self.solver.model().evaluate(self.cx[c]).as_long(),
                         self.solver.model().evaluate(self.cy[c]).as_long()))

        return idxs

    def allowed_height_constraint(self):
        """
    Ensure no placement outside of max height
    """
        constraints = list()
        for y in range(self.N):
            constraints.append(self.cy[y] + self.cheight[y] <= self.HEIGHT)
            constraints.append(self.cy[y] >= 0)

        return z3.And(constraints)

    def allowed_width_constraint(self):
        """
    Ensure no placement outside of max width
    """
        constraints = list()
        for x in range(self.N):
            constraints.append(self.cx[x] + self.cwidth[x] <= self.WIDTH)
            constraints.append(self.cx[x] >= 0)
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
        for i in range(self.N):
            for j in range(self.N):
                if i < j:
                    constraints.append(
                        z3.Or(
                            self.cx[i] + self.cwidth[i] <= self.cx[j],
                            self.cx[j] + self.cwidth[j] <= self.cx[i],
                            self.cy[i] + self.cheight[i] <= self.cy[j],
                            self.cy[j] + self.cheight[j] <= self.cy[i]
                        )
                    )

        return z3.And(constraints)

    def post_static_constraints(self):
        """
        Post static constraints
        """
        self.solver.add(
            self.allowed_height_constraint(),
            self.allowed_width_constraint(),
            self.overlapping_constraint()
        )
