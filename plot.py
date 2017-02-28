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


def plot(df, filename,name_matrix):
    plt.figure(figsize=(100,100))
    f, axn = plt.subplots(len(name_matrix)-1,len(name_matrix)-1, sharex='col',
            sharey='row')
    i = 0
    for ax_ in axn.flat:
        n_row = i // (len(name_matrix)-1)
        n_col = i % (len(name_matrix)-1)
        i = i+1
        if n_row < n_col:
            x = df[[name_matrix[n_row]]].values.squeeze()
            y = df[[name_matrix[n_col]]].values.squeeze()
            z = df[[name_matrix[-1]]].values.squeeze()
            cmap = cm.get_cmap(name='brg', lut=None)
            im = ax_.tricontour(y, x, z, 600, cmap=cmap);
        elif n_row == n_col:
            x = df[[name_matrix[n_row]]].values[0].squeeze()
            y = df[[name_matrix[n_col]]].values[0].squeeze()
            left, right = np.nanmin(x), np.nanmax(x)
            bottom, top = np.nanmin(y), np.nanmax(y)
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
    plt.savefig(filename, dpi=2000)


def main():
    name = sys.argv[1][:-4]

    data_file = open(sys.argv[1], 'r')
    data_matrix = np.loadtxt(data_file)

    # select data
    data_iv = data_matrix[:,range(0,16)]
    data_k = data_matrix[:,range(16,len(data_matrix[0]))]

    # split k mure vs k mlp
    data_k_mlp = data_k[:, ::2]
    data_k_mure = data_k[:, 1::2]

    # compute diff in pcm
    data_diff_k_pcm = abs(data_k_mure - data_k_mlp)/data_k_mlp *100000
    data_diff_k_pcm_sum = np.sum(data_diff_k_pcm, axis=1) / len(data_diff_k_pcm[0])


    data_diff_k_pcm_sum_with_index = np.column_stack((data_iv, np.asarray(data_diff_k_pcm_sum)))

    df = pd.DataFrame(data_diff_k_pcm_sum_with_index)
    name_file = open(name+'.nfo2', 'r')
    name_matrix = []
    for line in name_file:
        name_matrix.append(line[:-1])
    name_matrix.append('Delta')
    df.columns = name_matrix
    plot(df, 'myplot.png',name_matrix)

if __name__ == "__main__":
        main()
