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
  L_opt_n12 = grasp.calc_setup('L_opt_n12')#, clear = True, clear_what = ['All'])#, **Reigen)
  L_opt_n12.Clight(137.035999139000)
  L_opt_n12.Debug(dbg_control)
  L_opt_n12.Grid({'RHN':2.500000000000000E-007,
             'H'  :5.000000000000000E-002,
             'HP' :0.000000000000000E-001,
             'N'  :590})
  L_opt_n12.NucInfo(grasp.ElemTab['F'], NucDetail = {"NucSpin":1.0, "Dipole":1.0, 
                                           "Qpole":1.0,  
                                           "RNucRMS":0.1, "RNucSkin":0.05})
  L_opt_n12.CSFBasis({'JLow':0.5, 'JHigh':2.5,  # 2J
                  'config':['orbs:(n1,n2);ref:1s2_2s2_2p5',
                           ]
                 })
  #L_opt_n12.WaveFunc(Control = {'type':'n1,n2:TF;3sp,3d-:H;3d+:./rwfn.out'}) 
  L_opt_n12.WaveFunc(Control = {'type':'n1,n2:TF'})
  L_opt_n12.Angular(Control ={'kind':'parallel', 'interact':'full'})
  L_opt_n12.SCF(Control = {#'QED':{},
                      'maxiter':100,
                      'spec_orb':['*'],
                      'update_orb':['*'],
                      'accuracy':'1.e-8',
                      #'block' : {'weight':{'kind':'user', 'ratio':[0.7,0.3]}, 
                      'block' : {'weight':{'kind':'standard'},
                                 'level': {'3/2-':[1], '1/2-':[1]}, 
                      'order' : 'update' # or scc -- self consistency connected
                    # 'converg':{}   
                                }
                     })
  L_opt_n12.CI(Control = {'QED' : {'HTrans':True, 'TransFreq':False, 
                               'VacPol':True, 'NormMShift':True, 
                               'SpecMShift':True, 'Self':True, 
                               'SelfEnergyMaxN':3  }, 
                      'restart': False, #'perturb' : {'2-':[4]},
                      'block': {'1/2+':range(1,2),
                                '1/2-':range(1,2),'3/2-':range(1,2)} 
                     }
         )
  L_opt_n12.execute('Nuc,CSF,split,Wave,Angular,SCF,CI') 
  L_opt_n12.report('scf,ci')
  del L_opt_n12


  L_opt_3s = grasp.calc_setup('L_opt_3s')#, clear = True, clear_what = ['All'] )#, **Reigen)
  L_opt_3s.Debug(dbg_control)
  L_opt_3s.NucInfo(grasp.ElemTab['F'], NucDetail = {"NucSpin":1.0, "Dipole":1.0, 
                                          "Qpole":1.0,  
                                          "RNucRMS":0.1, "RNucSkin":0.05})
  L_opt_3s.CSFBasis({#'InactShell':'1s2 ', 'J':1, 
                  #'CloseCore':'He', 'JLow':0.5, 'JHigh':2.5,  # 2J
                  'JLow':0.5, 'JHigh':2.5,  # 2J
                  'config':['orbs:(n1,n2,3s);ref:1s2_2s2_2p4_3s1']
                 })
  #L_opt_n12.WaveFunc(Control = {'type':'n1,n2:TF;3sp,3d-:H;3d+:./rwfn.inp'}) 
  L_opt_3s.WaveFunc(Control = {'type':'n3:H;n1,n2:../L_opt_n12/rwfn.out'})
  L_opt_3s.Angular(Control ={'kind':'parallel', 'interact':'full'})
  L_opt_3s.SCF(Control = {#'QED':{},
                      'maxiter':100,
                      'spec_orb':['3s'],
                      'update_orb':['3*'],
                      'accuracy':'1.e-8',
              # 3s, 3p is only slightly mixed in first few levels, one can manually add more weight.
              # to achieve SCF convergence
                      'block' : {'weight':{'kind': 'standard'}, #'user', 'ratio':[0.2,0.9,0.1,0.9,0.1]}, #'standard'}, 
                                 'level': {'1/2+':[1,2],   # opt. 3s
                                           '1/2-':[1],  # opt. 1s,2s,2p
                                           '3/2-':[1], '3/2+':[1,2], 
                                           '5/2+':[1],'5/2-':[]}, 
                      'order' : 'update' # or scc -- self consistency connected
                    # 'converg':{}   
                                }
                     })

  L_opt_3s.CI(Control = {'QED' : {'HTrans':True, 'TransFreq':False, 
                               'VacPol':True, 'NormMShift':True, 
                               'SpecMShift':True, 'Self':True, 
                               'SelfEnergyMaxN':3  }, 
                      'restart': False, #'perturb' : {'2-':[4]},
                      'block': {'1/2+':range(1,3),'3/2+':range(1,3),'5/2+':range(1,3),
                                '1/2-':range(1,3),'3/2-':range(1,3),'5/2-':range(1,3)} 
                     }
         )
  L_opt_3s.execute('Nuc,Wave,Angular, scf') 
  L_opt_3s.execute('ci') 
  L_opt_3s.report('scf,ci')
  del L_opt_3s

  L_opt_3p = grasp.calc_setup('L_opt_3p')#, clear = True, clear_what = ['All'] )#, **Reigen)
  L_opt_3p.Debug(dbg_control)
  L_opt_3p.NucInfo(grasp.ElemTab['F'], NucDetail = {"NucSpin":1.0, "Dipole":1.0, 
                                          "Qpole":1.0,  
                                          "RNucRMS":0.1, "RNucSkin":0.05})
  L_opt_3p.CSFBasis({#'InactShell':'1s2 ', 'J':1, 
                  #'CloseCore':'He', 'JLow':0.5, 'JHigh':2.5,  # 2J
                  'JLow':0.5, 'JHigh':2.5,  # 2J
                  'config':['orbs:(n1,n2,3sp);ref:1s2_2s2_2p5_3s1',
                            'orbs:(n1,n2,3sp);ref:1s2_2s2_2p4_3p1']
                 })
  L_opt_3p.WaveFunc(Control = {'type':'3p:H;n1,n2,3s:../L_opt_3s/rwfn.out'})
  L_opt_3p.Angular(Control ={'kind':'parallel', 'interact':'full'})
  L_opt_3p.SCF(Control = {#'QED':{},
                      'maxiter':100,
                      'spec_orb':['3p*'],
                      'update_orb':['3p*'],
                      'accuracy':'1.e-8',
              # 3s, 3p is only slightly mixed in first few levels, one can manually add more weight.
              # to achieve SCF convergence
                      'block' : {'weight':{'kind': 'standard'}, #'user', 'ratio':[0.2,0.9,0.1,0.9,0.1]}, #'standard'}, 
                                 'level': {'1/2+':[1,2],   # opt. 3s
                                           '1/2-':[1,2],  # opt. 1s,2s,2p
                                           '3/2-':[1,2], '3/2+':[1,2], 
                                           '5/2+':[1],'5/2-':[1,2]}, 
                      'order' : 'update' # or scc -- self consistency connected
                    # 'converg':{}   
                                }
                     })

  L_opt_3p.CI(Control = {'QED' : {'HTrans':True, 'TransFreq':False, 
                               'VacPol':True, 'NormMShift':True, 
                               'SpecMShift':True, 'Self':True, 
                               'SelfEnergyMaxN':3  }, 
                      'restart': False, #'perturb' : {'2-':[4]},
                      'block': {'1/2+':range(1,3),'3/2+':range(1,3),'5/2+':range(1,3),
                                '1/2-':range(1,3),'3/2-':range(1,3),'5/2-':range(1,3)} 
                     }
         )
  L_opt_3p.execute('Nuc,Wave,Angular, scf') 
  L_opt_3p.execute('ci') 
  L_opt_3p.report('scf,ci')
  del L_opt_3p
if __name__ == '__main__' :
  main()
