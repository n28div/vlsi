## CP

### Python-stuff
* [x] Preprocess text files and feed them to minizinc model
* [x] Visualize results using plots 
* [x] export plots to use in the report
- [ ]  Configure to batch run models with all instances and record statistics
- [ ]  Graph the statistics

### Minizinc models
* [x] Naive model (pt 1 in project paper) **naive_model.mzn**
* [x] Implicit contraint (pt 2 in project paper): elements on rows should sum up to board width in any solution, same for height **implicit_1.mzn**
* [x] Naive boundary optimization: we can set up worst scenario lower (tallest circuit to be placed) and upper bound (circuits stacked vertically in one column) **naive_boundaries.mzn**
- [ ] Additional implicit contraint: for example area of the board will be bigger or equal to the sum of rectangles areas
- [ ] Convert constraints as much as possible to global contraints (pt 3 in project paper)
- [ ] Smart boundary optimization: idk about this
- [ ] Board symmetry breaking: implement boolean representation nqueens-like, break the 4 symmetries: main diagonal, secondary diagonal, vertical flip, horizontal flip (pt 4 in project paper)
- [ ] Value symmetry braking: when placing circuits of the exam shape it doesn't matter which one is choosed first
- [ ] Search optimization: place big circuits first and try fitting smallest one then
- [ ] Minimization dual idea: minimize the difference *board_area - circuits_summed_area*
