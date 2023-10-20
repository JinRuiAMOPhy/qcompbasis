#  Z  A   mass 
import os
import copy
import numpy as np
from subprocess import Popen, PIPE

import sys
sys.path.append('/home/ruijin/')
from mypylib import grasp_mcscf_v2 as grasp

dbg = {'cfg':False, 'wave':False, 'nuc':False,
       'angular':False, 'scf':False}

def main() :
  dbg_control = dbg # defined at the head of file
  DC_opt_n12 = grasp.calc_setup('DC_opt_n12')#, clear = True, clear_what = ['All'])#, **Reigen)
  DC_opt_n12.Clight(137.035999139000)
  DC_opt_n12.Debug(dbg_control)
  DC_opt_n12.Grid({'RHN':2.500000000000000E-007,
             'H'  :5.000000000000000E-002,
             'HP' :0.000000000000000E-001,
             'N'  :590})
  DC_opt_n12.NucInfo(grasp.ElemTab['F'], NucDetail = {"NucSpin":1.0, "Dipole":1.0, 
                                           "Qpole":1.0,  
                                           "RNucRMS":0.1, "RNucSkin":0.05})
  DC_opt_n12.CSFBasis({'JLow':0.5, 'JHigh':2.5,  # 2J
                  'config':['orbs:(n2,3p);ref:2s2_2p6_3p1',
                           ]
                 })
  #DC_opt_n12.WaveFunc(Control = {'type':'n1,n2:TF;3sp,3d-:H;3d+:./rwfn.out'}) 
  DC_opt_n12.WaveFunc(Control = {'type':'n2,3p:TF'})
  DC_opt_n12.Angular(Control ={'kind':'parallel', 'interact':'full'})
  DC_opt_n12.SCF(Control = {#'QED':{},
                      'maxiter':100,
                      'spec_orb':['*'],
                      'update_orb':['*'],
                      'accuracy':'1.e-8',
                      #'block' : {'weight':{'kind':'user', 'ratio':[0.7,0.3]}, 
                      'block' : {'weight':{'kind':'standard'},
                                 'level': {'1/2-':[1],'3/2-':[1]}, 
                      'order' : 'update' # or scc -- self consistency connected
                    # 'converg':{}   
                                }
                     })
  DC_opt_n12.CI(Control = {'QED' : {'HTrans':True, 'TransFreq':False, 
                               'VacPol':True, 'NormMShift':True, 
                               'SpecMShift':True, 'Self':True, 
                               'SelfEnergyMaxN':3  }, 
                      'restart': False, #'perturb' : {'2-':[4]},
                      'block': {'1/2+':[],
                                '1/2-':[1],'3/2-':[1]} 
                     }
         )
  DC_opt_n12.execute('Nuc,CSF,split,Wave,Angular,SCF,CI') 
  DC_opt_n12.report('scf,ci')
  del DC_opt_n12

  DC_opt_n12 = grasp.calc_setup('DC_opt_3dn4')#, clear = True, clear_what = ['All'])#, **Reigen)
  DC_opt_n12.Clight(137.035999139000)
  DC_opt_n12.Debug(dbg_control)
  DC_opt_n12.Grid({'RHN':2.500000000000000E-007,
             'H'  :5.000000000000000E-002,
             'HP' :0.000000000000000E-001,
             'N'  :590})
  DC_opt_n12.NucInfo(grasp.ElemTab['F'], NucDetail = {"NucSpin":1.0, "Dipole":1.0, 
                                           "Qpole":1.0,  
                                           "RNucRMS":0.1, "RNucSkin":0.05})
  DC_opt_n12.CSFBasis({'JLow':0.5, 'JHigh':2.5,  # 2J
                  'config':['orbs:(n2,3pd);ref:2s2_2p6_3p1; Excite:n2->n3(S,D)',
                           ]
                 })
  #DC_opt_n12.WaveFunc(Control = {'type':'n1,n2:TF;3sp,3d-:H;3d+:./rwfn.out'}) 
  DC_opt_n12.WaveFunc(Control = {'type':'n2,3p:../DC_opt_n12/rwfn.out; 3d:H'})
  DC_opt_n12.Angular(Control ={'kind':'parallel', 'interact':'full'})
  DC_opt_n12.SCF(Control = {#'QED':{},
                      'maxiter':100,
                      'spec_orb':[],
                      'update_orb':['3d*'],
                      'accuracy':'1.e-8',
                      #'block' : {'weight':{'kind':'user', 'ratio':[0.7,0.3]}, 
                      'block' : {'weight':{'kind':'standard'},
                                 'level': {'1/2-':[1],'3/2-':[1]}, 
                      'order' : 'update' # or scc -- self consistency connected
                    # 'converg':{}   
                                }
                     })
  DC_opt_n12.CI(Control = {'QED' : {'HTrans':True, 'TransFreq':False, 
                               'VacPol':True, 'NormMShift':True, 
                               'SpecMShift':True, 'Self':True, 
                               'SelfEnergyMaxN':3  }, 
                      'restart': False, #'perturb' : {'2-':[4]},
                      'block': {'1/2+':[],
                                '1/2-':[1],'3/2-':[1]} 
                     }
         )
  DC_opt_n12.execute('Nuc,CSF,split,Wave,Angular,SCF,CI') 
  DC_opt_n12.report('scf,ci')
  del DC_opt_n12
if __name__ == '__main__' :
  main()
