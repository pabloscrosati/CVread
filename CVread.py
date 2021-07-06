__program__ = 'Scribner CView Data Reader'
__version__ = '0.1'
__author__ = 'Pablo Scrosati'
__features__ = '* Read multiple COR CV data files and export individual cyclic scans\n' \
               + '* Output experiment parameters'
__description__ = 'Read and interpret COR data files for further data analysis.\n' \
                  + 'Current Features:\n' + __features__

print(__program__ + ' v' + __version__ + '\nWritten by: ' + __author__ + '\n')

# Import packages
import sys, argparse, os.path
from argparse import RawTextHelpFormatter

# Dependent variable
valid_flag = False


# Command line option parsing
def cmd_parse(desc, verbose_flag=False, details_flag=False):
    # Check if arguments were provided
    argv = sys.argv[1:]
    if len(argv) < 1:
        print('No command line arguments specified, exiting.')
        print('Use option "-h" for help.')
        sys.exit(2)

    # Parser settings and help message text
    parser = argparse.ArgumentParser(description=desc, epilog='The program will not execute because the help option '
                                                              'was requested. To proceed, remove the help "-h, --help" '
                                                              'option.', formatter_class=RawTextHelpFormatter)
    # Files argument is stored as a list
    parser.add_argument('-f', '--files', metavar='xxx.cor', dest='input_file', help='specify input file(s)', nargs='+')
    parser.add_argument('--details', help='store additional experimental details to file', action='store_true')
    parser.add_argument('-v', '--verbose', help='print additional details while running', action='store_true')
    args = parser.parse_args()

    # Check if files were provided and set list variable
    if args.input_file is None:
        print('No input files specified. This program requires at least 1 COR file. Exiting.')
        print('Use option "-h" for help.')
        sys.exit(2)
    else:
        input_files = args.input_file

    # Set verbose flag if specified
    if args.verbose:
        verbose_flag = True

    # Set details flag if specified
    if args.details:
        details_flag = True

    # Return arguments
    return input_files, verbose_flag, details_flag


if __name__ == '__main__':
    cmd_options = cmd_parse(__description__)
    input_files = cmd_options[0]
    verbose_flag = cmd_options[1]
    details_flag = cmd_options[2]

    for i in input_files:
        # Check if input files exist and treat exceptions
        if not os.path.isfile(i):
            print('%s was not found, skipping.' % i)
            if i == input_files[-1] and False == valid_flag:
                print('No valid input files were found, exiting.')
                print('Make sure your files are in the location specified.')
                sys.exit(2)
            pass
        else:
            valid_flag = True
            print('%s was found!' % i)

    print('\nProgram completed successfully!')
