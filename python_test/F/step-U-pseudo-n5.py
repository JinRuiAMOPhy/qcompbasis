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

  U_opt_n5 = grasp.calc_setup('U_opt_n5')#, clear = True, clear_what = ['All'] )#, **Reigen)
  #U_opt_n5.Version('mpi')
  U_opt_n5.Debug(dbg_control)
  U_opt_n5.NucInfo(grasp.ElemTab['F'], NucDetail = {"NucSpin":1.0, "Dipole":1.0, 
                                          "Qpole":1.0,  
                                          "RNucRMS":0.1, "RNucSkin":0.05})
  U_opt_n5.CSFBasis({#'InactShell':'1s2 ', 'J':1, 
                  #'CloseCore':'He', 'JLow':0.5, 'JHigh':2.5,  # 2J
                  'JLow':0.5, 'JHigh':2.5,  # 2J
                  'config':['orbs:(n1,n2,n3,n4,n5);ref:1s1_2s2_2p6; Excite:1s,n2,n3->n2,n3,n4,n5(S,D)',
                            'orbs:(n1,n2,n3,n4,n5);ref:1s1_2s2_2p5_3s1; Excite:1s,n2,n3->n2,n3,n4,n5(S,D)',
                            'orbs:(n1,n2,n3,n4,n5);ref:1s1_2s2_2p5_3p1; Excite:1s,n2,n3->n2,n3,n4,n5(S,D)']
                 })
  U_opt_n5.WaveFunc(Control = {'type':'n5:H; n1,n2,n3,n4:../U_opt_3dn4/rwfn.out'})
  U_opt_n5.Angular(Control ={'kind':'parallel', 'interact':'full'})
  U_opt_n5.SCF(Control = {#'QED':{},
                      'maxiter':100,
                      'spec_orb':[],
                      'update_orb':['5*'],
                      'accuracy':'1.e-8',
              # 3s, 3p is only slightly mixed in first few levels, one can manually add more weight.
              # to achieve SCF convergence
                      'block' : {'weight':{'kind': 'standard'}, #'user', 'ratio':[0.2,0.9,0.1,0.9,0.1]}, #'standard'}, 
                                 'level': {'1/2+':[1,2,3,4],   # opt. 3s
                                           '1/2-':[1,2,3],  # opt. 1s,2s,2p
                                           '3/2-':[1,2,3], '3/2+':[1,2,3,4], 
                                           '5/2+':[1,2,3,4],'5/2-':[1]}, 
                      'order' : 'update' # or scc -- self consistency connected
                    # 'converg':{}   
                                }
                     })

  U_opt_n5.CI(Control = {'QED' : {'HTrans':True, 'TransFreq':False, 
                               'VacPol':True, 'NormMShift':True, 
                               'SpecMShift':True, 'Self':True, 
                               'SelfEnergyMaxN':3  }, 
                      'restart': False, #'perturb' : {'2-':[4]},
                      'block': {'1/2+':range(1,8),'3/2+':range(1,8),'5/2+':range(1,5),
                                '1/2-':range(1,4),'3/2-':range(1,4),'5/2-':range(1,2)} 
                     }
         )
  U_opt_n5.execute('Nuc,Wave,Angular, scf') 
  U_opt_n5.execute('ci') 
  U_opt_n5.report('scf,ci')
  del U_opt_n5
if __name__ == '__main__' :
  main()
