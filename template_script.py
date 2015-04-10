#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# File: template_script.py
# @Author: Isaac Caswell
# @created: 21 February 2015
#
#===============================================================================
# DESCRIPTION:
#
# A template with my commenting conventions included, as well as generic_util, 
# which contains many useful functions, aand some common things I use, like 
# get_args and plotting with legends
#
#===============================================================================
# CURRENT STATUS: Works!  In progress.
#===============================================================================
# USAGE:
# import lolol as rofl
# print lolol(floop)
# 
#===============================================================================
# INPUT:
#
#===============================================================================
# OUTPUT:
#
#===============================================================================
# TODO: 
# -prepend 'private' methods with _
# -diagram program flow in this section
# -change all appropriate np.ndarrays to scipy sparse matrices


#standard modules
import numpy as np
import time
from collections import Counter
import heapq
import matplotlib.pyplot as plt


#third party modules
import generic_util as gutil


#===============================================================================
# CONSTANTS
#===============================================================================

#remember that full paths are needed for cron jobs and similar, so might as well
OUTPUT_FOLDER = '~/path/to/output/'
DATA_FOLDER = '~/path/to/data/'
K_OUTPUT_FILESTEM = "varying_k"

k = 20
ALPHA = .1

#===============================================================================
# FUNCTIONS
#===============================================================================

def get_args():
    """
    parses command line args"""
    parser = argparse.ArgumentParser() 
    parser.add_argument('--w', dest='LEARNED_W', type = str, default = '')
    parser.add_argument('--dir', dest='DIRECTED', default = False, action = 'store_true')

    return parser.parse_args()


#===============================================================================
# SCRIPT
#===============================================================================


#-------------------------------------------------------------------------------
# part (i) 

if __name__ == '__main__':
    print 'You are running this from the command line, so you must be testing it!'
    start_time = time.time()

    domain = range(k)
    f_1 = [i**2 for i in domain]
    f_2 = [np.sin(i) for i in domain]
    f_3 = [np.random.rand()*i for i in domain]


    colorprint("time to do computation: %s"%(time.time() - start_time))
    colorprint(time_string())



#===============================================================================
# CACHE RESULTS - useful especially if this is a script
#===============================================================================


"""
# save data to file for safety
with open(OUTPUT_FOLDER + K_OUTPUT_FILESTEM + '-' + time_string()) as f:
    for val in results:
        f.write(val + "\n")
"""

#===============================================================================
# PLOT RESULTS - again, useful mainly for scripts
#===============================================================================

p_1, = plt.plot(domain, f_1, 'ro')
p_2, = plt.plot(domain, f_2, 'b-')
p_3, = plt.plot(domain, f_3, 'k')

plt.xlabel("the domain is domainy")
plt.ylabel("value of silly functions")
plt.title("comparison of stuff")

plt.legend([p_1, p_2, p_3], ['exact', 'stuff', 'things'])

plt.show()

def convert_to_png(denoised_image):
    plt.imshow(denoised_image, cmap=plt.cm.gray)
    plt.show()



