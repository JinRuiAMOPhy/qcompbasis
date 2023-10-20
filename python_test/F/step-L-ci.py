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
  L_ci = grasp.calc_setup('L_ci')#, clear = True, clear_what = ['All'])#, **Reigen)
  L_ci.Clight(137.035999139000)
  L_ci.Debug(dbg_control)
  L_ci.Grid({'RHN':2.500000000000000E-007,
             'H'  :5.000000000000000E-002,
             'HP' :0.000000000000000E-001,
             'N'  :590})
  L_ci.NucInfo(grasp.ElemTab['F'], NucDetail = {"NucSpin":1.0, "Dipole":1.0, 
                                           "Qpole":1.0,  
                                           "RNucRMS":0.1, "RNucSkin":0.05})
  L_ci.CSFBasis({'JLow':0.5, 'JHigh':2.5,  # 2J
                  'config':[
                            'orbs:(n1,n2,n3,n4,n5,6spdfg,7spdfg);ref:1s2_2s2_2p5; Excite:n1,n2->n2,n3,n4,n5,n6,n7(S,D); restrict:n2>=5',
                            'orbs:(n1,n2,n3,n4,n5,6spdfg,7spdfg);ref:1s2_2s2_2p4_3s1; Excite:n1,n2->n2,n3,n4,n5,n6,n7(S,D); restrict:n2>=5',
                           ]
                 })
  L_ci.WaveFunc(Control = {'type':'n1,n2:../L_opt_n12/rwfn.out; 3s:../L_opt_3s/rwfn.out; 3p:../L_opt_3p/rwfn.out; 3d,n4:../L_opt_3dn4/rwfn.out; n5:../L_opt_n5/rwfn.out; n6:../L_opt_n6/rwfn.out; n7:../L_opt_n7/rwfn.out'})
  L_ci.Angular(Control ={'kind':'parallel', 'interact':'full'})
  L_ci.SCF(Control = {#'QED':{},
                      'maxiter':100,
                      'spec_orb':[],
                      'update_orb':[],
                      'accuracy':'1.e-8',
                      #'block' : {'weight':{'kind':'user', 'ratio':[0.7,0.3]}, 
                      'block' : {'weight':{'kind':'standard'},
                                 'level': {'5/2-':[1,2], '3/2-':[1,2], '1/2-':[1,2], 
                                           '5/2+':[1], '3/2+':[1,2], '1/2+':[1,2]}, 
                      'order' : 'update' # or scc -- self consistency connected
                    # 'converg':{}   
                                }
                     })
  L_ci.CI(Control = {'QED' : {'HTrans':True, 'TransFreq':False, 
                               'VacPol':True, 'NormMShift':True, 
                               'SpecMShift':True, 'Self':True, 
                               'SelfEnergyMaxN':3  }, 
                      'restart': False, #'perturb' : {'2-':[4]},
                      'block': {'1/2+':range(1,4),'3/2+':range(1,4),'5/2+':range(1,4),
                                '1/2-':range(1,4),'3/2-':range(1,4),'5/2-':range(1,4)} 
                     }
         )
  L_ci.execute('Nuc,split,Wave,Angular') 
  L_ci.execute('CI') 
  L_ci.report('ci')
  del L_ci

if __name__ == '__main__' :
  main()
