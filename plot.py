#!/usr/bin/env python
import sys
import argparse

import matplotlib
matplotlib.use('Agg')

from pyDOE import lhs
import numpy as np
import pandas as pd
from scipy import stats, integrate
import seaborn as sns





def main():


    data_file = open(sys.argv[1], 'r')
    data_matrix = np.loadtxt(data_file)
    print(len(data_matrix))


if __name__ == "__main__":
        main()
