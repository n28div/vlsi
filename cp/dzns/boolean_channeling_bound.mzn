include "globals.mzn";

int: WIDTH; % width of the circuit
int: N; % number of elements in the input file
%int: HBOUND; %parameter to substract from maximum hbound, UNCOMMENT FOR PYTHON

set of int: ELEMENTS = 1..N;
array[ELEMENTS] of int: cwidth;
array[ELEMENTS] of int: cheight;



function int: determine_hbound(int: n, array[ELEMENTS] of int: widths, array[ELEMENTS] of int: heights, int: heightacc, int: widthacc, int: it, int: count) = (
  if it > n then heightacc
  elseif widthacc <= 0 then heightacc
  elseif widthacc - widths[it] >= 0 then
    if count > 0 then let{int :h_added = heightacc+heights[it]} in
      max(determine_hbound(n, widths, heights, h_added, widthacc-widths[it], it+1, count+1),
        determine_hbound(n, widths, heights, heightacc, widthacc, it+1, count))
    else
      max(determine_hbound(n, widths, heights, heightacc, widthacc-widths[it], it+1, count+1),
        determine_hbound(n, widths, heights, heightacc, widthacc, it+1, count))
    endif
  else
    determine_hbound(n, widths, heights, heightacc, widthacc, it+1, count)
  endif
);
                                      
int: HBOUND = determine_hbound(N, cwidth, cheight, 0, WIDTH, 1, 0);
% compute worst case scenario boundaries for lower and upper bounds in maximum height search
% worst we can do is stacking all the circuits vertically
int: y_ub = sum (e in ELEMENTS) (cheight[e]) - HBOUND; % UNCOMMENT FOR PYTHON
%int: y_ub = sum (e in ELEMENTS) (cheight[e]); % UNCOMMENT FOR MINIZINC-IDE
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

% implicit constraint: summing circuits width must be less or equal than board width for each board row
constraint forall (h in 0..HEIGHT) (sum (e in ELEMENTS where cheight[e] + y[e] > h /\ y[e] <= h) (cwidth[e]) <= WIDTH);
% implicit constraint: summing circuits height must be less or equal than height width for each board column
constraint forall (w in 0..WIDTH) (sum (e in ELEMENTS where cwidth[e] + x[e] > w /\ x[e] <= w) (cheight[e]) <= HEIGHT);

% we can build an auxiliary array containing the area of each circuit we can then post an easy implicit contraint: board area >= sum(circuits area) in each solution
% we use as area boundaries the worst case scenario of having a WIDTH*y_ub board
var int: board_area = WIDTH * HEIGHT;
array[ELEMENTS] of int: carea = [cwidth[e]*cheight[e] | e in ELEMENTS];
constraint sum (e in ELEMENTS) (carea[e]) <= board_area;

% boolean channeling: each circuit bottom-left index is encoded as true in a matrix representing the whole board
array[0..y_ub, 0..WIDTH] of var bool: b;
%constraint forall (i in 0..y_ub, j in 0..WIDTH) (b[i, j] <-> exists (e in ELEMENTS) (x[e] = j /\ y[e] = i));
constraint forall(e in ELEMENTS) (b[y[e], x[e]]);

% horizontal flipping of the circuit

constraint lex_lesseq(array1d(b), [b[i, j] | i in 0..y_ub, j in reverse(0..WIDTH)]);
% vertical flipping of the circuit
constraint lex_lesseq(array1d(b), [b[i, j] | i in reverse(0..y_ub), j in 0..WIDTH]);


solve minimize HEIGHT;

output [ "X = \(x) \nY = \(y) \nh = \(HEIGHT) \n" ];
%output [ if fix(b[i, j]) then "X" else "." endif ++
%         if j == WIDTH then "\n" else "" endif | i in 0..fix(y_ub), j in 0..WIDTH];
