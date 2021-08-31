include "globals.mzn";
include "determine_hbound.mzn";

int: WIDTH; % width of the circuit
int: N; % number of elements in the input file

set of int: ELEMENTS = 1..N;
array[ELEMENTS] of int: cwidth;
array[ELEMENTS] of int: cheight;

int: y_ub = greedy_height(N, WIDTH, reverse(sort_by(cwidth, cheight)), reverse(sort(cheight)), 0, 0, 0, 1);
int: y_lb = max (e in ELEMENTS) (cheight[e]);

array[ELEMENTS] of var 0..WIDTH: x; % left-corner circuit positions, 0-indexed
array[ELEMENTS] of var 0..y_ub: y; % circuit y position, 0-indexed, goes from index 0 to upper bound

% maximum width is fixed by the parameter W
constraint max (e in ELEMENTS) (x[e] + cwidth[e]) <= WIDTH;
% no overlapping of boxes
constraint diffn(x, y, cwidth, cheight);

% height of circuit is the highest placed circuit top-left corner
var y_lb..y_ub: HEIGHT = max (e in ELEMENTS) (y[e] + cheight[e]);
    
solve minimize HEIGHT;

output [ "X = \(x) \nY = \(y) \nh = \(HEIGHT) \n" ];