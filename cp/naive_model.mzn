include "globals.mzn";

int: W = 8; % width of the circuit
int: N = 4; % number of elements in the input file

set of int: ELEMENTS = 1..N;
array[ELEMENTS, 1..2] of int: circuits = [|3, 3|
                                        3, 5|
                                        5, 3|
                                        5, 5|]; % 2D matrix containing height and width of the circuits to be placed

array[ELEMENTS] of var 0..W - 1: x; % left-corner circuit positions
array[ELEMENTS] of var 0..1000: y; % circuit y position

% maximum width is fixed by the parameter W
constraint forall (i in ELEMENTS) (x[i] + circuits[i, 1] < W);

% no overlapping of boxes
constraint diffn(x, y, [circuits[i, 1] | i in ELEMENTS], [circuits[i, 2] | i in ELEMENTS]);


var int: max_height = max (i in ELEMENTS) (y[i] + circuits[i, 2]);

solve minimize max_height;