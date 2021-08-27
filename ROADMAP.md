## CP

### Python-stuff
* [x] Preprocess text files and feed them to minizinc model
* [x] Visualize results using plots 
* [x] export plots to use in the report
* [x]  Configure to batch run models with all instances and record statistics
* [x]  Graph the statistics

### Minizinc models
#### TODO
* [x] Naive model (pt 1 in project paper) **naive_model.mzn**
* [x] Implicit contraint (pt 2 in project paper): elements on rows should sum up to board width in any solution, same for height **implicit_1.mzn**
* [x] Naive boundary optimization: we can set up worst scenario lower (tallest circuit to be placed) and upper bound (circuits stacked vertically in one column) **naive_boundaries.mzn**
* [x] Additional implicit contraint: for example area of the board will be bigger or equal to the sum of rectangles areas **implicit_2.mzn**
* [x] Convert constraints as much as possible to global contraints (pt 3 in project paper) (**cant really come up with a better formulation of constraints not using globals, globalizer doesnt give any hint too**)
* [x] Smart boundary optimization: idk about this
* [x] Board symmetry breaking: implement boolean representation nqueens-like, break the 4 symmetries: vertical flip, horizontal flip (pt 4 in project paper)
* [x] Value symmetry breaking: when placing circuits of the board, it doesn't matter which one is choosed first if there's 2+ having the same size
* [x] Simple constraint guiding: place highest element on (0, 0)
* [x] Search optimization: place big circuits first and try fitting smallest one then

#### model files and features
1. naive_model.mzn - basic contraints
2. naive_boundaries.mzn - naive boundaries based on worst case scenarios
3. smart_boundaries.mzn - boundaries fixed by greedy recursive solution
4. implicit_1.mzn - elements on rows (column) sum up to board width (height) in any solution
5. implicit_2.mzn - area of whole board is bigger or equal to sum of circuits areas
6. geometric_symmetry.mzn - remove board flippings by using boolean channeling
7. search_parameter.mzn - first fail, min first for both x and y
