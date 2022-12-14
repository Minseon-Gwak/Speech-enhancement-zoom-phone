# -*- coding: utf-8 -*-
"""Acoustic Improvement Bar Plot Example

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Xfu4rhw4HGF1cj3QMwOcps3AkXKX-YIH
"""

!pip install opensmile --quiet

import opensmile

LLD = opensmile.Smile(
    feature_set=opensmile.FeatureSet.eGeMAPSv02,
    feature_level=opensmile.FeatureLevel.LowLevelDescriptors)

FEATURE_NAMES = LLD.feature_names

import numpy as np
import plotly
import plotly.subplots
import plotly.graph_objects

!wget -q https://cmu.box.com/shared/static/dovpb587ojk72snc9rpmm99l2bf5l7xw --content-disposition --show-progress
!wget -q https://cmu.box.com/shared/static/66ew1ypwx7vyvku8fljsi4ezdflwlxsp --content-disposition --show-progress
!wget -q https://cmu.box.com/shared/static/75377grp7aak41459cpd8zndvfkg8jh7 --content-disposition --show-progress
!wget -q https://cmu.box.com/shared/static/1o9469rf0b4tv7f1nztgj1iclzc0h3eh --content-disposition --show-progress

C0 = np.load("src_clean.npy")
N0 = np.load("src_noisy.npy")
D0 = np.load("src_demuc.npy")
D1 = np.load("new_demuc.npy")

### Tabularize Mean Absolute Difference and Acoustic Improvement

MAE = lambda x, y: np.mean(np.abs(np.concatenate(x-y)), axis=0)
I = lambda mae_x, mae_y: (mae_y - mae_x) / mae_y

MAE_N0 = MAE( N0 , C0 )
MAE_D0 = MAE( D0 , C0 )
MAE_D1 = MAE( D1 , C0 )

I_D0_N0 = 100 * I( MAE_D0 , MAE_N0 )
I_D1_N0 = 100 * I( MAE_D1 , MAE_N0 )
I_D1_D0 = 100 * I( MAE_D1 , MAE_D0 )

np.mean(I_D0_N0), np.mean(I_D1_N0), np.mean(I_D1_D0)

### Show Acoustic Improvement Plot

fig = plotly.subplots.make_subplots(rows=1, cols=2, horizontal_spacing=0.01)

ORDER = np.argsort(I_D1_D0)
FEATURES = [FEATURE_NAMES[i].split("_")[0] for i in ORDER]

fig.append_trace(
    row=1, col=1,
    trace = plotly.graph_objects.Bar(
        y=FEATURES, 
        x=I_D0_N0[ORDER], 
        orientation='h', name="Baseline Improvement Over Noisy"))

fig.append_trace(
    row=1, col=1,
    trace = plotly.graph_objects.Bar(
        y=FEATURES, 
        x=I_D1_N0[ORDER], 
        orientation='h', name="Acoustic Improvement Over Noisy"))

fig.append_trace(
    row=1, col=2,
    trace = plotly.graph_objects.Bar( 
        x=I_D1_D0[ORDER], 
        orientation='h', name="Acoustic Improvement Over Baseline"))

HEIGHT = 290
WIDTH  = 370

fig.update_yaxes(showticklabels=False, col=2)
fig.update_layout(
    height = 3*HEIGHT, 
    width  = 3*WIDTH,
    legend=dict(orientation="h", yanchor="bottom"),
    margin = dict(l=0, r=0, t=0, b=0),
    bargap =0.50,
    xaxis1_range=[0,90],
    xaxis2_range=[0,40],
    xaxis1=dict(tickmode='linear', dtick=20),
    xaxis2=dict(tickmode='linear', dtick=10))

FONT_FAMILY = "Times New Roman"
FONT_SIZE   = 9

keys = list(locals().keys())
for l in keys:
    if l[:3] == 'fig':
        locals()[l].update_layout(font_family=FONT_FAMILY, font_size = 2*FONT_SIZE)

fig.show()

# fig.write_image("figures/figure_07.png")

