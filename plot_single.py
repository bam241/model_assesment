#!/usr/bin/env python
import sys
import argparse
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
plt.rc('xtick', labelsize=1)
plt.rc('ytick', labelsize=1)
plt.rcParams.update({'font.size': 5})
import matplotlib.cm as cm
import matplotlib.patches as patches

from pyDOE import lhs
import numpy as np
import pandas as pd
from scipy import stats, integrate
import seaborn as sns

u235=[0.0056262, 0.0021849, 0.0126721, 0.0065894, 0.0130528, 0.0040823]
pu239=[0.1193791 ,0.0418123 ,0.1549278 ,0.1685029 ,0.0413255 ,0.1090484]
pu240 = [0.0275085 ,0.0085549 ,0.0031588 ,0.0181252 ,0.0021652 ,0.0176020]

t_u235 = [0.0007503 ,0.0174395 ,0.0154170 ,0.0111862]

t_pu239 = [0.0876754 ,0.0886187 ,0.0731851 ,0.0587584]

t_pu240 = [0.0224435 ,0.0085253 ,0.0105483 ,0.0016683]

min_max = [ 
        [0, 0.0198],
        [0,0.18],
        [0,0.04]]


def plot(df, filename,name_matrix):
    plt.figure(figsize=(100,100))
    f, axn = plt.subplots(len(name_matrix)-1,len(name_matrix)-1, sharex='col',
            sharey='row')
    i = 0
    for ax_ in axn.flat:
        n_row = i // (len(name_matrix)-1)
        n_col = i % (len(name_matrix)-1)
        i = i+1
        list_ = [0, 1, 2]
        if n_row < n_col:
            not_row_col = np.delete(list_, np.s_[n_col, n_row] ) 
            print(name_matrix[not_row_col[0]])
            df__ = df.loc[ 
                    (df[name_matrix[not_row_col[0]]] <
                        min_max[not_row_col[0]][1]) & 
                    (df[name_matrix[not_row_col[0]]] >
                        min_max[not_row_col[0]][0])
                    ]
            df_ = df__[[name_matrix[n_row],name_matrix[n_col],name_matrix[-1]]]
            x = df_[[name_matrix[n_row]]].values.squeeze()
            y = df_[[name_matrix[n_col]]].values.squeeze()
            z = df_[[name_matrix[-1]]].values.squeeze()
            cmap = cm.get_cmap(name='brg', lut=None)
            im = ax_.tricontour(y, x, z, 1000, cmap=cmap);
            x_ = []
            y_ = []
            if filename == '1000/10.png':
                if n_row == 0: y_ = u235
                if n_row == 1: y_ = pu239
                if n_row == 2: y_ = pu240
                if n_col == 0: x_ = u235
                if n_col == 1: x_ = pu239
                if n_col == 2: x_ = pu240
                ax_.plot(x_, y_,marker='x',linestyle=' ',  color='black' )

        elif n_row == n_col:
            x = df[[name_matrix[n_row]]].values.squeeze()
            y = df[[name_matrix[n_col]]].values.squeeze()
            left, right = np.nanmin(x), np.nanmax(x)
            bottom, top = np.nanmin(x), np.nanmax(x)
            ax_.set_ylim(left,right);
            ax_.set_xlim(bottom,top);
            width = right - left
            height = top - bottom
            width = right - left
            height = top - bottom
            p = patches.Rectangle(
                (left, bottom), width, height,
                fill=False, transform=ax_.transAxes, clip_on=False)
            ax_.add_patch(p)
            ax_.text(0.5*(left+right),
                    0.5*(bottom+top),
                    name_matrix[n_row],
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=5,
                    color='red')

        for item in ([ax_.title, ax_.xaxis.label, ax_.yaxis.label] +
                             ax_.get_xticklabels() + ax_.get_yticklabels()):
                item.set_fontsize(3)
    f.subplots_adjust(right=0.8)
    cbar_ax = f.add_axes([0.85, 0.15, 0.05, 0.7])
    plt.tick_params(axis='both', which='major', labelsize=5)
    plt.tick_params(axis='both', which='minor', labelsize=4)

    f.colorbar(im, cax=cbar_ax)
    plt.savefig(filename, dpi=700)

def main():
    name = sys.argv[1][:-4]

    data_file = open(sys.argv[1], 'r')
    data_matrix = np.loadtxt(data_file)
    # select data
    data_iv = data_matrix[:,range(0,16)]
    data_k = data_matrix[:,range(16,len(data_matrix[0]))]

    # split k mure vs k mlp
    data_k_mlp = data_k[:, 80]
    data_k_mure = data_k[:, 81]
    
    # compute diff in pcm
    data_diff_k_pcm = abs(data_k_mure - data_k_mlp)/data_k_mlp *100000

    data_diff_k_pcm_with_index = np.column_stack((data_iv, np.asarray(data_diff_k_pcm)))

    df = pd.DataFrame(data_diff_k_pcm_with_index)
    name_file = open(name+'.nfo', 'r')
    name_matrix = []
    for line in name_file:
        name_matrix.append(line.split()[3])
    name_matrix.append('Delta')
    df.columns = name_matrix
    df.drop('238U', axis=1, inplace=True)
    df.drop('237Np', axis=1, inplace=True)
    df.drop('238Pu', axis=1, inplace=True)
    df.drop('241Pu', axis=1, inplace=True)
    df.drop('242Pu', axis=1, inplace=True)
    df.drop('241Am', axis=1, inplace=True)
    df.drop('242Amm', axis=1, inplace=True)
    df.drop('242Cm', axis=1, inplace=True)
    df.drop('243Cm', axis=1, inplace=True)
    df.drop('244Cm', axis=1, inplace=True)
    df.drop('245Cm', axis=1, inplace=True)
    df.drop('246Cm', axis=1, inplace=True)
    name_matrix = np.delete(name_matrix,
            np.s_[1,2,3,6,7,8,9,10,11,12,13,14,15] )
    filename = name +'_35GWdt.png'
    plot(df, filename,name_matrix)

if __name__ == "__main__":
        main()
