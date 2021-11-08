include "globals.mzn";
include "determine_hbound.mzn";

int: WIDTH; % width of the circuit
int: N; % number of elements in the input file

set of int: ELEMENTS = 1..N;
array[ELEMENTS] of int: cwidth;
array[ELEMENTS] of int: cheight;

% get the permutation that sorts cheight
array[ELEMENTS] of ELEMENTS: sorted_idxs = reverse(arg_sort(cheight));
% sort cheight and cwidth by cheight
array[ELEMENTS] of int: s_cwidth = [cwidth[sorted_idxs[e]] | e in ELEMENTS];
array[ELEMENTS] of int: s_cheight = [cheight[sorted_idxs[e]] | e in ELEMENTS];

int: y_ub = greedy_height(N, WIDTH, s_cwidth, s_cheight, 0, 0, 0, 1);
int: y_lb = max (e in ELEMENTS) (cheight[e]);

array[ELEMENTS] of var 0..WIDTH: x; % left-corner circuit positions, 0-indexed
array[ELEMENTS] of var 0..y_ub: y; % circuit y position, 0-indexed, goes from index 0 to upper bound

% height of circuit is the highest placed circuit top-left corner
var y_lb..y_ub: HEIGHT = max (e in ELEMENTS) (y[e] + cheight[e]);

% maximum width is fixed by the parameter W
constraint max (e in ELEMENTS) (x[e] + cwidth[e]) <= WIDTH;
% no overlapping of boxes
constraint diffn(x, y, cwidth, cheight);
constraint cumulative(x, cwidth, cheight, HEIGHT);
constraint cumulative(y, cheight, cwidth, WIDTH);

% implicit constraint: summing circuits width must be less or equal than board width for each board row
constraint forall (h in 0..HEIGHT) (sum (e in ELEMENTS where cheight[e] + y[e] > h /\ y[e] <= h) (cwidth[e]) <= WIDTH);
% implicit constraint: summing circuits height must be less or equal than height width for each board column
constraint forall (w in 0..WIDTH) (sum (e in ELEMENTS where cwidth[e] + x[e] > w /\ x[e] <= w) (cheight[e]) <= HEIGHT);

% we can build an auxiliary array containing the area of each circuit we can then post an easy implicit contraint: board area >= sum(circuits area) in each solution
var int: board_area = WIDTH * HEIGHT;
array[ELEMENTS] of int: carea = [cwidth[e]*cheight[e] | e in ELEMENTS];
constraint sum (e in ELEMENTS) (carea[e]) <= board_area;

% domain reduction for each element, remove idxs that would make the circuit go out of the board
constraint forall(e in ELEMENTS) (x[e] <= WIDTH - cwidth[e]);
constraint forall(e in ELEMENTS) (y[e] <= HEIGHT - cheight[e]);

% flatten the position of each circuit in a single int
% adapted from http://vlsicad.eecs.umich.edu/BK/Slots/cache/vlsicad.eecs.umich.edu/BK/BloBB/PAPERS/symcon-06.pdf
function var int: flattenpos(var int: i, var int: j) = (i * WIDTH) + j;
array[ELEMENTS] of var int: flatpos;
constraint forall (e in ELEMENTS) (flatpos[e] = flattenpos(y[e], x[e]));

array[ELEMENTS] of var int: flatpos_hor;
constraint forall (e in ELEMENTS) (flatpos_hor[e] = flattenpos(y[e], (WIDTH - cwidth[e]) - x[e]));
array[ELEMENTS] of var int: flatpos_ver;
constraint forall (e in ELEMENTS) (flatpos_ver[e] = flattenpos((HEIGHT - cheight[e]) - y[e], x[e]));

% horizontal, vertical and combined symmetry breaking
constraint lex_lesseq(flatpos, flatpos_hor);
constraint lex_lesseq(flatpos, flatpos_ver);

solve :: seq_search([
   int_search(y, first_fail, indomain_max),
   int_search(x, first_fail, indomain_min),
   int_search([HEIGHT], input_order, indomain_min),
  ]) minimize HEIGHT;


output [ "X = \(x) \nY = \(y) \nh = \(HEIGHT)" ];