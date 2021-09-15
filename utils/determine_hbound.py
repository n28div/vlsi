from typing import List, Union

def greedy_height(N: int,  # number of circuits
                  W: int,  # width of the board
                  widths: List[int],  # ordered by width
                  heights: List[int],  # ordered by height
                  row_height: int = 0,
                  height_acc: int = 0,
                  width_acc: int = 0,
                  it: int = 1):
  if (it == N):
    return height_acc  # base case, return accumulated height
  else:
    ew = widths[it]
    eh = heights[it]
    if (width_acc + ew <= W):
      if (row_height == 0):
        return greedy_height(N, W, widths, heights, eh, height_acc + eh, width_acc + ew, it + 1)
      else:
        return greedy_height(N, W, widths, heights, row_height, height_acc, width_acc + ew, it + 1)
    else:
      return greedy_height(N, W, widths, heights, 0, height_acc, 0, it)

