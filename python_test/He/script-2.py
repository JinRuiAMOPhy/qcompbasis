#  Z  A   mass 
import os
import copy
import numpy as np
from subprocess import Popen, PIPE

import sys
sys.path.append('/home/ruijin/')
from mypylib import grasp_mcscf as grasp

dbg = {'cfg':False, 'wave':False, 'nuc':False,
       'angular':False, 'scf':False}

def main() :
#  Reigen = {'idiag':0, 'ipolph': 2, 'n_phy_targ':4, 'sym_blocks':[grasp.symmetry(0,1), grasp.symmetry(1,-1)]}
  mod1 = grasp.calc_setup('mod1', clear = True, clear_what = ['All'])
  mod1.Clight(137.035999139000)
  dbg_control = dbg # defined at the head of file
  mod1.Debug(dbg_control)
  mod1.Grid({'RHN':0.528850E-06,
             'H'  :0.104167E-01,
             'HP' :0.000000000000000E-001,
             'N'  :1764})
  mod1.NucInfo(grasp.ElemTab['He'], NucDetail = {"NucSpin":1.0, "Dipole":1.0, 
                                           "Qpole":1.0,  
                                           "RNucRMS":0.1, "RNucSkin":0.05})
  mod1.CSFBasis({#'InactShell':'1s2 ', 'J':1, 'CloseCore':'He'
                  'JLow':0, 'JHigh':0,  'Parity':1, # 2J even 1 odd -1
                  'config':['orbs:(1s,2s,3s,4s,5s,6s,7s,8s,9s,10s,11s,12s,13s,14s);ref:1s2;'+\
                                  'Excite:1s->2:14s(S)',
                            'orbs:(ano-14s);ref:2s2;'+\
                                  'Excite:2s->3:14s(S)']
                  #          'orbs:(n1,n2);ref:2p1',
                  #          'orbs:(n1,3s);ref:3s1'] 
                 })
  
  del mod1

if __name__ == '__main__' :
  main()
