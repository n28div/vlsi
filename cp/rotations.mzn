include "globals.mzn";
include "determine_hbound.mzn";
include "chuffed.mzn";

int: WIDTH; % width of the circuit
int: N; % number of elements in the input file

set of int: ELEMENTS = 1..N;
array[ELEMENTS] of int: cwidth;
array[ELEMENTS] of int: cheight;

int: y_ub = greedy_height(N, WIDTH, reverse(sort_by(cwidth, cheight)), reverse(sort(cheight)), 0, 0, 0, 1);
int: y_lb = max (e in ELEMENTS) (cheight[e]);

array[ELEMENTS] of var 0..WIDTH: x; % left-corner circuit positions, 0-indexed
array[ELEMENTS] of var 0..y_ub: y; % circuit y position, 0-indexed, goes from index 0 to upper bound

array[ELEMENTS] of var bool: rotated;
array[ELEMENTS] of var int: rwidth;
array[ELEMENTS] of var int: rheight;

constraint forall (e in ELEMENTS where cwidth[e] = cheight[e]) (rotated[e] = false);
constraint forall (e in ELEMENTS) (rwidth[e] = if (rotated[e]) then cheight[e] else cwidth[e] endif);
constraint forall (e in ELEMENTS) (rheight[e] = if (rotated[e]) then cwidth[e] else cheight[e] endif);

% maximum width is fixed by the parameter W
constraint max (e in ELEMENTS) (x[e] + rwidth[e]) <= WIDTH;
% no overlapping of boxes
constraint diffn(x, y, rwidth, rheight);
constraint cumulative(x, rwidth, rheight, HEIGHT);
constraint cumulative(y, rheight, rwidth, WIDTH);

% height of circuit is the highest placed circuit top-left corner
var y_lb..y_ub: HEIGHT = max (e in ELEMENTS) (y[e] + rheight[e]);

% implicit constraint: summing circuits width must be less or equal than board width for each board row
constraint forall (h in 0..HEIGHT) (sum (e in ELEMENTS where rheight[e] + y[e] > h /\ y[e] <= h) (rwidth[e]) <= WIDTH);
% implicit constraint: summing circuits height must be less or equal than height width for each board column
constraint forall (w in 0..WIDTH) (sum (e in ELEMENTS where rwidth[e] + x[e] > w /\ x[e] <= w) (rheight[e]) <= HEIGHT);

% we can build an auxiliary array containing the area of each circuit we can then post an easy implicit contraint: board area >= sum(circuits area) in each solution
var int: board_area = WIDTH * HEIGHT;
array[ELEMENTS] of int: carea = [cwidth[e]*cheight[e] | e in ELEMENTS];
constraint sum (e in ELEMENTS) (carea[e]) <= board_area;

% domain reduction for each element, remove idxs that would make the circuit go out of the board
constraint forall(e in ELEMENTS) (x[e] <= WIDTH - rwidth[e]);
constraint forall(e in ELEMENTS) (y[e] <= HEIGHT - rheight[e]);

% flatten the position of each circuit in a single int
% adapted from http://vlsicad.eecs.umich.edu/BK/Slots/cache/vlsicad.eecs.umich.edu/BK/BloBB/PAPERS/symcon-06.pdf
function var int: flattenpos(var int: i, var int: j) = (i * WIDTH) + j;
array[ELEMENTS] of var int: flatpos;
constraint forall (e in ELEMENTS) (flatpos[e] = flattenpos(y[e], x[e]));
% horizontal, vertical and combined symmetry breaking
constraint symmetry_breaking_constraint(lex_lesseq(flatpos, [flattenpos(y[e], WIDTH - rwidth[e] - x[e]) | e in ELEMENTS]));
constraint symmetry_breaking_constraint(lex_lesseq(flatpos, [flattenpos(HEIGHT - rheight[e] - y[e], x[e]) | e in ELEMENTS]));

% value symmetry: if two values of the same height are adjacent then break symmetry between them
constraint forall(e1, e2 in ELEMENTS where e1 > e2 /\ rheight[e1] = rheight[e2])
  (if y[e1] = y[e2] then x[e2] >= rwidth[e1] + x[e1] endif);

solve
  :: seq_search([
    int_search(y, first_fail, indomain_min), 
    int_search(x, first_fail, indomain_min)
   ]) 
  minimize HEIGHT;

output [ "X = \(x) \nY = \(y) \nh = \(HEIGHT) \nrotations: = \(rotated)" ];