from typing import List, Union
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import sys, os

def plot_vlsi(cwidth: List[int], cheight: List[int], cx: List[int], cy: List[int], save: Union[bool, str]=False, show: bool=True, title: str=""):
  """Plot vlsi solution

  Args:
      cwidth (List[int]): Array containing circuits widths
      cheight (List[int]): Array containing circuits heights
      cx (List[int]): Array containing bottom-left x-axis corner position of each circuit
      cy (List[int]): Array containing bottom-left y-axis corner position of each circuit
      save (Union[bool, str], optional): Save the plot to the specified path. Defaults to False and doesn't save anything.
      show (bool, optional): Show the plot. Defaults to True.
      title (str, optional): Title of plot. Defaults to empty.
  """
  try:
    _, ax = plt.subplots()
    ax.set_ylim(0, max([cheight[i] + cy[i] for i in range(len(cwidth))]))
    ax.set_xlim(0, max([cwidth[i] + cx[i] for i in range(len(cwidth))]))
    ax.set_title(title)

    # load N colors
    colors = plt.cm.get_cmap("tab20", len(cwidth))
    for i, (w, h, x, y) in enumerate(zip(cwidth, cheight, cx, cy)):
      # draw rectangle
      ax.add_patch(Rectangle((x, y), w, h, fill=True, facecolor=colors(i)))

    if show: plt.show()
    if save is not False: plt.savefig(save)
  except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)