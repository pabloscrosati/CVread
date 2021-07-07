__program__ = 'Scribner CView Data Reader'
__version__ = '1.0'
__author__ = 'Pablo Scrosati'
__features__ = '* Read multiple COR CV data files and export individual cyclic scans\n' \
               + '* Output experiment parameters'
__description__ = 'Read and interpret COR data files for further data analysis.\n' \
                  + 'Current Features:\n' + __features__

print(__program__ + ' v' + __version__ + '\nWritten by: ' + __author__ + '\n')

# Import packages
import sys, argparse, os.path, shutil, textwrap
from argparse import RawTextHelpFormatter

# Variables
valid_flag = True

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
def cmd_parse(desc, verbose_flag=False, details_flag=False, split_flag=False, override_flag=False):
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
    parser.add_argument('--override', help='override files and folders if they are already present', action='store_true')
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

    # Set override flag if specified
    if args.override:
        override_flag = True

    # Return arguments
    return input_files, verbose_flag, details_flag, split_flag, override_flag

# Logic for reading COR files
def read_COR(file_name):
    with open(file_name) as f:
        data = [line.rstrip() for line in f]
    return data

# Logic for determining scan direction and splitting cycles within a single COR file
def scan_logic(potential_list):
    indecies, cycle_flag, scandown, scanup = [], 0, False, False

    # Find initial scan direction
    for i in range(len(potential_list)):
        if scanup == True or scandown == True:
            break
        if i == 0:
            continue
        elif potential_list[i] < potential_list[i-1] and scandown == False and scanup == False:
            scandown = True
            continue
        elif potential_list[i] > potential_list[i-1] and scandown == False and scanup == False:
            scanup = True
            continue

    # Logic for detecting multiple scans depending on scan direction
    for i in range(len(potential_list)):
        if i == 0:
            continue
        elif scandown == True:
            if potential_list[i] < potential_list[i-1] and cycle_flag < 1:
                continue
            elif potential_list[i] > potential_list[i-1] and cycle_flag < 1:
                cycle_flag += 1
                continue
            elif potential_list[i] > potential_list[i-1] and cycle_flag == 1:
                continue
            elif potential_list[i] < potential_list[i-1] and cycle_flag == 1:
                indecies.append(str(i-1))
                cycle_flag = 0
                continue
        elif scanup == True:
            if potential_list[i] > potential_list[i-1] and cycle_flag < 1:
                continue
            elif potential_list[i] < potential_list[i-1] and cycle_flag < 1:
                cycle_flag += 1
                continue
            elif potential_list[i] < potential_list[i-1] and cycle_flag == 1:
                continue
            elif potential_list[i] > potential_list[i-1] and cycle_flag == 1:
                indecies.extend(str(i-1))
                cycle_flag = 0
                continue

    return indecies

def write_out(list_file, file_name):
    with open(file_name, 'w') as f:
        for item in list_file:
            f.write('%s\n' % item)


if __name__ == '__main__':
    cmd_options = cmd_parse(__description__)
    input_files = cmd_options[0]
    verbose_flag = cmd_options[1]
    details_flag = cmd_options[2]
    split_flag = cmd_options[3]
    override_flag = cmd_options[4]

    invalid_index = []

    for i in input_files:
        # Check if input files exist and treat exceptions
        if not os.path.isfile(i):
            if verbose_flag == True:
                print('%s was NOT found.' % i)
            valid_flag = False
        else:
            if verbose_flag == True:
                print('%s was found!' % i)

    if valid_flag == False and verbose_flag == True:
        print('\nOne or more input files were not found.')
        print('Make sure your files are in the location specified.')
        print('The program will not proceed.')
        sys.exit(2)
    elif valid_flag == False and verbose_flag == False:
        print('One or more input files were not found.')
        print('Make sure your files are in the location specified.')
        print('The program will not proceed.')
        sys.exit(2)

    # Read input COR files
    for i in input_files:
        scan_index = []
        comment_str, scan_range = '', []
        potential_e, current_i, time_t = [], [], []
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
                    scan_range.append(line[1].strip())
                if line[0] == 'Potential #3':
                    scan_range.append(line[1].strip())
                if len(scan_range) == 2:
                    exp_info.upper_range = max(scan_range)
                    exp_info.lower_range = min(scan_range)

        # Read data section
        for x in data_file:
            if x.strip() == 'End Comments':
                data_index = data_file.index(x) + 1
                break

        # Compile data
        for q in range(data_index, len(data_file)):
            potential_e.append(float(data_file[q].strip().split()[0]))
            current_i.append(float(data_file[q].strip().split()[1]))
            time_t.append(float(data_file[q].strip().split()[2]))

        scan_index = scan_logic(potential_e)

        if split_flag == True:
            if os.path.isdir(i.split('.')[0]) == False:
                if verbose_flag == True:
                    print(i.split('.')[0], 'directory was created.')
                os.mkdir(i.split('.')[0])
                if details_flag == True:
                    exp_text = 'File:\t\t\t' + i + '\nExperiment:\t\t' + exp_info.exp_type + '\nReference Electrode:\t' \
                        + exp_info.ref_type + '\nScan Range (V):\t\t' + str(exp_info.lower_range) + ' to ' \
                        + str(exp_info.upper_range) + ' vs. ' + exp_info.ref_type + '\nScan Rate (mV/s):\t' \
                        + str(exp_info.scan_rate) + '\nNumber of Scans:\t' + str(exp_info.scan_number) + '\n\nComments:\n' \
                        + textwrap.fill(exp_info.exp_comment, 80)
                    details_file = i.split('.')[0] + '_details.txt'
                    with open(os.path.join(i.split('.')[0], details_file), 'w') as outfile:
                        outfile.write(exp_text)
                    if verbose_flag == True:
                        print('Details file written to %s' % os.path.join(i.split('.')[0], details_file))

                # Logic for splitting replicate runs and formatting
                data_list, k = ['E (V),I (A/cm2),t (sec),t_norm (sec)'], 0
                for x in range(len(potential_e)):
                    if x == int(scan_index[k]):
                        write_out(data_list, os.path.join(i.split('.')[0], i.split('.')[0] + '_%s.csv' % str(k+1)))
                        data_list = ['E (V),I (A/cm2),t (sec),t_norm (sec)']
                        if k == (len(scan_index) -1):
                            data_list.append(str(potential_e[x]) + ',' + str(format(current_i[x], '.12f')) + ',' \
                                             + str(format(time_t[x], '.3f')) + ',' \
                                             + str(format(time_t[x] - time_t[int(scan_index[k])] if x >= int(scan_index[0]) \
                                           else time_t[x] - time_t[0], '.3f')))
                        else:
                            k += 1
                            data_list.append(str(potential_e[x]) + ',' + str(format(current_i[x], '.12f')) + ',' \
                                         + str(format(time_t[x], '.3f')) + ',' \
                                         + str(format(time_t[x] - time_t[int(scan_index[k-1])] if x >= int(scan_index[0]) \
                                                          else time_t[x] - time_t[0], '.3f')))
                    elif x < int(scan_index[k]):
                        data_list.append(str(potential_e[x]) + ',' + str(format(current_i[x], '.12f')) + ',' \
                                         + str(format(time_t[x], '.3f')) + ',' \
                                         + str(format(time_t[x] - time_t[int(scan_index[k-1])] if x > int(scan_index[0]) \
                                                      else time_t[x] - time_t[0], '.3f')))
                    elif x > int(scan_index[k]):
                        data_list.append(str(potential_e[x]) + ',' + str(format(current_i[x], '.12f')) + ',' \
                                         + str(format(time_t[x], '.3f')) + ',' \
                                         + str(format(time_t[x] - time_t[int(scan_index[k])] if x > int(scan_index[0]) \
                                                      else time_t[x] - time_t[0], '.3f')))
                    if x == (len(potential_e) - 1):
                        write_out(data_list, os.path.join(i.split('.')[0], i.split('.')[0] + '_%s.csv' % str(k + 2)))
                if verbose_flag == True:
                    print('%s data files written.' % exp_info.scan_number)

            elif os.path.isdir(i.split('.')[0]) and override_flag == False:
                print(i.split('.')[0], 'already exists!')
                print('"--split" was requested, but directories already exist. "--override" was not set.')
                print('To maintain data integrity, the program will not continue.')
                sys.exit(2)

            elif os.path.isdir(i.split('.')[0]) and override_flag == True:
                if verbose_flag == True:
                    print(i.split('.')[0], 'already exists! "--override" set. Will write over existing directory.')
                shutil.rmtree(i.split('.')[0])
                os.mkdir(i.split('.')[0])
                if details_flag == True:
                    exp_text = 'File:\t\t\t' + i + '\nExperiment:\t\t' + exp_info.exp_type + '\nReference Electrode:\t' \
                        + exp_info.ref_type + '\nScan Range (V):\t\t' + str(exp_info.lower_range) + ' to ' \
                        + str(exp_info.upper_range) + ' vs. ' + exp_info.ref_type + '\nScan Rate (mV/s):\t' \
                        + str(exp_info.scan_rate) + '\nNumber of Scans:\t' + str(exp_info.scan_number) + '\n\nComments:\n' \
                        + textwrap.fill(exp_info.exp_comment, 80)
                    details_file = i.split('.')[0] + '_details.txt'
                    with open(os.path.join(i.split('.')[0], details_file), 'w') as outfile:
                        outfile.write(exp_text)
                    if verbose_flag == True:
                        print('Details file written to %s' % os.path.join(i.split('.')[0], details_file))

                # Logic for splitting replicate runs and formatting
                data_list, k = ['E (V),I (A/cm2),t (sec),t_norm (sec)'], 0
                for x in range(len(potential_e)):
                    if x == int(scan_index[k]):
                        write_out(data_list, os.path.join(i.split('.')[0], i.split('.')[0] + '_%s.csv' % str(k+1)))
                        data_list = ['E (V),I (A/cm2),t (sec),t_norm (sec)']
                        if k == (len(scan_index) -1):
                            data_list.append(str(potential_e[x]) + ',' + str(format(current_i[x], '.12f')) + ',' \
                                             + str(format(time_t[x], '.3f')) + ',' \
                                             + str(format(time_t[x] - time_t[int(scan_index[k])] if x >= int(scan_index[0]) \
                                           else time_t[x] - time_t[0], '.3f')))
                        else:
                            k += 1
                            data_list.append(str(potential_e[x]) + ',' + str(format(current_i[x], '.12f')) + ',' \
                                         + str(format(time_t[x], '.3f')) + ',' \
                                         + str(format(time_t[x] - time_t[int(scan_index[k-1])] if x >= int(scan_index[0]) \
                                                          else time_t[x] - time_t[0], '.3f')))
                    elif x < int(scan_index[k]):
                        data_list.append(str(potential_e[x]) + ',' + str(format(current_i[x], '.12f')) + ',' \
                                         + str(format(time_t[x], '.3f')) + ',' \
                                         + str(format(time_t[x] - time_t[int(scan_index[k-1])] if x > int(scan_index[0]) \
                                                      else time_t[x] - time_t[0], '.3f')))
                    elif x > int(scan_index[k]):
                        data_list.append(str(potential_e[x]) + ',' + str(format(current_i[x], '.12f')) + ',' \
                                         + str(format(time_t[x], '.3f')) + ',' \
                                         + str(format(time_t[x] - time_t[int(scan_index[k])] if x > int(scan_index[0]) \
                                                      else time_t[x] - time_t[0], '.3f')))
                    if x == (len(potential_e) - 1):
                        write_out(data_list, os.path.join(i.split('.')[0], i.split('.')[0] + '_%s.csv' % str(k + 2)))
                if verbose_flag == True:
                    print('%s data files written.' % exp_info.scan_number)

        else:
            if details_flag == True:
                exp_text = 'File:\t\t\t' + i + '\nExperiment:\t\t' + exp_info.exp_type + '\nReference Electrode:\t' \
                           + exp_info.ref_type + '\nScan Range (V):\t\t' + str(exp_info.lower_range) + ' to ' \
                           + str(exp_info.upper_range) + ' vs. ' + exp_info.ref_type + '\nScan Rate (mV/s):\t' \
                           + str(exp_info.scan_rate) + '\nNumber of Scans:\t' + str(
                    exp_info.scan_number) + '\n\nComments:\n' \
                           + textwrap.fill(exp_info.exp_comment, 80)
                details_file = i.split('.')[0] + '_details.txt'
                with open(details_file, 'w') as outfile:
                    outfile.write(exp_text)
                if verbose_flag == True:
                    print('Details file written to %s' % details_file)

            # Logic for splitting replicate runs and formatting
            data_list, k = ['E (V),I (A/cm2),t (sec),t_norm (sec)'], 0
            for x in range(len(potential_e)):
                if x == int(scan_index[k]):
                    write_out(data_list, os.path.join(i.split('.')[0] + '_%s.csv' % str(k + 1)))
                    data_list = ['E (V),I (A/cm2),t (sec),t_norm (sec)']
                    if k == (len(scan_index) - 1):
                        data_list.append(str(potential_e[x]) + ',' + str(format(current_i[x], '.12f')) + ',' \
                                         + str(format(time_t[x], '.3f')) + ',' \
                                         + str(format(time_t[x] - time_t[int(scan_index[k])] if x >= int(scan_index[0]) \
                                                          else time_t[x] - time_t[0], '.3f')))
                    else:
                        k += 1
                        data_list.append(str(potential_e[x]) + ',' + str(format(current_i[x], '.12f')) + ',' \
                                         + str(format(time_t[x], '.3f')) + ',' \
                                         + str(
                            format(time_t[x] - time_t[int(scan_index[k - 1])] if x >= int(scan_index[0]) \
                                       else time_t[x] - time_t[0], '.3f')))
                elif x < int(scan_index[k]):
                    data_list.append(str(potential_e[x]) + ',' + str(format(current_i[x], '.12f')) + ',' \
                                     + str(format(time_t[x], '.3f')) + ',' \
                                     + str(format(time_t[x] - time_t[int(scan_index[k - 1])] if x > int(scan_index[0]) \
                                                      else time_t[x] - time_t[0], '.3f')))
                elif x > int(scan_index[k]):
                    data_list.append(str(potential_e[x]) + ',' + str(format(current_i[x], '.12f')) + ',' \
                                     + str(format(time_t[x], '.3f')) + ',' \
                                     + str(format(time_t[x] - time_t[int(scan_index[k])] if x > int(scan_index[0]) \
                                                      else time_t[x] - time_t[0], '.3f')))
                if x == (len(potential_e) - 1):
                    write_out(data_list, os.path.join(i.split('.')[0] + '_%s.csv' % str(k + 2)))
            if verbose_flag == True:
                print('%s data files written.' % exp_info.scan_number)

    print('\nProgram process has reached the end.')
