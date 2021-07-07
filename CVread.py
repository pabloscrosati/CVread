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
comment_str, scan_range = '', []
potential_e, current_i, time_t = [], [], []

# Initialize classes
# These are mostly redundant for the current code, but may be useful later

# Class for experimental details
class exp_details:
    ref_type = 'Saturated Calomel Electrode'
    def __init__(self, exp_type, comment_lines, exp_comment, scan_rate, scan_number, lower_range, upper_range):
        self.exp_type = exp_type
        self.comment_lines = comment_lines
        self.exp_comment = exp_comment
        self.scan_rate = scan_rate
        self.scan_number = scan_number
        self.lower_range = lower_range
        self.upper_range = upper_range

# Command line option parsing
def cmd_parse(desc, verbose_flag=False, details_flag=False, split_flag=False):
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
    parser.add_argument('-v', '--verbose', help='print additional details while running, including additional error '
                                                'messages', action='store_true')
    parser.add_argument('--split', help='create new folder for each input file', action='store_true')
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

    # Set split flag if specified
    if args.split:
        split_flag = True

    # Return arguments
    return input_files, verbose_flag, details_flag, split_flag

# Logic for reading COR files
def read_COR(file_name):
    with open(file_name) as f:
        data = [line.rstrip() for line in f]
    return data

# Logic for determining scan direction and splitting cycles within a single COR file
def scan_logic(potential_list, cycle_flag=False, scandown=False, scanup=False, indecies=[]):
    for i in range(len(potential_list)):
        if i == 0:
            continue
        elif potential_list[i] < potential_list[i-1]:
            scandown = True
            continue
        elif potential_list[i] > potential_list[i-1]:
            scanup = True
            continue



if __name__ == '__main__':
    cmd_options = cmd_parse(__description__)
    input_files = cmd_options[0]
    verbose_flag = cmd_options[1]
    details_flag = cmd_options[2]
    split_flag = cmd_options[3]

    for i in input_files:
        # Check if input files exist and treat exceptions
        if not os.path.isfile(i):
            if verbose_flag == True:
                print('%s was not found, skipping.' % i)
            if i == input_files[-1] and False == valid_flag:
                print('No valid input files were found, exiting.')
                if verbose_flag == True:
                    print('Make sure your files are in the location specified.')
                sys.exit(2)
            pass
        else:
            valid_flag = True
            if verbose_flag == True:
                print('%s was found!' % i)

    # Read input COR files
    for i in input_files:
        data_file = read_COR(i)

        # Read experiment details and save to object if details requested
        if details_flag == True:
            if verbose_flag == True:
                print('Reading experimental parameters for %s' % i)
            exp_info = exp_details((data_file[2].split('\t'))[0].strip(), None, None, None, None, None, None)
            for x in data_file:
                line = x.lstrip().split(':')
                if line[0] == 'Comment Lines':
                    exp_info.comment_lines = int(line[1].strip())
                    line_index = data_file.index(x)
                    for n in range(exp_info.comment_lines):
                        comment_str = comment_str + (data_file[(line_index + n + 1)].split(':'))[1].strip() + ''
                    exp_info.exp_comment = comment_str
                    pass
                if line[0] == 'Scan Rate':
                    exp_info.scan_rate = line[1].strip()
                    pass
                if line[0] == 'Scan Number':
                    exp_info.scan_number = line[1].strip()
                    pass
                if line[0] == 'Potential #2':
                    scan_range.extend(line[1].strip())
                if line[0] == 'Potential #3':
                    scan_range.extend(line[1].strip())
                if len(scan_range) == 2:
                    exp_info.upper_range = max(scan_range)
                    exp_info.lower_range = min(scan_range)

        # Read data section
        for x in data_file:
            if x.strip() == 'End Comments':
                data_index = data_file.index(x) + 1
                break

        for i in range(data_index, len(data_file)):
            potential_e.append(float(data_file[i].strip().split()[0]))
            current_i.append(float(data_file[i].strip().split()[1]))
            time_t.append(float(data_file[i].strip().split()[2]))


    print(potential_e)
    print('\nProgram completed successfully!')
