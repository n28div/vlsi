include "globals.mzn";

int: WIDTH; % width of the circuit
int: N; % number of elements in the input file

set of int: ELEMENTS = 1..N;
array[ELEMENTS] of int: cwidth;
array[ELEMENTS] of int: cheight;

% compute worst case scenario boundaries for lower and upper bounds in maximum height search
% worst we can do is stacking all the circuits vertically
int: y_ub = sum (e in ELEMENTS) (cheight[e]);
% lower bound can naively be implemented by relaxing the board fixed width and stacking all circuits horizontally
% thus the min height is equal to the tallest circuit in the board
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
output [ "X = \(x) \nY = \(y) \nh = \(HEIGHT) " ];