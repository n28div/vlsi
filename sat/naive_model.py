import z3
from .base import SatModel

class NaiveModel(SatModel):
  """
  Naive model implementation

  Each circuits gets a whole WIDTHxHEIGHT board representation
  Fixed width and not overlapping circuits constraints are posted.
  """

  def setup(self):
    """
    Builds boards encodings:
      * board - full board occupation
      * cboard - occupation of each circuit
      * cx and cy - row (column) of bottom-left-index of each circuits
    """
    # build board
    self.board = [[z3.Bool(f"b_{i}_{j}") for j in range(self.WIDTH)] for i in range(self.HEIGHT)]

    # build cboard
    self.cboard = [[[z3.Bool(f"cb_{c}_{i}_{j}") for j in range(self.WIDTH)] for i in range(self.HEIGHT)] for c in range(self.N)]

    # build cx and cy
    self.cy = [[z3.Bool(f"cy_{c}_{i}") for i in range(self.HEIGHT)] for c in range(self.N)]
    self.cx = [[z3.Bool(f"cx_{c}_{j}") for j in range(self.WIDTH)] for c in range(self.N)]


  def channeling_constraint(self):
    """
    Build channeling constraint
    """
    constraint = list()
    for i in range(self.HEIGHT):
      for j in range(self.WIDTH):
        for c in range(self.N):
          cx_cy_cond = z3.And(self.cy[c][i], self.cx[c][j])
          
          hor_cond = z3.And([z3.And(self.board[i][k], self.cboard[c][i][k]) for k in range(j, self.cwidth[c])])
          ver_cond = z3.And([z3.And(self.board[i][k], self.cboard[c][i][k]) for k in range(j, self.cwidth[c])])
          board_cboard = z3.And(hor_cond, ver_cond)

          constraint.append(cx_cy_cond == board_cboard)
    
    return constraint


  def not_overlapping_constraint(self):
    """
    Build not overlapping constraint
    """
    constraint = \
      z3.And([
        z3.And([
          z3.Not(z3.And([
            self.cboard[k][i][j]
          for k in range(self.N)]))
        for j in range(self.WIDTH)])
      for i in range(self.HEIGHT)])

    return constraint

  def feasible_placement_constraint(self):
    """
    Build feasible placement constraint
    """
    constraint = \
      z3.And([
        z3.And([
          z3.And([
            z3.Not(z3.And(self.cy[c][i], self.cx[c][j]))
          for j in range(self.WIDTH - self.cwidth[c], self.WIDTH)])
        for i in range(self.HEIGHT - self.cheight[c], self.HEIGHT)])
      for c in range(self.N)])
    
    return constraint

  def post_constraints(self):
    """
    Post constraints on the model
    """
    self.solver.add(self.channeling_constraint())
    #self.solver.add(self.not_overlapping_constraint())
    #self.solver.add(self.feasible_placement_constraint())