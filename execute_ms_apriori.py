from datetime import datetime
import ms_apriori as ap

__author__ = 'Gourang'

default_sup_dif_alwd = 1
default_beta = 0.5
default_ls = 0.01

ls = default_ls
beta = default_beta
sup_dif_alwd = default_sup_dif_alwd
must_have = []
cant_be_tog = []


def user_input(prompt_str, def_val):
    """
    Accept and validate user input for ls, beta and support difference allowed
    :param prompt_str: <str> Prompt message for input
    :return: The value entered by the user. If not, default value
    """
    while True:
        value = input(prompt_str).strip()
        if value:
            value = float(value)
            if 0 <= value <= 1:
                return value
            else:
                print("Enter correct value")
        else:
            return def_val


file_path = input("Enter Dataset File Name (File path if in diff directory): ")
out_file_name = input("\n**By Default, output file name would be of the form"
                      " output_inpFileName_...Enter below Output File name if"
                      " you want to change it**\nOutput File Name; Just Press"
                      " enter to Skip (txt file would be created): ")

if len(out_file_name) != 0:
    """Changing the file name to end with .txt, if it is not so"""
    if out_file_name.rfind('.') == -1:
        out_file_name = out_file_name + '.txt'
    elif out_file_name[out_file_name.rfind('.'):] != 'txt':
        out_file_name = out_file_name[:out_file_name.rfind('.')] + '.txt'

with open(file_path, 'r') as f:
    chg_def_para = input("\n**The default parameters are LS: {0}, Beta: {1} and"
                         " Supp diff: {2}**\nIf you want to change above values "
                         "or enter must-have/ cannot-be-together items,\nEnter y,"
                         " Otherwise n: ".format(default_ls, default_beta, default_sup_dif_alwd))
    if chg_def_para not in {'n', 'N'}:
        """Ask the user for custom values"""
        print("\n**Press enter to skip(if you want to take default values"
              " LS: 0.01, Beta:0.5 and Supp diff:0.05)**")
        fin_val_str = "**So, taken values are LS: "
        ls = user_input("Enter LS Value(for 1% enter 0.01, for 50% enter 0.5,"
                        " for 100% enter 1 and so on): ", default_ls)
        fin_val_str += str(ls) + ', '

        fin_val_str += "Beta: "
        beta = user_input("Enter Beta Value(Enter value between 0 and"
                          " 1): ", default_beta)
        fin_val_str += str(beta) + ', '

        fin_val_str += "Support Difference Constraint Value:"
        sup_dif_alwd = user_input("Enter Support Difference Constraint Value"
                                  "(for 1% enter 0.01, for 50% enter 0.5 and"
                                  " so on): ", default_sup_dif_alwd)
        print("{0} {1}".format(fin_val_str, str(sup_dif_alwd)))

        print("\n**Enter Item Constraints, Just press Enter to skip**")
        must_have = [int(i)
                     for i in input("Enter Must-Have item ids separated"
                                    " by space: ").strip().split(' ')
                     if len(i) != 0]
        print("Enter Cannot-Be-Together sets below in the form: 1, 2, 3; 45, 96, 81"
              "where cannot-be-together sets are separated by ';'\n and pairwise"
              "combinations within a set is considered that is all the combinations"
              "of size 2 of 1,2,3 and 4 cannot\n be together and similarly for 45, 96 and 81"
              "if you want to enter 2 and 3 together to form combinations of size 3,\n then"
              "enter 1, 2, 3, 2 3; 45, 96, 81 i.e additionally 2 and 3 separated by space:")
        cant_be_tog_temp = [[j for j in k.strip().split(',')]
                            for k in input('->').strip().split(';') if len(k) != 0]

        cant_be_tog = []
        for i in cant_be_tog_temp:
            elem_cant_be_tog = []
            for j in i:
                if ' ' in j:
                    elem_cant_be_tog.append([int(k) for k in j.strip().split(' ')])
                else:
                    elem_cant_be_tog.append([int(j.strip())])
            cant_be_tog.append(elem_cant_be_tog)

    start_time = datetime.now()  # start time of the ms_apriori algorithm
    trans = []
    single_trans_set = set()
    for line in f:
        single_trans_set = {int(i) for i in line.strip().split(' ') if i is not ''}
        trans.append(single_trans_set)  # storing the transactions as list of sets

file_name_index = file_path.rfind('\\')
if file_name_index == -1:
    file_name = file_path
else:
    file_name = file_path[file_name_index + 1:]

if len(out_file_name) == 0:
    out_file_name = "output_" + file_name[:file_name.rindex('.')] + '_ls_' + str(ls) + \
                    '_beta_' + str(beta) + '_sup_dif_' + str(sup_dif_alwd) + '.txt'

print("\nSuccessfully Read the Dataset in the input file. \nRunning MS_Apriori...")

ap.ms_apriori(trans, ls, beta, sup_dif_alwd, must_have, cant_be_tog, out_file_name)

print("Total time taken ~ {0}".format(datetime.now() - start_time))
