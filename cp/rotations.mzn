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

%square elements are not allowed to be rotated
array[ELEMENTS] of bool: rotatable = [if cwidth[e] == cheight[e] then false else true endif | e in ELEMENTS];

array[ELEMENTS] of var bool: rotated;
array[ELEMENTS] of var int: rwidth;
array[ELEMENTS] of var int: rheight;

constraint forall (e in ELEMENTS) (rwidth[e] = if (rotated[e] /\ rotatable[e]) then cheight[e] else cwidth[e] endif);
constraint forall (e in ELEMENTS) (rheight[e] = if (rotated[e] /\ rotatable[e]) then cwidth[e] else cheight[e] endif);
% maximum width is fixed by the parameter W
constraint max (e in ELEMENTS) (x[e] + rwidth[e]) <= WIDTH;
% no overlapping of boxes
constraint diffn(x, y, rwidth, rheight);

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

% horizontal symmetry breaking
constraint lex_lesseq(x, [(WIDTH - rwidth[e]) - x[e] | e in ELEMENTS]);
% vertical symmetry breaking
constraint lex_greatereq(y, [(HEIGHT - rheight[e]) - y[e] | e in ELEMENTS]);

% flatten the position of each circuit in a single int
% adapted from http://vlsicad.eecs.umich.edu/BK/Slots/cache/vlsicad.eecs.umich.edu/BK/BloBB/PAPERS/symcon-06.pdf
function var int: flattenpos(var int: i, var int: j) = (i * WIDTH) + j;
array[ELEMENTS] of var int: flatpos;
constraint forall (e in ELEMENTS) (flatpos[e] = flattenpos(y[e], x[e]));

% horizontal value symmetry: if two adjacent blocks of the same width are at the same y then they can be swapped
predicate hor_adjacent(var ELEMENTS: e1, var ELEMENTS: e2) = 
  if x[e1] < x[e2] then x[e1] + rwidth[e1] = x[e2] else x[e2] + rwidth[e2] = x[e1] endif;
constraint forall(e1, e2 in ELEMENTS where e1 != e2 /\ y[e1] = y[e2] /\ rheight[e1] = rheight[e2] /\ hor_adjacent(e1, e2))
  (lex_lesseq(flatpos, [if e = e1 then flatpos[e2] elseif e = e2 then flatpos[e1] else flatpos[e] endif | e in ELEMENTS]));

% vertical value symmetry: if two adjacent blocks of the same height are at the same x then they can be swapped
predicate ver_adjacent(var ELEMENTS: e1, var ELEMENTS: e2) = 
  if y[e1] < y[e2] then y[e1] + rheight[e1] = x[e2] else y[e2] + rheight[e2] = y[e1] endif;
constraint forall(e1, e2 in ELEMENTS where e1 != e2 /\ y[e1] = y[e2] /\ rheight[e1] = rheight[e2] /\ hor_adjacent(e1, e2))
  (lex_lesseq(flatpos, [if e = e1 then flatpos[e2] elseif e = e2 then flatpos[e1] else flatpos[e] endif | e in ELEMENTS]));

% total value symmetry: if two blocks are not adjacent but they have the same width and the same height then they can be swapped
constraint forall(e1, e2 in ELEMENTS where e1 != e2 /\ rwidth[e1] = rwidth[e2] /\ rheight[e1] = rheight[e2])
  (lex_lesseq(flatpos, [if e = e1 then flatpos[e2] elseif e = e2 then flatpos[e1] else flatpos[e] endif | e in ELEMENTS]));

% tallest element in (0, 0)
%constraint x[arg_max(rheight)] = 0 /\ y[arg_max(rheight)] = 0;

solve :: seq_search([int_search(rotated, first_fail, indomain_min),
                     int_search(reverse(sort_by(y, cheight)), input_order, indomain_min),
                     int_search(reverse(sort_by(x, cheight)), input_order, indomain_min)])
  minimize HEIGHT;

output [ "X = \(x) \nY = \(y) \nh = \(HEIGHT) \nrotations: = \(rotated) \nrotatable: = \(rotatable)" ];