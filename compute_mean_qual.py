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


    print( sys.argv[1], " ", np.mean(data_diff_k_pcm_sum))


if __name__ == "__main__":
        main()
