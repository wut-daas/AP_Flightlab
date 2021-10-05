#%%
#!/usr/bin/env python3
import os
import glob
import argparse
import platform
from posixpath import pardir

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DEG = 57.2957795

#plt.rcParams.update({'font.size': 20})
plt.rcdefaults()
plt.rcParams['axes.grid'] = True

os_name = platform.system()
if os_name == 'Windows':
    default_path = os.getcwd() + '\\results\\logs\\'
    cwd = os.getcwd()
    res_path = cwd + '\\results\\'
elif os_name == 'Linux':
    default_path = os.getcwd() + '/results/logs/'
    cwd = os.getcwd()
    res_path = cwd + '/results/'
else:
    print("Unexpected os")
    raise

list_of_files = glob.glob(default_path + '*')
default_path = max(list_of_files, key=os.path.getctime)

parser = argparse.ArgumentParser(description="Logging options")
parser.add_argument('--path', default=default_path, help='full path, def /results/logs/*newest*')
parser.add_argument('--save', dest='save', action='store_true')
parser.add_argument('--no-save', dest='save', action='store_false')
parser.set_defaults(save=False)
#args = parser.parse_args()
args, unknown = parser.parse_known_args()

df = pd.read_csv(args.path)
print("Loaded file " + args.path)

if args.save:
    if not os.path.isdir(res_path):
        os.mkdir(res_path)
    assert not os.path.isdir(res_path + os.path.basename(os.path.normpath(args.path))[:-4])
    save_path = res_path + os.path.basename(os.path.normpath(args.path))[:-4]
    os.mkdir(save_path)

fig, axs = plt.subplots(1,2)
fig.set_figheight(4)
fig.set_figwidth(15)
axs[0].plot(df.t, df.z.abs())
axs[0].set(xlabel='Czas [s]')
axs[0].set_title('Wysokość CG nad ziemią [m]')
axs[1].plot(df.y, df.x)
axs[1].set(ylabel='S-N', xlabel='W-E')
axs[1].set_title('Położenie w czasie [m,m]')
axs[1].plot(0, 0)

if args.save:
    plt.savefig(save_path + '/location.png')

fig, axs = plt.subplots(3)
fig.set_figheight(15)
fig.set_figwidth(15)
fig.suptitle('Euler orientacja [deg]')
axs[0].plot(df.t, df.pitch * DEG)
axs[0].set(ylabel='Pochylenie +nose up')
axs[1].plot(df.t, df.roll * DEG)
axs[1].set(ylabel='Przechylenie +right')
axs[2].plot(df.t, df.yaw * DEG)
axs[2].set(ylabel='Odchylenie +E')

for ax in axs.flat:
    ax.set(xlabel='Czas [s]')

for ax in axs.flat:
    ax.label_outer()

if args.save:
    plt.savefig(save_path + '/euler.png')

fig, axs = plt.subplots(3)
fig.set_figheight(15)
fig.set_figwidth(15)
fig.suptitle('Euler zmiana [rad/s]')
axs[0].plot(df.t, df.q)
axs[0].set(ylabel='Pochylenie zmiana +right')
axs[1].plot(df.t, df.p)
axs[1].set(ylabel='Przechylenie zmiana +nose up')
axs[2].plot(df.t, df.r)
axs[2].set(ylabel='Odchylenie zmiana 0°=N +E')

for ax in axs.flat:
    ax.set(xlabel='Czas [s]')

for ax in axs.flat:
    ax.label_outer()

if args.save:
    plt.savefig(save_path + '/euler_rate.png')

fig, axs = plt.subplots(3)
fig.set_figheight(5)
fig.set_figwidth(10)
fig.suptitle('Przyspieszenie [m/s^2]')
axs[0].plot(df.t, df.accx)
axs[0].set(ylabel='X +forward')
axs[1].plot(df.t, df.accy)
axs[1].set(ylabel='Y +right')
axs[2].plot(df.t, df.accz)
axs[2].set(ylabel='Z +down')

for ax in axs.flat:
    ax.set(xlabel='Czas [s]')

for ax in axs.flat:
    ax.label_outer()

if args.save:
    plt.savefig(save_path + '/acceleration.png')

fig, axs = plt.subplots(3)
fig.set_figheight(5)
fig.set_figwidth(10)
fig.suptitle('Prędkość earth frame [m/s]')
axs[0].plot(df.t, df.vx)
axs[0].set(ylabel='X +forward')
axs[1].plot(df.t, df.vy)
axs[1].set(ylabel='Y +right')
axs[2].plot(df.t, df.vz)
axs[2].set(ylabel='Z +down')

for ax in axs.flat:
    ax.set(xlabel='Czas [s]')

for ax in axs.flat:
    ax.label_outer()

if args.save:
    plt.savefig(save_path + '/velocity.png')
 
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

if args.save:
    plt.savefig(save_path + '/control.png')

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

if args.save:
    plt.savefig(save_path + '/pwm.png')

# %%
