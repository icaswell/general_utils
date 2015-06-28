#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# File: generic_util.py
# @Author: Isaac Caswell
# @created: 21 February 2015
#
#===============================================================================
# DESCRIPTION:
#
# A file containing various useful functions I often find I have to write in my 
# scripts/have to look up from other files.  For instance, how to plot things 
# with legends, print things in color, and get command line arguments
#
#===============================================================================
# CURRENT STATUS: Works!  In progress.
#===============================================================================
# USAGE:
# import generic_util as gu
# gu.colorprint("This text is flashing in some terminals!!", "flashing")
# 
#===============================================================================
# CONTAINS:
# 
#-------------------------------------------------------------------------------
# COSMETIC:
#-------------------------------------------------------------------------------
# colorprint: prints the given text in the given color
# time_string:
#       returns a string representing the date in the form '12-Jul-2013' etc.
#       Handy naming of files.
#-------------------------------------------------------------------------------
# FOR (LARGE) FILES:
#-------------------------------------------------------------------------------
# randomly_sample_file: given the name of some unnecessarily large file that you
#       have to work with, original_fname, randomly samples it to have a given
#       number of lines.  This function is used for when you want to do some 
#       testing of your script on a pared down file first.
# scramble_file_lines:
#       randomly permutes the lines in the input file.  If the input 
#       file is a list, permutes all lines in the iput files in the asme way.
#       Useful if you are doing SGD, for instance.
# file_generator:
#       streams a file line by line, and processes that line as a list of integers.
# split_file: given the name of some unnecessarily large file that you have to 
#       work with, original_fname, this function splits it into a bunch of
#       smaller files that you can then do multithreaded operations on.
#
#===============================================================================
# TODO: 
# make general plotting function


#standard modules
import numpy as np
import time
from collections import Counter, defaultdict
import heapq
import matplotlib.pyplot as plt
import argparse
import shutil
import csv
import os
import re
import collections
import json


#===============================================================================
# FUNCTIONS
#===============================================================================


def add_header(fname, header):
    tmp_fname = 'loltempfile'
    if header[-1] != '\n':
        header += '\n'
    shutil.copyfile(fname, tmp_fname)
    with open(fname, 'w') as f:
        f.write(header)
        with open(tmp_fname, 'r') as g:
            for line in g:
                f.write(line)
    os.remove(tmp_fname)

 
def split_file(original_fname, output_dir_fname, n_splits = 15, delimitor = '\n'):
    """given the name of some unnecessarily large file that you have to work with, original_fname,
    this function splits it into a bunch of smaller files that you can then do multithreaded 
    operations on.

    Usage: split_file('./data/words_stream.txt', './data/words_stream_split_15')

    """
    if not os.path.exists(output_dir_fname):
        os.makedirs(output_dir_fname)

    lines_in_file = 0
    with open(original_fname, 'r') as f:
        for line in f:
            lines_in_file += 1

    lines_per_subfile = lines_in_file/n_splits

    with open(original_fname, 'r') as input_f:
        cur_split = 0
        output_f = open(output_dir_fname + '/split_%s'%cur_split, 'w')
        for i, line in enumerate(input_f):
            if i%lines_per_subfile == 0 and i:
                cur_split += 1
                output_f.close()
                output_f = open(output_dir_fname + '/split_%s'%cur_split, 'w')
            output_f.write(line)

        output_f.close()


def make_dev_train_sets(original_fname, names, percents, scramble = False, preserve_header = 0):
    """
    TODO: extend to take lists of files as input. 
    """
    assert(abs(sum(percents) - 1) < 1e-5)
    assert(len(names) == len(percents))

    if scramble:
        scramble_file_lines(original_fname, original_fname  + '.scrambled', keep_first_line_first = preserve_header)
        original_fname = original_fname  + '.scrambled'

    lines_in_file = 0
    header = None
    with open(original_fname, 'r') as f:
        for i, line in enumerate(f):
            if not i and preserve_header:
                header = line
            lines_in_file += 1

    lines_per_split = [p*lines_in_file for p in percents]
    lines_per_split = [np.ceil(n) for n in lines_per_split]

    with open(original_fname, 'r') as input_f:
        cur_split = 0
        output_f = open(names[0], 'w')
        i = 0
        if preserve_header:
            input_f.readline()
        for line in input_f:
            if i%lines_per_split[cur_split] == 0 and i:
                cur_split += 1
                i=0
                output_f.close()
                output_f = open(names[cur_split], 'w')
                if preserve_header:
                    output_f.write(header)
            output_f.write(line)
            i += 1

        output_f.close()


def randomly_sample_file(original_fname, output_fname, n_lines_to_output = 100, delimitor = '\n', preserve_first_line = 1):
    """given the name of some unnecessarily large file that you have to work with, original_fname,
    randomly samples it to have n_lines_to_output.  This function is used for when you want to
    do some testing of your script on a pared down file first.

    if original_fname is a list, then all files are sampled evenly  (the same lines are taken from 
    each one.)

    Usage: 
    randomly_sample_file(["./data/features.txt", "./data/target.txt"], ["./data/dev_features.txt", "./data/dev_target.txt"], 200)

    randomly_sample_file("data/clean_mail.tsv", "data/toy.tsv")

    """
    assert(type(original_fname) == type(output_fname))
    if isinstance(original_fname, list):
        assert(len(original_fname) == len(output_fname))
    else:
        original_fname = [original_fname]
        output_fname = [output_fname]


    lines_in_file = 0
    with open(original_fname[0], 'r') as f:
        for line in f:
            lines_in_file += 1

    line_idxs_to_output = range(lines_in_file)[1:] if preserve_first_line else np.arange(lines_in_file)
    np.random.shuffle(line_idxs_to_output)
    if preserve_first_line: line_idxs_to_output = [0] + line_idxs_to_output
    line_idxs_to_output = set(line_idxs_to_output[0:n_lines_to_output])

    for input_fname_i, output_fname_i in zip(original_fname, output_fname): 
        with open(input_fname_i, 'r') as input_i, open(output_fname_i, 'w') as output_i:
            for j, line in enumerate(input_i):
                if j in line_idxs_to_output:
                    output_i.write(line)


def scramble_file_lines(original_fname, output_fname, delimitor = '\n', keep_first_line_first = 0):
    """randomly permutes the lines in the input file.  If the input 
    file is a list, permutes all lines in the iput files in the same way.
    Useful if you are doing SGD, for instance.

    Usage: 
    scramble_file_lines([X_FILENAME, Y_FILENAME], ["./data/scrambled_features.txt", "./data/scrambled_target.txt"])

    """
    assert(type(original_fname) == type(output_fname))
    if isinstance(original_fname, list):
        assert(len(original_fname) == len(output_fname))
    else:
        original_fname = [original_fname]
        output_fname = [output_fname]


    lines = [] #lines[i] is a list of lines
    headers = []
    for input_i in original_fname:
        with open(input_i, 'r') as f:
            if keep_first_line_first:
                headers.append(f.readline())
            for i, line in enumerate(f):
                if len(lines) == i:
                    lines.append([])
                lines[i].append(line)

    np.random.shuffle(lines)

    for i, output_fname_i in enumerate(output_fname): 
        with open(output_fname_i, 'w') as output_i:
            if keep_first_line_first:
                output_i.write(headers[i])
            for line in lines:
                output_i.write(line[i])

def file_generator(fname):
    """streams a file line by line, and processes that line as a list of integers."""
    with open(fname, 'r') as f:
        for line in f:
            yield [int(v) for v in line.split()]


#-----------------------------------------------------------------------------------------            

def colorprint(message, color="rand"):
    message = unicode(message)
    """prints your message in pretty colors! So far, only a few color are available."""
    if color == 'none': print message
    if color == 'demo':
        for i in range(99):
            print '\n%i-'%i + '\033[%sm'%i + message + '\033[0m\t',
    print '\033[%sm'%{
        'neutral' : 99,
        'flashing' : 5,
        'underline' : 4,
        'red_highlight' : 41,
        'green_highlight' : 42,
        'orange_highlight' : 43,
        'blue_highlight' : 44,
        'magenta_highlight' : 45,
        'teal_highlight' : 46,
        'pink_highlight' : 46,        
        'pink' : 35,
        'purple' : 34,
        'peach' : 37,
        'yellow' : 93,   
        'teal' : 96,     
        'rand' : np.random.randint(1,99),
        'green?' : 92,
        'red' : 91,
        'bold' : 1
    }.get(color, 1)  + message + '\033[0m'


def time_string(precision='day'):
    """ returns a string representing the date in the form '12-Jul-2013' etc.
    intended use: handy naming of files.
    """
    t = time.asctime()
    precision_bound = 10 #precision == 'day'
    yrbd = 19
    if precision == 'minute':
        precision_bound = 16
    elif precision == 'second':
        precision_bound = 19
    elif precision == 'year':
        precision_bound = 0
        yrbd = 20
    t = t[4:precision_bound] + t[yrbd:24]
    t = t.replace(' ', '-')
    return t


def random_string_signature(length = 4):
    candidates = list("qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890")
    np.random.shuffle(candidates)
    return "".join(candidates[0:length])

def str_parse(s, to_lower = True):
    parse = re.split('[\s/\\\\,]', s)
    # below line fails on unicode
    # parse = [w.translate(string.maketrans("",""), string.punctuation) for w in parse]
    parse = [re.sub('[,<>\.;:!?\"]', '', w) for w in parse]
    parse = [w for w in parse if w]
    if to_lower:
        parse = [w.lower() for w in parse]
    return parse




# class BarGraph:
#     '''
#         Module to allow for bar graphs

#     '''
    
#     def __init__(self, title, ylabel='', xlabel=''):
#         self.clfs_to_f1 = defaultdict(list)
#         self.clfs = []
#         self.datasets = []
#         self.title = title
#         self.ylabel = ylabel
#         self.xlabel = xlabel
#         self.width = 0.08
#         self.colors = ('b','g','r','c','m','y','k','w')


#     def add_to_graph(self, dataset_name, clf_name, f1):
#         self.clfs_to_f1[clf_name].append(f1)
#         if clf_name not in self.clfs:
#             self.clfs.append(clf_name)
#         if dataset_name not in self.datasets:
#             self.datasets.append(dataset_name)

#     def plot(self):
#         ind = np.arange(len(self.datasets))
#         fig, ax = plt.subplots()
#         rects = [ax.bar(ind+self.width*i, self.clfs_to_f1[clf], self.width, color=self.colors[i%len(self.colors)]) for i, clf in enumerate(self.clfs)]
#         ax.set_ylabel(self.ylabel)
#         ax.set_title(self.title)
#         ax.set_xticks(ind+self.width*len(self.clfs))
#         ax.set_xticklabels( tuple(self.datasets) )
#         ax.legend(tuple([rect[0] for rect in rects]), tuple(self.clfs))
#         plt.show()

#     def sklearn_clf_rpt_parser(self, rpt):
#         line = re.findall('avg / total [\.\d\s]*', rpt)
#         if line == []:
#             return ()
#         return float(line[0].split()[5]) 

#===============================================================================
# TESTING SCRIPT
#===============================================================================

#-------------------------------------------------------------------------------
# part (i) 


if __name__ == '__main__':
    # print 'You are running this from the command line, so you must be demoing it!'


    # print str_parse("//THERE REALLY HASN'T BEEN ONE//ILLEGAL IMMIGRATION")
    # print str_parse("<DK>")
    # print str_parse("\\\\jobs\\\\ anyting else\\\\")  

    # print str_parse("service, installs systems into houses, condos, hotels")         
    # print str_parse("the war/so many deaths/")         
    # print str_parse("Finance/everybody is going broke, all small businesses are shuting down,big corporations are letting go of workers")                 
    # print str_parse(""""jobs"//""")

    # pc = PlotCatcher()
    # # exit(0)
    # def report_smartness(): 
    #     if np.random.random()<.8 :
    #         return 'still training...' 
    #     else:
    #         return """FINDINGS ON DATASET ./preprocessed_data/train/mip_personal_2_binarized_pp_train.tsv:
    #          precision    recall  f1-score   support
    #         avg / total       0.74      0.75      0.73      2009
    #         Accuracy: 0.749128919861"""

    # for i in range(19):
    #     print pc.catch(i**2, 'x squared')
    #     print pc.catch(i**3, 'x cubed', c='r--')  
    #     print pc.catch(report_smartness(), 'ml', pc.sklearn_clf_rpt_parser)      
    # pc.plotByIds(['x squared', 'x cubed'])
    # pc.plotByIds('ml')


    # colorprint("nyaan", color="demo")           

    # exit(0)
    # print os.listdir('../original_data/all_data')
    # fnames = ['current_industry', 'current_occupation', 'MIP_personal_1', 'MIP_personal_2', 'MIP_political_1', 'MIP_political_2', 'past_industry', 'past_occupation', 'PK_brown', 'PK_cheney', 'PK_pelosi', 'PK_roberts', 'terrorists']
    # fnames = ['current_industry_binarized', 'current_occupation_binarized', 'mip_personal_binarized', 'mip_political_binarized', 'past_industry_binarized', 'past_occupation_binarized', 'pk_brown_binarized', 'pk_cheney_binarized', 'pk_pelosi_binarized', 'pk_roberts_binarized', 'terrorists_binarized']
    # fnames =  ['industry_binarized', 'occupation_binarized']
    # for fname in fnames:
    fname = "mip_binarized"
    make_dev_train_sets('../original_data/all_data/%s.tsv'%fname, \
        ['../original_data/train/%s_train.tsv'%fname, 
        '../original_data/dev/%s_dev.tsv'%fname, 
        '../original_data/test/%s_test.tsv'%fname
        ], 
        [.75, .15, .1], 
        scramble = True)
    # add_header('data/clean_mail_test.tsv', 'Subject   Delivered-To    Received    From    To  X-GM-THRID  X-Gmail-Labels  importance  content')
    # add_header('data/clean_mail_train.tsv', 'Subject   Delivered-To    Received    From    To  X-GM-THRID  X-Gmail-Labels  importance  content')
    # randomly_sample_file("data/clean_mail.tsv", "data/toy_train.tsv", preserve_first_line = 1)
    # randomly_sample_file("data/clean_mail.tsv", "data/toy_test.tsv", preserve_first_line = 1)








