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
  L_opt_n5 = grasp.calc_setup('L_opt_n5')#, clear = True, clear_what = ['All'])#, **Reigen)
  #L_opt_n5.Version('mpi')
  L_opt_n5.Clight(137.035999139000)
  L_opt_n5.Debug(dbg_control)
  L_opt_n5.Grid({'RHN':2.500000000000000E-007,
             'H'  :5.000000000000000E-002,
             'HP' :0.000000000000000E-001,
             'N'  :590})
  L_opt_n5.NucInfo(grasp.ElemTab['F'], NucDetail = {"NucSpin":1.0, "Dipole":1.0, 
                                           "Qpole":1.0,  
                                           "RNucRMS":0.1, "RNucSkin":0.05})
  L_opt_n5.CSFBasis({'JLow':0.5, 'JHigh':2.5,  # 2J
                  'config':[
                            'orbs:(n1,n2,n3,n4,n5);ref:1s2_2s2_2p5; Excite:n1,n2->n3,n4,n5(S,D)',
                            'orbs:(n1,n2,n3,n4,n5);ref:1s2_2s2_2p4_3s1; Excite:n1,n2,3s->n3,n4,n5(S,D)',
                            'orbs:(n1,n2,n3,n4,n5);ref:1s2_2s2_2p4_3p1; Excite:n1,n2,3p->n3,n4,n5(S,D)',
                           ]
                 })
  L_opt_n5.WaveFunc(Control = {'type':'n1,n2,n3,n4:../L_opt_3dn4/rwfn.out; n5:H'})
  L_opt_n5.Angular(Control ={'kind':'parallel', 'interact':'full'})
  L_opt_n5.SCF(Control = {#'QED':{},
                      'maxiter':100,
                      'spec_orb':[],
                      'update_orb':['5*'],
                      'accuracy':'1.e-8',
                      #'block' : {'weight':{'kind':'user', 'ratio':[0.7,0.3]}, 
                      'block' : {'weight':{'kind':'standard'},
                                 'level': {'5/2-':[1,2], '3/2-':[1,2], '1/2-':[1,2], 
                                           '5/2+':[1], '3/2+':[1,2], '1/2+':[1,2]}, 
                      'order' : 'update' # or scc -- self consistency connected
                    # 'converg':{}   
                                }
                     })
  L_opt_n5.CI(Control = {'QED' : {'HTrans':True, 'TransFreq':False, 
                               'VacPol':True, 'NormMShift':True, 
                               'SpecMShift':True, 'Self':True, 
                               'SelfEnergyMaxN':3  }, 
                      'restart': False, #'perturb' : {'2-':[4]},
                      'block': {'1/2+':range(1,3),'3/2+':range(1,3),'5/2+':range(1,3),
                                '1/2-':range(1,3),'3/2-':range(1,3),'5/2-':range(1,3)} 
                     }
         )
  L_opt_n5.execute('Nuc,split,Wave,Angular_mpi') 
  L_opt_n5.execute('SCF_mpi') 
  L_opt_n5.execute('CI_mpi') 
  L_opt_n5.report('scf,ci')
  del L_opt_n5

if __name__ == '__main__' :
  main()
