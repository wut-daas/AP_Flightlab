#%%
#!/usr/bin/env python3
import os
import glob
import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#WARNING! On Windows

default_path = os.getcwd() + '\\results\\logs\\'
list_of_files = glob.glob(default_path + '*')
default_path = max(list_of_files, key=os.path.getctime)

parser = argparse.ArgumentParser(description="Logging options")
parser.add_argument('--path', default=default_path, help='full path, def /results/logs/*newest*')
parser.add_argument('--save', dest='save', action='store_true')
parser.add_argument('--no-save', dest='save', action='store_false')
parser.set_defaults(save=True)
#args = parser.parse_args()
args, unknown = parser.parse_known_args()

df = pd.read_csv(args.path)
print("Loaded file " + args.path)

fig, axs = plt.subplots(1,2)
fig.set_figheight(4)
fig.set_figwidth(15)
axs[0].plot(df.t, df.z.abs())
axs[0].set(xlabel='Czas [s]')
axs[0].set_title('Wysokość CG nad ziemią [m]')
axs[1].plot(df.y, df.x)
axs[1].set(ylabel='N-S', xlabel='W-E')
axs[1].set_title('Położenie w czasie [m,m]')

fig, axs = plt.subplots(3)
fig.set_figheight(15)
fig.set_figwidth(15)
fig.suptitle('Euler orientacja [deg]')
axs[0].plot(df.t, df.pitch)
axs[0].set(ylabel='Pochylenie')
axs[1].plot(df.t, df.roll)
axs[1].set(ylabel='Przechylenie')
axs[2].plot(df.t, df.yaw)
axs[2].set(ylabel='Odchylenie')

for ax in axs.flat:
    ax.set(xlabel='Czas [s]', ylabel='Stopnie [deg] <- CZY NA PEWNO DEG?') #FIXME

# Hide x labels and tick labels for top plots and y ticks for right plots.
for ax in axs.flat:
    ax.label_outer()
 
fig, axs = plt.subplots(2, 2)
fig.set_figheight(15)
fig.set_figwidth(15)
axs[0, 0].plot(df.t, df.xb)
axs[0, 0].set_title('Cyk Poch')
axs[0, 1].plot(df.t, df.xa, 'tab:orange')
axs[0, 1].set_title('Cyk Przech')
axs[1, 0].plot(df.t, df.xc, 'tab:green')
axs[1, 0].set_title('Coll')
axs[1, 1].plot(df.t, df.xp, 'tab:red')
axs[1, 1].set_title('Ped')

for ax in axs.flat:
    ax.set(xlabel='Czas [s]', ylabel='Kąty łopat [deg]')

fig, axs = plt.subplots(4)
fig.set_figheight(10)
fig.set_figwidth(10)
fig.suptitle('Sygnały sterowania [pwm]')
axs[0].plot(df.t, df.pwm1)
axs[0].set(ylabel='Aileron')
axs[0].set_xticklabels([])
axs[1].plot(df.t, df.pwm2)
axs[1].set(ylabel='Collective')
axs[1].set_xticklabels([])
axs[2].plot(df.t, df.pwm3)
axs[2].set(ylabel='Elevator')
axs[2].set_xticklabels([])
axs[3].plot(df.t, df.pwm4)
axs[3].set(ylabel='Tail', xlabel='Czas [s]')

# %%
