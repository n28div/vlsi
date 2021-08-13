include "globals.mzn";

int: WIDTH = 8; % width of the circuit
int: N = 4; % number of elements in the input file

set of int: ELEMENTS = 1..N;
array[ELEMENTS] of int: cwidth = [3, 3, 5, 5];
array[ELEMENTS] of int: cheight = [3, 5, 3, 5];

array[ELEMENTS] of var 0..WIDTH: x; % left-corner circuit positions, 0-indexed
array[ELEMENTS] of var 0..1000: y; % circuit y position, 0-indexed

% maximum width is fixed by the parameter W
constraint max (e in ELEMENTS) (x[e] + cwidth[e]) <= WIDTH;
% no overlapping of boxes
constraint diffn(x, y, cwidth, cheight);

% height of circuit is the highest placed circuit top-left corner
var int: HEIGHT = max (e in ELEMENTS) (y[e] + cheight[e]);

solve minimize HEIGHT;
output [ "X = \(x) \nY = \(y) \nh = \(HEIGHT) " ];