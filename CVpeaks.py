__program__ = 'TBD'
__version__ = 'dev0.1'
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


def csv_in(filename):
    dataframe = pd.read_csv(filename)
    return dataframe


# initialize required variables
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

        elif cmd_in[0] == 'show_plot':
            show_plot(dataframe[x_col], dataframe[y_col])

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
            print('Loaded %s' % cmd_in[1])
            datafile = cmd_in[1]
            dataframe = csv_in(cmd_in[1])
            df_columns = len(dataframe.columns)

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
