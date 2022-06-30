import json
import seaborn as sns
import pandas as pd

import matplotlib.pyplot as plt

# this is the setting for plots for research paper and articles.
# %matplotlib inline
# %config InlineBackend.figure_format = 'retina'

# Set the global font to be DejaVu Sans, size 10 (or any other sans-serif font of your choice!)
plt.rc('font',**{'family':'sans-serif','sans-serif':['DejaVu Sans'],'size':16})

# Set the font used for MathJax - more on this later
plt.rc('mathtext',**{'default':'regular'})

# Set the style for seaborn 
plt.style.use(['seaborn-whitegrid', 'seaborn-paper'])

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'large',
         'axes.labelsize': 'large',
         'axes.titlesize': 'large',
         'xtick.labelsize': 'large',
         'ytick.labelsize': 'large'
         }

pylab.rcParams.update(**params)

import seaborn as sns
sns.set_context(rc=params)

def stylize_axes(ax, title):
    """
    Stylize the axes by removing ths spines and ticks. 
    """
    # removes the top and right lines from the plot rectangle
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.xaxis.set_tick_params(top=False, direction='out', width=1)
    ax.yaxis.set_tick_params(right=False, direction='out', width=1)

    # Enforce the size of the title, label and tick labels
    ax.set_xlabel(ax.get_xlabel(), fontsize='large')
    ax.set_ylabel(ax.get_ylabel(), fontsize='large')

    ax.set_yticklabels(ax.get_yticklabels(), fontsize='medium')
    ax.set_xticklabels(ax.get_xticklabels(), fontsize='medium')

    ax.set_title(title, fontsize='large')

def save_image(fig, title):
    """
    Save the figure as PNG and pdf files
    """
    if title is not None:
        fig.savefig(title+".png", dpi=300, bbox_inches='tight', transparent=True)
        fig.savefig(title+".pdf", bbox_inches='tight')

def figure_size(fig, size):
    fig.set_size_inches(size)
    fig.tight_layout()
    
def resadjust(ax, xres=None, yres=None):
    """
    Send in an axis and fix the resolution as desired.
    """

    if xres:
        start, stop = ax.get_xlim()
        ticks = np.arange(start, stop + xres, xres)
        ax.set_xticks(ticks)
    if yres:
        start, stop = ax.get_ylim()
        ticks = np.arange(start, stop + yres, yres)
        ax.set_yticks(ticks)

with open("jane_doe_diffs_legalbert-large-1.7M-2.json", "r") as f:
    jane_doe_lb = json.load(f)
with open("jane_doe_diffs_bert-large-uncased.json", "r") as f:
    jane_doe_b = json.load(f)
with open("jane_doe_diffs_legalbert-large-1.7M-2_negative.json", "r") as f:
    jane_doe_lb_negjd = json.load(f)
with open("jane_doe_diffs_bert-large-uncased_negative.json", "r") as f:
    jane_doe_b_negjd = json.load(f)


import matplotlib.pyplot as plt

df = pd.DataFrame.from_dict({
    "Model" : (["bert"] * len(jane_doe_b)) + (["pol-bert"] * len(jane_doe_lb)) +  (["bert"] * len(jane_doe_b_negjd)) + (["pol-bert"] * len(jane_doe_lb_negjd)),
    "Jane Doe Score" : jane_doe_b + jane_doe_lb + jane_doe_b_negjd + jane_doe_lb_negjd,
    "Sample Type" : ["Court Case\n(Jane Doe)"] * (len(jane_doe_b) + len(jane_doe_lb)) + ["Bios"] * (len(jane_doe_b_negjd) + len(jane_doe_lb_negjd))
})

#swarm_plot = sns.barplot(x="Model", y="Jane Doe Score", data=df)
swarm_plot = sns.factorplot(x = 'Sample Type', y='Jane Doe Score',
               hue = 'Model', data=df, kind='bar')
#fig = swarm_plot.get_figure()
plt.xticks(rotation=20)

save_image(swarm_plot.fig, "janedoe")
import numpy as np
print(np.mean(jane_doe_b) - np.mean(jane_doe_b_negjd))
print(np.mean(jane_doe_lb) - np.mean(jane_doe_lb_negjd))