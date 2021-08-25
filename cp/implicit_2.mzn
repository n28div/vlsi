include "globals.mzn";
include "determine_hbound.mzn";

int: WIDTH; % width of the circuit
int: N; % number of elements in the input file

set of int: ELEMENTS = 1..N;
array[ELEMENTS] of int: cwidth;
array[ELEMENTS] of int: cheight;

int: y_ub = sum (e in ELEMENTS) (cheight[e]) - determine_hbound(N, cwidth, cheight, 0, WIDTH, 1, 0);
int: y_lb = max (e in ELEMENTS) (cheight[e]);

array[ELEMENTS] of var 0..WIDTH: x; % left-corner circuit positions, 0-indexed
array[ELEMENTS] of var 0..y_ub: y; % circuit y position, 0-indexed, goes from index 0 to upper bound

% maximum width is fixed by the parameter W
constraint max (e in ELEMENTS) (x[e] + cwidth[e]) <= WIDTH;
% no overlapping of boxes
constraint diffn(x, y, cwidth, cheight);

% height of circuit is the highest placed circuit top-left corner
var y_lb..y_ub: HEIGHT = max (e in ELEMENTS) (y[e] + cheight[e]);

% implicit constraint: summing circuits width must be less or equal than board width for each board row
constraint forall (h in 0..HEIGHT) (sum (e in ELEMENTS where cheight[e] + y[e] > h /\ y[e] <= h) (cwidth[e]) <= WIDTH);
% implicit constraint: summing circuits height must be less or equal than height width for each board column
constraint forall (w in 0..WIDTH) (sum (e in ELEMENTS where cwidth[e] + x[e] > w /\ x[e] <= w) (cheight[e]) <= HEIGHT);

% we can build an auxiliary array containing the area of each circuit we can then post an easy implicit contraint: board area = sum(circuits area) in each solution
var int: board_area = WIDTH * HEIGHT;
array[ELEMENTS] of int: carea = [cwidth[e]*cheight[e] | e in ELEMENTS];
constraint sum (e in ELEMENTS) (carea[e]) <= board_area;

solve minimize HEIGHT;
output [ "X = \(x) \nY = \(y) \nh = \(HEIGHT) " ];