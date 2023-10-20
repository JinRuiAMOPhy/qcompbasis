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
  L_opt_n7 = grasp.calc_setup('L_opt_n7')#, clear = True, clear_what = ['All'])#, **Reigen)
  #L_opt_n7.Version('mem')
  L_opt_n7.Clight(137.035999139000)
  L_opt_n7.Debug(dbg_control)
  L_opt_n7.Grid({'RHN':2.500000000000000E-007,
             'H'  :5.000000000000000E-002,
             'HP' :0.000000000000000E-001,
             'N'  :590})
  L_opt_n7.NucInfo(grasp.ElemTab['F'], NucDetail = {"NucSpin":1.0, "Dipole":1.0, 
                                           "Qpole":1.0,  
                                           "RNucRMS":0.1, "RNucSkin":0.05})
  L_opt_n7.CSFBasis({'JLow':0.5, 'JHigh':2.5,  # 2J
                  'config':[
                            'orbs:(n1,n2,n3,n4,n5,6spdfg,7spdfg);ref:1s2_2s2_2p5; Excite:n1,n2->n2,n3,n4,n5,n6,n7(S,D);restrict:n7<=1, n6<=1',
                            'orbs:(n1,n2,n3,n4,n5,6spdfg,7spdfg);ref:1s2_2s2_2p4_3s1; Excite:n1,n2,3s->n2,n3,n4,n5,n6,n7(S,D);restrict: n7<=1, n6<=1',
                            'orbs:(n1,n2,n3,n4,n5,6spdfg,7spdfg);ref:1s2_2s2_2p4_3p1; Excite:n1,n2,3p->n2,n3,n4,n5,n6,n7(S,D);restrict: n7<=1, n6<=1',
                           ]
                 })
  L_opt_n7.WaveFunc(Control = {'type':'n1,n2,n2,n3,n4,n5,n6:../L_opt_n6/rwfn.out; n7:H'})
  L_opt_n7.Angular(Control ={'kind':'parallel', 'interact':'full'})
  L_opt_n7.SCF(Control = {#'QED':{},
                      'maxiter':100,
                      'spec_orb':[],
                      'update_orb':['7*'],
                      'accuracy':'1.e-8',
                      #'block' : {'weight':{'kind':'user', 'ratio':[0.7,0.3]}, 
                      'block' : {'weight':{'kind':'standard'},
                                 'level': {'5/2-':[1,2], '3/2-':[1,2], '1/2-':[1,2], 
                                           '5/2+':[1], '3/2+':[1,2], '1/2+':[1,2]}, 
                      'order' : 'update' # or scc -- self consistency connected
                    # 'converg':{}   
                                }
                     })
  L_opt_n7.CI(Control = {'QED' : {'HTrans':True, 'TransFreq':False, 
                               'VacPol':True, 'NormMShift':True, 
                               'SpecMShift':True, 'Self':True, 
                               'SelfEnergyMaxN':3  }, 
                      'restart': False, #'perturb' : {'2-':[4]},
                      'block': {'1/2+':range(1,3),'3/2+':range(1,3),'5/2+':range(1,3),
                                '1/2-':range(1,3),'3/2-':range(1,3),'5/2-':range(1,3)} 
                     }
         )
  #L_opt_n7.execute('Nuc,split,Wave,Angular, scf') 
  L_opt_n7.execute('Nuc,split,Wave, scf') 
  L_opt_n7.execute('CI') 
  L_opt_n7.report('scf,ci')
  del L_opt_n7

if __name__ == '__main__' :
  main()
