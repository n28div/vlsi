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
