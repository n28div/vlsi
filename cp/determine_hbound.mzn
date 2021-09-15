% determines the height bound af the board by placing circuits in greedy way
function int: determine_hbound(int: n,
                               array[int] of int: widths, 
                               array[int] of int: heights, 
                               int: heightacc, 
                               int: widthacc,
                               int: it, 
                               int: count) = (
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

function int: greedy_height(int: N, % number of circuits
                            int: W, % width of the board
                            array[int] of int: widths, % ordered by width
                            array[int] of int: heights, % ordered by width
                            int: row_height, % initially = 0                            
                            int: height_acc, % initially = 0
                            int: width_acc, % initially = 0
                            int: it % iterator
                            ) = (
  if it = N then height_acc % base case -> return accumulated height
  else let { int: ew = widths[it], int: eh = heights[it] } in
     if width_acc + ew <= W then % circuit fits in the remaining width
       if row_height = 0 then % on a new "row"
         greedy_height(N, W, widths, heights, eh, height_acc + eh, width_acc + ew, it + 1)
       else % on existing "row", place the circuit
         greedy_height(N, W, widths, heights, row_height, height_acc, width_acc + ew, it + 1)
       endif
    else % add a new "row"
      greedy_height(N, W, widths, heights, 0, height_acc, 0, it)
    endif
  endif
);