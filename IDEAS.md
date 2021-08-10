# Random ideas

## State representation
we'll have to exploit the [`cumulative`](https://www.minizinc.org/doc-2.5.5/en/lib-globals.html#index-119) constraint for sure, setting up the model so that each rectangle height is the number of resources it requires and its weight is the duration.
In this way however we end up stacking horizontally and then vertically (or the opposite?), we can stack in the complementary direction by rotating of 90° the timetable, basically encoding width with the time a resource is being used and height with the resource required.

we can then enforce the global contraint and search for a feasible solution.

### Auxiliary variables
Maybe a boolean matrix encoding the whole chip?
so that we can later use this also for symmetry breakings.
The cell `(i, j)` in the matrix is set to `True` if in the timetable at time `j` we need `i` resources.

We could also build a 3d-matrix so that we can also keep track of each rectangle position: if we use a single matrix we only have a global vision of occupied vs not occupied cells. 
If one matrix for each rectangle that needs to be placed we can keep track of the position of each rectangle.

We only need to make sure (through a constraint?) that each 2d-matrix is pairwise disjunct.

By using 3d-matrix as aux variable we can enforce value symmetry between rectangles that have the same size.

