import typing
import z3
import numpy as np
from .naive_model import SmtModel
from itertools import chain, combinations
from typing import List


class NaiveModelRot(SmtModel):
    ROTATIONS = True

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
        idxs = list()

        for c in range(self.N):
            idxs.append((self.solver.model().evaluate(self.cx[c]).as_long(),
                         self.solver.model().evaluate(self.cy[c]).as_long()))

        return idxs

    @property
    def rotations(self):
        model = self.solver.model()
        rot = list()

        for r in self.rotated:
            try:
                rot.append(bool(model.evaluate(r)))
            except:
                rot.append(False)

        return rot

    def setup(self):
        # build default setup
        super().setup()

        # build flattenpos arrays
        self.rotated = np.array([z3.Bool(f"r_{i}") for i in range(self.N)])
            
    def allowed_height_constraint(self):
        """
        Ensure no placement outside of max height
        """
        constraints = list()
        for y in range(self.N):
            constraints.append(
                z3.If(
                    self.rotated[y],
                    self.cy[y] + self.cwidth[y] <= self.HEIGHT,
                    self.cy[y] + self.cheight[y] <= self.HEIGHT  
                )
            )
            constraints.append(self.cy[y] >= 0)

        return z3.And(constraints)

    def allowed_width_constraint(self):
        """
        Ensure no placement outside of max width
        """
        constraints = list()
        for x in range(self.N):
            constraints.append(
                z3.If(
                    self.rotated[x],
                    self.cx[x] + self.cheight[x] <= self.WIDTH,
                    self.cx[x] + self.cwidth[x] <= self.WIDTH  
                )
            )
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
                    # both not rotated
                    constraints.append(z3.Implies(
                        z3.Not(z3.And(self.rotated[i], self.rotated[j])),
                        z3.Or(
                            self.cx[i] + self.cwidth[i]  <= self.cx[j], self.cx[j] + self.cwidth[j]  <= self.cx[i],
                            self.cy[i] + self.cheight[i] <= self.cy[j], self.cy[j] + self.cheight[j] <= self.cy[i]
                        )))

                    # only i rotated
                    constraints.append(z3.Implies(
                        z3.And(self.rotated[i], z3.Not(self.rotated[j])),
                        z3.Or(
                            self.cx[i] + self.cheight[i] <= self.cx[j],
                            self.cx[j] + self.cwidth[j] <= self.cx[i],
                            self.cy[i] + self.cwidth[i] <= self.cy[j],
                            self.cy[j] + self.cheight[j] <= self.cy[i])))

                    # only j rotated
                    constraints.append(z3.Implies(
                        z3.And(z3.Not(self.rotated[i]), self.rotated[j]),
                        z3.Or(
                            self.cx[i] + self.cwidth[i] <= self.cx[j],
                            self.cx[j] + self.cheight[j] <= self.cx[i],
                            self.cy[i] + self.cheight[i] <= self.cy[j],
                            self.cy[j] + self.cwidth[j] <= self.cy[i])))

                    # both rotated
                    constraints.append(z3.Implies(
                        z3.And(self.rotated[i], self.rotated[j]),
                        z3.Or(
                            self.cx[i] + self.cheight[i] <= self.cx[j],
                            self.cx[j] + self.cheight[j] <= self.cx[i],
                            self.cy[i] + self.cwidth[i] <= self.cy[j],
                            self.cy[j] + self.cwidth[j] <= self.cy[i])))

        return z3.And(constraints)

    def post_static_constraints(self):
        """
        Post static constraints
        """
        self.solver.add(
            self.allowed_height_constraint(),
            self.allowed_width_constraint(),
            self.overlapping_constraint(),
        )
