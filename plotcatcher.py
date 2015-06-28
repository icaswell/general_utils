#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# File: plotcatcher.py
# @Author: Isaac Caswell
# @created: 21 June 2015
#
#===============================================================================
# DESCRIPTION:
#
# A module to easliy make and save plots of any subset of variables from a
# script.  As an example, one can wrap a function call in the function 
# Plotcatcher.catch(), and plotcatcher will automatically record every value 
# recorded from a call to that function, and save a plot of that value over 
# time.  Users can specify custom functions to tell plotcatcher what to catch 
# from the function output.  Uses matplotlib.pyplot functionality.
#
#===============================================================================
# CURRENT STATUS: Seems to work, little testing has been done, however
#===============================================================================
# USAGE:
# [for more detailed examples look at if __name__="__main__" clause]
#
# import numpy as np
# from plotcatcher import PlotCatcher
#
# pc = Plotcatcher()
# 
# for i in range(20):
#     print pc.catch(i**2, 'x squared')
#     print pc.catch(i**3, 'x cubed', c='r--')  
# 
# pc.plotByIds(['x squared', 'x cubed'], save=True)
#
#===============================================================================
# TODO: 
# ?
# ===============================================================================

import matplotlib.pyplot as plt
import time

class PlotCatcher:
    """ A module to allow you to automatically plot things from your code with minimal effort.
    """
    def __init__(self, save_dir='./'):
        if save_dir[-1] != '/':
            save_dir += '/'
        self._save_dir = save_dir

        self.plots = defaultdict(list)

        # self._gb__plot_attributes are global attributes that are called for any plot
        self._gb_plot_attributes = {}
        # self._plot_attributes are attributes of specific plots
        self._plot_attributes = {}        

        # self.pid_colors is a mapping of pid to the color it wants to be plotted in
        self.pid_colors = {}
        self.default_parser = lambda tup, pid: (self._prev_i(pid), tup)

    def catch(self, output_tuple, pid = 'Main Plot', tuple_parser = None, c = ''):
        """
        Catches and stores a set of values (for instance, from the output of a function) and returns them.
        i.e. instead of writing

        >>> foo = dree(weird)

        you can write 

        >>> pc = PlotCatcher()
        >>> foo = pc.catch(dree(weird))


        @param output_tuple: a tuple of things you want to plot.  (Doesn't need to be a tuple;
              this depends on your tuple_parser.)
        @param str pid: the id of the plot who you are adding things to
        @param tuple_parser: a fuction of the tuple which outputs a tuple of 
                (domain, function_value),
                or () if the input tuple should be ignored.
        @param str c: the color/style of the plot of this caught value, e.g. 'b', 'ro', 'k--', etc.  There can only be one color per plot id.
        """
        if tuple_parser is None:
            tuple_parser = self.default_parser

        tup = tuple_parser(output_tuple, pid)
        if tup: #ignore empty tuples
            self.plots[pid].append(tup)

        if c: #if no c is specified, the default colorscheme is used
            self.pid_colors[pid] = c
        return output_tuple

    def set_pid_colors(self, pids, colors):
        if isinstance(pids, str): pids = [pids]

        for pid, c in zip(pids, colors):
            if pid not in self.plot_colors:
                print "warning: plot with pid %s doesn't yet exist"%pid
            self.plot_colors[pid] = c


    def set_plot_attributes(self, pids, attributes):
        """
        Sets attributes (title, x limits, etc) of the plot associated with 
        this particular pid. Note that this has precedence over the global
        attributes: calling this function before or after
        set_default_attributes will cause these
        attribute to be used instead of the global ones

        @param str/list pids: a string representing the pid whose attributes 
                you are setting, OR a list of the pids of the plots whose 
                attributes you are setting
        @param dict attributes: a dict mapping attributes to their values, e.g.
                {'title': 'my best graph', 'xlim': (0, 1)}

        """

        if isinstance(pids, str): pids = [pids]
        for pid in pids:
            self._plot_attributes[pid] = dict(attributes)


    def set_default_attributes(self, attributes):
        """
        Sets default attributes (title, x limits, etc) of the plot associated
        with all pids. 
        """
        assert(isinstance(attributes, dict))
        self._gb_plot_attributes.update(attributes)


    def plot_all(self, save=False, plot=True, file_label=''):
        """ 
        @param str file_label: this is appended to name of the file 
            that the plot is saved to. A smart exampe would be a 
            string identifying the hyperparameters of the run.
        """
        for pid, vals in self.plots.iteritems():
            self.plotByIds([pid], save=save, plot=plot, file_label = file_label)

    def plotByIds(self, pids, save=False, plot=True, file_label=''):
        """plots on a single plots associated with the list 
        of pids.  if pids is a string, just that one graph is plotted.
        """
        if isinstance(pids, str): pids = [pids]
        plt_objs = []
        for pid in pids:
            domain, values = zip(*self.plots[pid])
            if pid in self.pid_colors:
                pi, = plt.plot(domain, values, self.pid_colors[pid])
            else:
                pi, = plt.plot(domain, values)                
            plt_objs.append(pi)

        plt.title(", ".join(pids)) #This will be overwritten if another title is supplied
        legend_loc = self._set_attributes(pids[0])
        plt.legend(plt_objs, pids, loc=legend_loc)

        if save:
            if file_label: file_label = '_' + file_label
            save_fname = self._save_dir \
                    + "+".join([re.sub(' ', '_', pid) for pid in pids]) + '_' \
                    + self._timestring() \
                    + file_label + '.png'
            print save_fname
            plt.savefig(save_fname)
        if plot:
            plt.show()

    def sklearn_clf_rpt_parser(self, rpt, pid):
        """
        A parser which picks up the f1 score from the sklearn
        classification report
        """
        line = re.findall('avg / total [\.\d\s]*', rpt)
        if line == []:
            return ()
        return (self._prev_i(pid), float(line[0].split()[5]))

    #==================================================================
    # private functions

    def _set_attributes(self, pid):
        """
        sets the attributes of the plot for the given pid.  Returns the 
        location of the legend for that plot
        """

        attrib = dict(self._gb_plot_attributes)
        attrib.update(dict(self._plot_attributes.get(pid, {})))

        if 'title' in attrib:
            plt.title(attrib['title'])
        if 'xlim' in attrib:
            plt.xlim(*attrib['xlim'])
        if 'ylim' in attrib:
            plt.ylim(*attrib['ylim']) 
        if 'x_label' in attrib:
            plt.x_label(*attrib['x_label'])
        if 'y_label' in attrib:
            plt.y_label(*attrib['y_label'])

        #note: options for legend loc include "lower left", "left", "center", etc, 
        return attrib.get('legend_loc', 'best')

    def _prev_i(self, pid):
        return self.plots[pid][-1][0] + 1 if self.plots[pid] else 0


    def _timestring(self, precision='day'):
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



if __name__=="__main__":
    from collections import defaultdict; import numpy as np; import re


        
    pc = PlotCatcher()

    #=================================================================
    # basic example
    for i in range(20):
        print pc.catch(i**2, 'x squared')
        print pc.catch(i**3, 'x cubed', c='r--')  

    pc.plotByIds(['x squared', 'x cubed'], save=True)

    #=================================================================
    # example to simulate a machine learning script
    def report_smartness():
        """A toy function to simulate
        a function that ouputs a lot of random stuff before 
        telling you what you want
        """ 
        if np.random.random()<.8 :
            return 'still training...' 
        else:
            return """FINDINGS ON DATASET ./preprocessed_data/train/mip_personal_2_binarized_pp_train.tsv:
             precision    recall  f1-score   support
            avg / total       0.74      0.75      %s      2009
            Accuracy: 0.749128919861"""%np.random.random()

    for i in range(19):
        print pc.catch(report_smartness(), 'ml', pc.sklearn_clf_rpt_parser)

    #=================================================================
    # example to change attributes of plots

    pc.plotByIds('ml')

    pc.set_default_attributes({'title': 'my great plot'})
    pc.plotByIds('ml')

    pc.set_plot_attributes('ml', {'ylim': (0,2)})
    pc.plotByIds('ml')

    #=================================================================
    # showing plotall (plots all plots sequentially)

    pc.plot_all()


