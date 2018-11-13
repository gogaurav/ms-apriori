import numpy as np
from operator import itemgetter
from itertools import combinations

__author__ = 'Gourang'


def get_sup_cnt(trans):
    """
    Get the support count of all the elements present across the transactions
    in the input dataset file
    :param trans: <list> of transactions(<set>)
    :return: <dict> having item: support-count
    """
    itm_sup_cnt = {}
    for row in trans:
        for elem in row:
            itm_sup_cnt[elem] = itm_sup_cnt.get(elem, 0) + 1

    return itm_sup_cnt


def get_cand_sup_cnt(trans, cand_iset):
    """
    Get the support count of a candidate for frequent itemset
    :param trans: <list> of transactions(<set>)
    :param cand_iset: tuple
    :return: <dict> having cand_iset: support-count
    """
    cand_iset_sup_cnt = {}
    for row in trans:
        for cand in cand_iset:
            if set(cand).issubset(row):
                cand_iset_sup_cnt[cand] = cand_iset_sup_cnt.get(cand, 0) + 1
    return cand_iset_sup_cnt


def get_first_pass(min_sup, itm_sup):
    """
    First_pass(L) would be generated here. Here items with min support are passed
    in sorted order based on MIS. First item to be appended to the first_pass is the
    first item with its support greater than minimum support. Thereafter items, with
    MIS greater than MIS of the first item, is included
    :param min_sup: <list> of <tuple> having item and mis
    :param itm_sup: <dict> of item: support
    :return: <list> of <tuple> having first_pass items and their mis values
    """
    first_pass = []
    for i in range(len(min_sup)):
        if itm_sup[min_sup[i][0]] > min_sup[i][1]:
            first_pass.append((min_sup[i][0], min_sup[i][1]))
            break

    temp_mis_i = min_sup[i][1]
    for k in range(i + 1, len(min_sup)):
        if itm_sup[min_sup[k][0]] > temp_mis_i:
            first_pass.append((min_sup[k][0], min_sup[k][1]))

    return first_pass


def check_cant_be_tog(item_set, cant_be_tog):
    """
    All the items in a particular set in cant_be_tog should not be in item_set.
    If above condition holds, the item_set satisfy cannot-be-together constraint
    :param item_set: <list> of items in a frequent item set
    :param cant_be_tog: <list> of <list> of <list> items that cannot be together
                        like if all combinations of 1,2 and 3 should not
                        be together and similarly combinations of 4,5 and 6
                        then it ll be [[[1], [2], [3], [2,3]], [[4], [5], [6], [5,6]]
                        if the only requirement is combinations of size 2, then it ll
                        be [[[1], [2], [3]], [[4], [5], [6]]]
    :return: True if item_set satisfy the cannot-be-together constraint. otherwise False
    """
    for lset in cant_be_tog:
        comb_elem = list(combinations(lset, 2))
        comb_elem = [set(i[0] + i[1]) for i in comb_elem]
        comb_elem = [tuple(i) for i in comb_elem]
        comb_elem = set(comb_elem)
        for elem in comb_elem:
            if set(elem).issubset(set(item_set)):
                return False

    return True


def get_must_have(item_sets, must_have):
    """
    Filter out the item_sets (all the item_sets are of same size are passed) which
    satisfy must-have constraint i.e. any of the item in an itemset is present in
    must_have
    :param item_sets: <list> of <tuple> having frequent itemsets of same size
    :param must_have: <list> of must-have items
    :return: <list> of <tuple> of itemsets satisfying must-have constraint
    """
    isets_having_must_have = []
    for a_set in item_sets:
        for elem in a_set[:-1]:
            if elem in set(must_have):
                isets_having_must_have.append(a_set)
                break

    return isets_having_must_have


def level2_candidate_gen(first_pass, itm_sup, sup_dif_alwd):
    """
    All the combinations of size 2 of first_pass elements with first element having
    support greater than it's MIS and second element having support greater than 1st
    element's MIS is generated. Additionally, the support difference of the two elems
    should be less that sup diff constraint value to be included in candidates list.
    The logic is same as the standard level2_candidate_gen related to ms_apriori
    :param first_pass: <list> of <tuple> having first_pass elems and their MIS value
    :param itm_sup: <dict> of item: support
    :param sup_dif_alwd: <float> sup diff constraint value entered by the user or the
                         default value in the program
    :return: <list> of <tuple> having candidates of size 2
    """
    cand_size2 = []
    length = len(first_pass)
    for i in range(len(first_pass)):
        if itm_sup[first_pass[i][0]] >= first_pass[i][1]:
            for j in range(i + 1, length):
                if itm_sup[first_pass[j][0]] >= first_pass[i][1]:
                    sup_dif = abs(itm_sup[first_pass[j][0]] - itm_sup[first_pass[i][0]])

                    if sup_dif <= sup_dif_alwd:
                        cand_size2.append((first_pass[i][0], first_pass[j][0]))

    return cand_size2


def ms_candiate_gen(freq_iset, itm_sup, min_sup_dict, sup_dif_alwd):
    """
    k-size candidates are generated here where k is size of elems in freq_iset
    plus 1. The standard algorithm of ms_candidate_gen related to ms-apriori is
    followed here except 2 things: 1) I have sorted the freq_iset based on the
    first elem and breaking from the inner loop when the first element differs as
    there would be no further possibility of f1[0:len(f1)-1)] == f2[0:len(f2)-1)].
    2) I am also checking condition Ik-1 < I'k-1 as in the original algorithm. But
    due to sorting mentioned above, if the condition fails, I am still combining
    f2 and f1 instead of f1 and f2 such that the condition holds.
    :param freq_iset: <list> of <tuple> having frequent itemsets of size k-1
    :param itm_sup: <dict> of item: support
    :param min_sup_dict: <dict> having MIS values of all the items in dataset
    :param sup_dif_alwd: <float> sup diff constraint value entered by the user or the
                         default value in the program
    :return: <list> of <tuple> having candidates of size k
    """
    candidates = []
    freq_iset = sorted(freq_iset, key=itemgetter(0))
    length = len(freq_iset[0])
    for i in range(len(freq_iset)):
        f1 = freq_iset[i]
        for j in range(i + 1, len(freq_iset)):
            f2 = freq_iset[j]
            if f1[:-1] == f2[:-1]:
                if f1[-1] != f2[-1]:
                    sup_dif = abs(itm_sup[f2[-1]] - itm_sup[f1[-1]])
                    if sup_dif <= sup_dif_alwd:
                        if itm_sup[f1[-1]] < itm_sup[f2[-1]]:
                            cand_list = list(f1) + list([f2[-1]])
                        else:
                            cand_list = list(f2) + list([f1[-1]])
                        subsets_size_1less = list(combinations(cand_list, length))
                        for ssets in subsets_size_1less:
                            if (cand_list[0] in ssets)\
                                    or min_sup_dict[cand_list[1]] == min_sup_dict[cand_list[0]]:
                                if ssets not in set(freq_iset):
                                    break
                        else:
                            candidates.append(tuple(cand_list))
            elif f1[0] != f2[0]:
                break
    return candidates


def ms_apriori(trans, ls, beta, sup_dif_alwd, must_have, cant_be_tog, out_file_name):
    """
    Frequent itemsets are generated and written to the file. It follows the standard
    algorithm and uses level2-candidate-generation and ms-candidate-generation.
    Additional Features are Item Constraints. Must-have is applied at the
    end when all the freq itemsets have already been generated to avoid loss of
    frequent itemsets. Cannot-be-together constraint is applied while frequent
    itemsets are generated out of the candidates as an additional condition.
    :param trans: <list> of transactions(<set>)
    :param ls: <float> ls value entered by the user or the default value in program
    :param beta: <float> beta value entered by the user or the default value in program
    :param sup_dif_alwd: <float> sup diff constraint value entered by the user or the
                         default value in program
    :param must_have: <list> of must-have items
    :param cant_be_tog:
    :param out_file_name: The name of the output file having the final freq itemsets
    """
    cnt_freq_iset = 0
    all_freq_isets = []
    sup_str = ' #Sup: '
    must_have_len = len(must_have)
    trans_len = len(trans)
    itm_sup_cnt = get_sup_cnt(trans)
    itm_sup = {k: v / trans_len for k, v in itm_sup_cnt.items()}
    min_sup = []
    for k, v in itm_sup.items():
        """ mis = beta * item_support
            if mis is less than ls than ls, then mis = ls"""
        mis_temp = v * beta
        if mis_temp > ls:
            min_sup.append((k, mis_temp))
        else:
            min_sup.append((k, ls))

    min_sup = sorted(min_sup, key=itemgetter(1))
    min_sup_dict = dict(min_sup)
    first_pass = get_first_pass(min_sup, itm_sup)
    """Frequent Itemsets of size 1"""
    freq_iset = [(item[0], (sup_str + str(itm_sup_cnt[item[0]])))
                 for item in first_pass if itm_sup[item[0]] > item[1]]

    with open(out_file_name, 'w') as f:
        if must_have_len == 0:
            np.savetxt(f, freq_iset, fmt='%s')
        else:
            """Store freq itemsets in <list> of <list> to apply must-have at the end"""
            all_freq_isets = [freq_iset]
        cnt_freq_iset = cnt_freq_iset + len(freq_iset)
        len_sing_freq_iset = 1
        print("Status - Frequent Itemsets of following sizes have already been found:\n1", end='')
        cand_iset = level2_candidate_gen(first_pass, itm_sup, sup_dif_alwd)
        cand_iset_sup_cnt = get_cand_sup_cnt(trans, cand_iset)
        cand_iset_sup = {k: v / trans_len for k, v in cand_iset_sup_cnt.items()}
        freq_iset = []
        freq_iset_with_sup = []
        if len(cant_be_tog) == 0:
            for k, v in cand_iset_sup.items():
                if v > min_sup_dict[k[0]]:
                    freq_iset.append(k)
                    freq_iset_with_sup.append(k + (sup_str + str(cand_iset_sup_cnt[k]),))
        else:
            """additionally check whether candidate satisfy cannot-be-together constraint"""
            for k, v in cand_iset_sup.items():
                if v > min_sup_dict[k[0]] and check_cant_be_tog(k, cant_be_tog):
                    freq_iset.append(k)
                    freq_iset_with_sup.append(k + (sup_str + str(cand_iset_sup_cnt[k]),))

        len_freq_iset = len(freq_iset)
        while len_freq_iset > 0:
            if must_have_len == 0:
                np.savetxt(f, freq_iset_with_sup, fmt='%s')
            else:
                """Store freq itemsets in <list> of <list> to apply must-have at the end"""
                all_freq_isets = all_freq_isets + [freq_iset_with_sup]
            cnt_freq_iset = cnt_freq_iset + len_freq_iset
            len_sing_freq_iset = len(freq_iset[0])
            print(", {0}".format(len_sing_freq_iset), end='')  # for showing the status
            cand_iset = ms_candiate_gen(freq_iset, itm_sup,
                                        min_sup_dict, sup_dif_alwd)
            cand_iset_sup_cnt = get_cand_sup_cnt(trans, cand_iset)
            cand_iset_sup = {k: v / trans_len
                             for k, v in cand_iset_sup_cnt.items()}
            freq_iset = []
            freq_iset_with_sup = []
            if len(cant_be_tog) == 0:
                for k, v in cand_iset_sup.items():
                    if v > min_sup_dict[k[0]]:
                        freq_iset.append(k)
                        freq_iset_with_sup.append(k + (sup_str + str(cand_iset_sup_cnt[k]),))
            else:
                for k, v in cand_iset_sup.items():
                    if v > min_sup_dict[k[0]] and check_cant_be_tog(k, cant_be_tog):
                        freq_iset.append(k)
                        freq_iset_with_sup.append(k + (sup_str + str(cand_iset_sup_cnt[k]),))
            len_freq_iset = len(freq_iset)

        if must_have_len != 0:
            """Applying must-have constraint at the end 
            when all the freq itemsets have already been generated"""
            cnt_freq_iset = 0
            for isets_len_k in all_freq_isets:
                isets_having_must_have = get_must_have(isets_len_k, must_have)
                len_isets = len(isets_having_must_have)
                if len_isets != 0:
                    np.savetxt(f, isets_having_must_have, fmt='%s')
                    cnt_freq_iset = cnt_freq_iset + len_isets

    print("\n\nMS Apriori Algorithm run has successfully complete!"
          "\nFile {0} has the Frequent Itemsets\n\nMax size of frequent itemset"
          " found is {1} \nTotal no. of frequent itemsets generated "
          "is {2}".format(out_file_name, len_sing_freq_iset, cnt_freq_iset))
