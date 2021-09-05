from typing import List, Union
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from math import ceil
import sys, os
import numpy as np

def plot_multi_vlsi(cwidth: List[int], cheight: List[int], cx: List[List[int]], cy: List[List[int]], 
                    rotations: List[List[bool]], save: Union[bool, str]=False, show: bool=True, title: str=""):
  """Plot vlsi solution

  Args:
      cwidth (List[int]): Array containing circuits widths
      cheight (List[int]): Array containing circuits heights
      cx (List[List[int]]): Array containing bottom-left x-axis corner position of each circuit
      cy (List[List[int]]): Array containing bottom-left y-axis corner position of each circuit
      rotations (List[List[int]], optional): Array containing if an element has been rotated
      save (Union[bool, str], optional): Save the plot to the specified path. Defaults to False and doesn't save anything.
      show (bool, optional): Show the plot. Defaults to True.
      title (str, optional): Title of plot. Defaults to empty.
  """
  try:
    cols = min(3, len(cx))
    rows = ceil(len(cx) / cols)

    _, axs = plt.subplots(rows, cols)
    solution = 0

    for ax in np.atleast_1d(axs).flatten():
      ax.set_ylim(0, max([cheight[i] + cy[solution][i] for i in range(len(cwidth))]))
      ax.set_xlim(0, max([cwidth[i] + cx[solution][i] for i in range(len(cwidth))]))
      ax.set_title(title)

      # load N colors
      colors = plt.cm.get_cmap("tab20", len(cwidth))
      for i, (w, h, x, y, r) in enumerate(zip(cwidth, cheight, cx[solution], cy[solution], rotations[solution])):
        text_x = x + 0.3
        text_y = y + 0.4
        text = str(i)
        
        # rotate if needed
        if r:
          w, h = h, w
          text += "r"

        # draw rectangle
        ax.add_patch(Rectangle((x, y), w, h, fill=True, facecolor=colors(i), linewidth=1.5, edgecolor="white"))
        # write element index and wether its rotated
        ax.text(text_x, text_y, text, fontsize="large", color="white")

      solution += 1
      if solution >= len(cx):
        break

    if show: plt.show()
    if save is not False: plt.savefig(save)
  except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

def plot_vlsi(cwidth: List[int], cheight: List[int], cx: List[int], cy: List[int], 
              rotations: List[bool] = None, save: Union[bool, str]=False, show: bool=True, title: str=""):
  """Plot vlsi solution

  Args:
      cwidth (List[int]): Array containing circuits widths
      cheight (List[int]): Array containing circuits heights
      cx (List[int]): Array containing bottom-left x-axis corner position of each circuit
      cy (List[int]): Array containing bottom-left y-axis corner position of each circuit
      rotations (List[int], optional): Array containing if an element has been rotated
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
    for i, (w, h, x, y, r) in enumerate(zip(cwidth, cheight, cx, cy, rotations)):
      text_x = x + 0.3
      text_y = y + 0.4
      text = str(i)
      
      # rotate if needed
      if r:
        w, h = h, w
        text += "r"
      
      # draw rectangle
      ax.add_patch(Rectangle((x, y), w, h, fill=True, facecolor=colors(i), linewidth=1.5, edgecolor="white"))
      # write element index and wether its rotated
      ax.text(text_x, text_y, text, fontsize="large", color="white")


    if show: plt.show()
    if save is not False: plt.savefig(save)
  except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)