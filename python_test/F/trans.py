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
  dbg_control = dbg # defined at the head of file

#  T1 = grasp.transit('mod5L', 'mod5U')
#  T1.execute('trans')
#  del T1
#  T1 = grasp.transit('mod5L', 'mod5M')
#  T1.execute('rbiotr, trans')
#  T1 = grasp.transit('mod5GS3p', 'mod5M')
#  T1.execute('rbiotr, trans')
  #T1 = grasp.transit('mod5L-1s-act', 'mod5U-1s-act')
  #T1.execute('rbiotr, trans')
  #T1 = grasp.transit('mod5-shake-1s-act', 'mod5M-1s-act')
  #T1 = grasp.transit('L_opt_n5', 'U_opt_n5')
  os.system('ulimit -s unlimited')
  T1 = grasp.transit('L_opt_n7', 'U_opt_n7')
  T1.execute('rbiotr, trans')
if __name__ == '__main__' :
  main()
