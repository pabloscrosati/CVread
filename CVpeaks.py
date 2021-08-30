__program__ = 'TBD'
__version__ = 'dev0.2'
__author__ = 'Pablo Scrosati'

# import dependent packages
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.signal import find_peaks
import sys


# functions
# show data on plot
def show_plot(x_data, y_data):
    plt.plot(x_data, y_data)
    plt.show()

# read CSV file into program
def csv_in(filename):
    dataframe = pd.read_csv(filename)
    return dataframe

def baseline_als(y, lam, p , niter=10):
    L = len(y)
    D = sparse.diags([1,-2,1], [0,-1,-2], shape=(L,L-2))
    w = np.ones(L)
    for i in range(niter):
        W = sparse.spdiags(w, 0, L, L)
        Z = W + lam * D.dot(D.transpose())
        z = spsolve(Z, w*y)
        w = p * (y > z) + (1 - p) * (y < z)
    return z

# split a single data file into its up and down scans
# only for use with '''''''' FILL NAME HERE!
def cv_split(dataframe, x_col, scan=None, index=None):
    # find direction of original loop
    for i in range(len(dataframe[x_col])):
        if scan is None:
            if dataframe[x_col][i] < dataframe[x_col][i + 1]:
                # scan increases first
                scan = 1
                continue
            else:
                # scan decreases first
                scan = 2
                continue
        if scan == 1 and dataframe[x_col][i] > dataframe[x_col][i - 1]:
            continue
        elif scan == 1 and dataframe[x_col][i] < dataframe[x_col][i - 1]:
            index = i
            break

        if scan == 2 and dataframe[x_col][i] < dataframe[x_col][i - 1]:
            continue
        elif scan == 2 and dataframe[x_col][i] > dataframe[x_col][i - 1]:
            index = i
            break
    return index




# initialize required variables
# initial blank data file to check if one has been provided
datafile = ''

# main program, loops until 'exit' command
if __name__ == '__main__':
    while True:
        cmd_in = input('command: ').split()
        if not cmd_in:
            continue
        print('received command:', ' '.join(cmd_in))

        # exit logic
        if any(x == 'exit' for x in cmd_in):
            print('Exit command given, program will exit.')
            sys.exit()

        elif cmd_in[0] == 'fit_baseline':
            scan_index = cv_split(dataframe, x_col)
            print('Warning! This module only works if your CV data file only contains one scan.')


        # logic to plot data
        elif cmd_in[0] == 'show_plot':
            show_plot(dataframe[x_col], dataframe[y_col])

        # logic to read CSV file into program
        elif cmd_in[0] == 'csv_in':
            if len(cmd_in) < 2:
                print('CSV file not specified!')
                continue
            elif len(cmd_in) > 2:
                print('Too many arguments!')
                continue
            if cmd_in[1].split('.')[-1] != 'csv':
                print('Incorrect filetype!')
                continue
            datafile = cmd_in[1]
            dataframe = csv_in(cmd_in[1])
            df_columns = len(dataframe.columns)
            print('Loaded %s' % cmd_in[1])

            while True:
                print('Select the column containing the x-axis data:')
                for i in range(df_columns):
                    print('%s' % (i + 1), (dataframe.columns[i]).strip() + ', ', '(col %s)' % (i + 1))
                x_col = input('selection: ')
                if x_col == 'exit':
                    sys.exit()
                try:
                    int(x_col)
                except:
                    print('Invalid selection input!')
                    continue
                if int(x_col) < 1 or int(x_col) > (df_columns + 1):
                    print('Selection out of range!')
                    continue
                else:
                    break

            while True:
                print('Select the column containing the y-axis data:')
                for i in range(df_columns):
                    print('%s.' % (i + 1), (dataframe.columns[i]).strip() + ',', '(col %s)' % (i + 1))
                y_col = input('selection: ')
                if y_col == 'exit':
                    sys.exit()
                try:
                    int(y_col)
                except:
                    print('Invalid selection input!')
                    continue
                if int(y_col) < 1 or int(y_col) > (df_columns + 1):
                    print('Selection out of range!')
                    continue
                elif x_col == y_col:
                    print('x- and y-axis columns cannot be the same!')
                    continue
                else:
                    break

            x_col = dataframe.columns[int(x_col) - 1]
            y_col = dataframe.columns[int(y_col) - 1]

        # logic to show raw data and provide some description of the current working file
        elif cmd_in[0] == 'show_data':
            if len(cmd_in) != 1:
                print('Too many arguments!')
                continue
            if not datafile:
                print('Data file has not been set!')
                continue
            else:
                print('Data file in use: %s' % datafile)
                while True:
                    yes_no = input('Show data? (y/n)\n')
                    if yes_no == 'y':
                        print(dataframe.to_string(index=False))
                        break
                    elif yes_no == 'n':
                        break
                    elif yes_no == 'exit':
                        sys.exit()
                    else:
                        print('Invalid selection!')
