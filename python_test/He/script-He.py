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
  mod1 = grasp.calc_setup('He-Mod1', clear = True, clear_what = ['All'], exec_grasp = True)
  mod1.Clight(137.035999139000)
  dbg_control = dbg # defined at the head of file
  mod1.Debug(dbg_control)
  mod1.Grid({'RHN':2.500000000000000E-007,
             'H'  :5.000000000000000E-002,
             'HP' :0.000000000000000E-001,
             'N'  :590})
  mod1.NucInfo(grasp.ElemTab['He'], NucDetail = {"NucSpin":1.0, "Dipole":1.0, 
                                           "Qpole":1.0,  
                                           "RNucRMS":0.1, "RNucSkin":0.05})
  mod1.CSFBasis({#'InactShell':'1s2 ', 'J':1, 
                  'JLow':0, 'JHigh':2, 'Parity':1,  # 2J
                  'config':['orbs:(ano-2s);ref:1s2;Excite:1s->2s(S,D)']
                 })
  mod1.WaveFunc(Control = {'type':'n1,n2:TF'})
  mod1.Angular(Control ={'kind':'parallel', 'interact':'full'})
  mod1.SCF(Control = {#'QED':{},
                      'maxiter':100,
                      'spec_orb':['*'],
                      'update_orb':['*'],
                      'accuracy':'1.e-8',
                      'block' : {'weight':{'kind':'user', 'ratio':[0.4,0.2,0.2]}, 
                                 'level': {'0+':range(1,3)},
                      'order' : 'update' # or scc -- self consistency connected
                    # 'converg':{}   
                                }
                     })
  mod1.CI(Control = {} 
         )
  
  del mod1

  mod2 = grasp.calc_setup('He-Mod2', clear = True, clear_what = ['All'], exec_grasp = True)
  mod2.Clight(137.035999139000)
  dbg_control = dbg # defined at the head of file
  mod2.Debug(dbg_control)
  mod2.Grid({'RHN':2.500000000000000E-007,
             'H'  :5.000000000000000E-002,
             'HP' :0.000000000000000E-001,
             'N'  :590})
  mod2.NucInfo(grasp.ElemTab['He'], NucDetail = {"NucSpin":1.0, "Dipole":1.0, 
                                           "Qpole":1.0,  
                                           "RNucRMS":0.1, "RNucSkin":0.05})
  mod2.CSFBasis({#'InactShell':'1s2 ', 'J':1, 
                  'JLow':0, 'JHigh':2, 'Parity':1,  # 2J
                  'config':['orbs:(ano-4s);ref:1s2;Excite:1s->2:4s(S,D)']
                 })
  mod2.WaveFunc(Control = {'type':'n1,n2:He-Mod1/rwfn.out;3s,4s:TF'})
  mod2.Angular(Control ={'kind':'parallel', 'interact':'full'})
  mod2.SCF(Control = {#'QED':{},
                      'maxiter':100,
                      'spec_orb':['*'],
                      'update_orb':['3s', '4s'],
                      'accuracy':'1.e-8',
                      'block' : {'weight':{'kind':'user', 'ratio':[0.4,0.2,0.2,0.1,0.1]}, 
                                 'level': {'0+':range(1,3),'1+':[1,2,3]},
                      'order' : 'update' # or scc -- self consistency connected
                    # 'converg':{}   
                                }
                     })
  mod2.CI(Control = {} 
         )
  
  del mod2

if __name__ == '__main__' :
  main()
