#  Z  A   mass 
import os
import copy
import numpy as np
from subprocess import Popen, PIPE

import sys
#sys.path.append('/home/ruijin/')
#from mypylib import grasp_mcscf as grasp
import grasp_mcscf as grasp

dbg = {'cfg':False, 'wave':False, 'nuc':False,
       'angular':False, 'scf':False}

def main() :
#  Reigen = {'idiag':0, 'ipolph': 2, 'n_phy_targ':4, 'sym_blocks':[grasp.symmetry(0,1), grasp.symmetry(1,-1)]}
  mod1 = grasp.calc_setup('He-basis-gen', clear = True, clear_what = ['All'], exec_grasp = True) #False)
  mod1.Clight(137.035999139000)
  dbg_control = dbg # defined at the head of file
  mod1.Debug(dbg_control)
  #mod1.Grid({'RHN':0.528850E-06,
  #           'H'  :0.104167E-01,
  #           'HP' :0.000000000000000E-001,
  #           'N'  :1764})
  mod1.NucInfo(grasp.ElemTab['O'], NucDetail = {"NucSpin":1.0, "Dipole":1.0, 
                                           "Qpole":1.0,  
                                           "RNucRMS":0.1, "RNucSkin":0.05})
  mod1.CSFBasis({#'InactShell':'1s2 ', 'J':1, 'CloseCore':'He'
                  'J2Low':0, 'J2High':2,  'Parity':1, # 2J even 1 odd -1
                  #'JLow':0, 'JHigh':2,  'Parity':1, # 2J even 1 odd -1
                  'config':['orbs:(n1,n2,3s);ref:1s2_2s2_2p4;'+\
                                  'Excite:1s->2:3s(S)',
                            'orbs:(n1,n2,ano-5p);ref:1s2_2s2_2p4;'+\
                                  'Excite:2p->3:5p(S)']
                  #          'orbs:(n1,n2);ref:2p1',
                  #          'orbs:(n1,3s);ref:3s1'] 
                 })
  
  mod1.WaveFunc(Control = {'type':'n1,n2,3s,ano-5p:TF'})
  mod1.Angular(Control ={'kind':'parallel', 'interact':'full'})
  mod1.SCF(Control = {#'QED':{},
                      'maxiter':100,
                      'spec_orb':['*'],
                      'update_orb':['*'],
                      'accuracy':'1.e-8',
                      'block' : {'weight':{'kind':'user', 'ratio':[0.7,0.3]}, 
                                 'level': {'0+':range(1,3)},
                      'order' : 'update' # or scc -- self consistency connected
                    # 'converg':{}   
                                }
                     })
  mod1.CI(Control = {} 
         )
  del mod1

if __name__ == '__main__' :
  main()
