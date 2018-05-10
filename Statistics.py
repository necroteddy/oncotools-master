# -*- coding: utf-8 -*-
"""
Created on Wed May  9 20:12:02 2018

@author: Vincent Qi
"""
import sys

class Stat():
    def __init__(self, lst):
        self.statlist = lst
        self.numbTrue = -1
        self.numbFalse = -1
        
    def calcstats(self):
        self.numbTrue = sum(self.statlist)
        self.numbFalse = len(self.statlist) - self.numbTrue
        
    def printstats(self):
        if self.numTrue == -1:
            self.calcstats()
        else:
            out1 = "There are {} masks with no errors found".format(self.numbTrue)
            out2 = "There are {} masks with errors found".format(self.numbFalse)
            sys.stdout.write(out1)
            sys.stdout.write(out2)