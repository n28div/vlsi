% scan through the widths (which are ordered) and if it fits inside the board add the element to the 
% elem_acc, iterate until the board is full and no elements can be inserted anymore
function array[int] of int: elem_on_bottom(int: W, % board width
                                           array[int] of int: widths,   % widths and elements need to be
                                           array[int] of int: elements, % ordered by the same criteria
                                           int: it, 
                                           array[int] of int: elem_acc) = (
  % if an element fits then insert it
  if W - widths[it] >= 0 then 
    elem_on_bottom(W - widths[it], widths, elements, it + 1, elem_acc ++ [elements[it]])
  % else current element doesnt fit but next one might do
  elseif it < length(widths) then
    elem_on_bottom(W, widths, elements, it + 1, elem_acc)
  % no more elements fits, return the elements found so far
  else
    elem_acc
  endif
);