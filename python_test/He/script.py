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
  mod1 = grasp.calc_setup('mod1', clear = True, clear_what = ['All'], kcmax = 11)
  mod1.Clight(137.035999139000)
  dbg_control = dbg # defined at the head of file
  mod1.Debug(dbg_control)
  mod1.Grid({'RHN':2.500000000000000E-007,
             'H'  :5.000000000000000E-002,
             'HP' :0.000000000000000E-001,
             'N'  :590})
  mod1.NucInfo(grasp.ElemTab['O'], NucDetail = {"NucSpin":1.0, "Dipole":1.0, 
                                           "Qpole":1.0,  
                                           "RNucRMS":0.1, "RNucSkin":0.05})
  mod1.CSFBasis({#'InactShell':'1s2 ', 'J':1, 
                  'CloseCore':'He', 'JLow':0, 'JHigh':6,  # 2J
                  'config':['orbs:(n1,n2);ref:2s2_2p4',
                            'orbs:(n1,n2);ref:2s1_2p5',
                            'orbs:(n1,n2);ref:2p6']
                 })
  #mod1.WaveFunc(Control = {'type':'n1,n2:TF;3sp,3d-:H;3d+:./rwfn.out'}) 
  mod1.WaveFunc(Control = {'type':'n1,n2:TF'})
  mod1.Angular(Control ={'kind':'parallel', 'interact':'full'})
  mod1.SCF(Control = {#'QED':{},
                      'maxiter':100,
                      'spec_orb':['*'],
                      'update_orb':['*'],
                      'accuracy':'1.e-8',
                      'block' : {'weight':{'kind':'user', 'ratio':[0.3,0.7]}, 
                                 'level': {'2+':range(1,2),'1+':range(1,2)},
                      'order' : 'update' # or scc -- self consistency connected
                    # 'converg':{}   
                                }
                     })
  mod1.CI(Control = {} 
         )
  #mod1.execute('Nuc,CSF,split,Wave,Angular,SCF,CI') 
  # not every module need to be executed.
  #mod1.execute('Nuc,csf,Wave,Angular, scf') 
  
  del mod1

  mod2 = grasp.calc_setup('mod2', clear = True, clear_what = ['All'])
  mod2.NucInfo(grasp.ElemTab['O'], NucDetail = {"NucSpin":1.0, "Dipole":1.0, 
                                          "Qpole":1.0,  
                                          "RNucRMS":0.1, "RNucSkin":0.05})
  mod2.CSFBasis({#'InactShell':'1s2 ', 'J':1, 
                  'CloseCore':'He', 'JLow':0, 'JHigh':6,  # 2J
                  'config':['orbs:(n1,n2,n3);ref:2s2_2p4;Excite:n2,n3->n2,n3(S)',
                            'orbs:(n1,n2,3sp);ref:2s1_2p5;Excite:n2->n2,n3(S)',
                            'orbs:(n1,n2,n3);ref:2p6;Excite:n2->n2,n3(S)'] 
                 })
  #mod1.WaveFunc(Control = {'type':'n1,n2:TF;3sp,3d-:H;3d+:./rwfn.inp'}) 
  mod2.WaveFunc(Control = {'type':'n3:TF;n1,n2:mod1/rwfn.out'})
  mod2.Angular(Control ={'kind':'parallel', 'interact':'full'})
  mod2.SCF(Control = {#'QED':{},
                      'maxiter':1,
                      'spec_orb':['*'],
                      'update_orb':['3*'],
                      'accuracy':'1.e-8',
                      'block' : {'weight':{'kind':'user', 'ratio':[0.3,0.2,0.3,0.2]}, 
                                 'level': {'3+':range(1,3),'1+':range(1,3)},
                      'order' : 'update' # or scc -- self consistency connected
                    # 'converg':{}   
                                }
                     })
  mod2.CI(Control = {} 
         )
  #mod1.execute('Nuc,CSF,split,Wave,Angular,SCF,CI,Rmat') 
  # not every module need to be executed.
  #mod2.execute('Nuc,csf,Wave,Angular, scf') #,split,Wave,Angular,SCF,CI,Rmat') 

if __name__ == '__main__' :
  main()
