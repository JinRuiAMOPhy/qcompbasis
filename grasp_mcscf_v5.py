#  Z  A   mass 
import os
import copy
import numpy as np
from subprocess import Popen, PIPE
import time

# some global data.
shell_delm = '_'
grasp_exe_deft = '/home/ruijin/grasp-dev/bin'
grasp_exe_big = '/home/ruijin/grasp-big/bin'
grasp_exe_mpi = '/home/ruijin/grasp-mpi/bin'
NCPUCORES = 5
AngTab = {'s':0, 'p':1, 'd':2, 'f':3, 'g':4,
          'h':5, 'i':6, 'j':7, 'k':8, 'l':9,
          'm':10, 'n':11, 'o':12}
KapTab = {'s':-1,'p-':1,'p':-2,'d-':2,'d':-3,'f-':3,
          'f':-4,'g-':4,'g':-5,'h-':5,'h':-6,
          'i-':6,'i':-7,'j-':7,'j':-8} 

def KapStr(kap) :
  for key, value in KapTab.items() :
     if value == kap : 
        return key
  return None

CloseCoreTab = { 'He':1, 'Ne':2, 'Ar':3, 'Kr':4,'Xe':5,'Rn':6} # empty 0
Nelec_of_CloseCore = [0,  2, 10, 18, 36, 54, 86]
Conf_of_CloseCore =  ['', '1s' ,'1s_2s_2p', '1s_2s_2p_3s_3p', '1s_2s_2p_3s_3p_3d_4s_4p','1s_2s_2p_3s_3p_3d_4s_4p_4d_5s_5p',
                      '1s_2s_2p_3s_3p_3d_4s_4p_4d_5s_5p_4f_5d_6s_6p']
RelConf_of_CloseCore =  ['', 
                         '1s' ,
                         '1s_2s_2p-_2p', 
                         '1s_2s_2p-_2p_3s_3p-_3p', 
                         '1s_2s_2p-_2p_3s_3p-_3p_3d-_3d_4s_4p-_4p',
                         '1s_2s_2p-_2p_3s_3p-_3p_3d-_3d_4s_4p-_4p_4d-_4d_5s_5p-_5p',
                         '1s_2s_2p-_2p_3s_3p-_3p_3d-_3d_4s_4p-_4p_4d-_4d_5s_5p-_5p_5d-_5d_6s_6p-_6p']
AngStr = 'spdfghijklmno'
ExctStr = {'S':1,'D':2,'T':3,'Q':4}
MaxOcc = [ 4 * l + 2 for l in range(0,12)]
MaxOcc_J2 = [ 1 + J2 for J2 in range(0,13)]

# some basic classes
     
class symmetry() :
   def __init__(self, J, p) :
     self.J = J
     self.p = p
class Elem :
   def __init__(self, Z, A, mass) :
     self.Z = Z
     self.A = A
     self.mass = mass

   #def __del__(self) :
   #  pass
     #print("Class Elem destroyed")
ElemTab = {
     # H Need to use point nucleus
     'H'  : Elem(1, 0, 1.0794), 
     'He' : Elem(2, 4, 4.002602),
     'Li' : Elem(3, 7, 6.941),
     'Be'  : Elem(4, 9, 9.012182),
     'B'  : Elem(5, 11, 10.811),
     'C'  : Elem(6, 12, 12.0107),
     'N'  : Elem(7, 14, 14.0067),
     'O'  : Elem(8, 16, 15.9994),
     'F'  : Elem(9, 19, 18.9984032),
     'Ne'  : Elem(10, 20, 20.1797),
     'Na'  : Elem(11, 23, 22.98976928),
     'Mg'  : Elem(12, 24, 24.3050),
     'Al'  : Elem(13, 27, 26.9815386),
     'Si'  : Elem(14, 28, 29.0855),
     'P'  : Elem(15, 31, 30.973762),
     'S'  : Elem(16, 32, 32.065),
     'Cl'  : Elem(17, 35, 35.453),
     'Ar'  : Elem(18, 40, 39.948),
     'K'  : Elem(19, 39, 39.0938),
     'Ca'  : Elem(20, 40, 40.078),
     'Sc'  : Elem(21, 45, 44.955912),
     'Ti'  : Elem(22, 48, 47.867),
     'V'  : Elem(23, 51, 50.9415),
     'Cr'  : Elem(24, 52, 51.9961),
     'Mn'  : Elem(25, 55, 54.938045),
     'Fe'  : Elem(26, 56, 55.845),
     'Co'  : Elem(27, 59, 58.933195),
     'Ni'  : Elem(28, 59, 58.6934),
     'Cu'  : Elem(29, 64, 63.546),
     'Zn'  : Elem(30, 65, 65.409),
     'Ga'  : Elem(31, 70, 69.723),
     'Ge'  : Elem(32, 73, 72.64),
     'As'  : Elem(33, 75, 74.92160),
     'Se'  : Elem(34, 79, 78.96),
     'Br'  : Elem(35, 80, 79.904),
     'Kr'  : Elem(36, 84, 83.798),
     'Rb'  : Elem(37, 85, 85.4678),
     'Sr'  : Elem(38, 88, 87.62),
     'Y'  : Elem(39, 89, 88.90585),
     'Zr'  : Elem(40, 91, 91.224),
     'Nb'  : Elem(41, 93, 92.90638),
     'Mo'  : Elem(42, 96, 95.94),
     'Tc'  : Elem(43, 98, 98),
     'Ru'  : Elem(44, 101, 10.07),
     'Rh'  : Elem(45, 103, 102.90550),
     'Pd'  : Elem(46, 106, 106.42),
     'Ag'  : Elem(47, 108, 107.8682),
     'Cd'  : Elem(48, 112, 112.411),
     'In'  : Elem(49, 115, 114.818),
     'Sn'  : Elem(50, 119, 118.710),
     'Sb'  : Elem(51, 122, 121.760),
     'Te'  : Elem(52, 128, 127.60),
     'I'  : Elem(53, 127, 126.90447),
     'Xe'  : Elem(54, 131, 131.293),
     'Cs'  : Elem(55, 133, 132.9054519),
     'Ba'  : Elem(56, 137, 137.327),
     'La'  : Elem(57, 139, 138.90547),
     'Ce'  : Elem(58, 140, 140.116),
     'Pr'  : Elem(59, 141, 140.90765),
     'Nd'  : Elem(60, 144, 144.242),
     'Pm'  : Elem(61, 145, 145),
     'Sm'  : Elem(62, 150, 150.36),
     'Eu'  : Elem(63, 152, 151.964),
     'Gd'  : Elem(64, 157, 157.25),
     'Tb'  : Elem(65, 159, 158.92535),
     'Dy'  : Elem(66, 163, 162.5),
     'Ho'  : Elem(67, 165, 164.93032),
     'Er'  : Elem(68, 167, 167.259),
     'Tm'  : Elem(69, 169, 168.93421),
     'Yb'  : Elem(70, 173, 173.04),
     'Lu'  : Elem(71, 175, 174.967),
     'Hf'  : Elem(72, 178, 178.49),
     'Ta'  : Elem(73, 181, 180.94788),
     'W'  : Elem(74, 184, 183.84),
     'Re'  : Elem(75, 186, 186.207),
     'Os'  : Elem(76, 190, 190.23),
     'Ir'  : Elem(77, 192, 192.217),
     'Pt'  : Elem(78, 195, 195.084),
     'Au'  : Elem(79, 197, 196.966569),
     'Hg'  : Elem(80, 201, 200.59),
     'Tl'  : Elem(81, 204, 204.3833),
     'Pb'  : Elem(82, 207, 207.2),
     'Bi'  : Elem(83, 209, 208.9804),
     'Po'  : Elem(84, 209, 209),
     'At'  : Elem(85, 210, 210),
     'Rn'  : Elem(86, 222, 222),
     'Fr'  : Elem(87, 223, 223),
     'Ra'  : Elem(88, 226, 226),
     'Ac'  : Elem(89, 227, 227),
     'Th'  : Elem(90, 232, 232.03806),
     'Pa'  : Elem(91, 231, 231.03588),
     'U'  : Elem(92, 238, 238.02891),
     'Np'  : Elem(93, 237, 237),
     'Pu'  : Elem(94, 244, 244),
     'Am'  : Elem(95, 243, 243),
     'Cm'  : Elem(96, 247, 247),
     'Bk'  : Elem(97, 247, 247),
     'Cf'  : Elem(98, 251, 251),
     'Es'  : Elem(99, 252, 252),
     'Fm'  : Elem(100, 257, 257),
     'Md'  : Elem(101, 258, 258),
     'No'  : Elem(102, 259, 259),
     'Lr'  : Elem(103, 262, 262),
     'Rf'  : Elem(104, 267, 267),
     'Db'  : Elem(105, 268, 268),
     'Sg'  : Elem(106, 271, 271),
     'Bh'  : Elem(107, 272, 272),
     'Hs'  : Elem(108, 277, 277),
     'Mt'  : Elem(109, 276, 276),
     'Ds'  : Elem(110, 281, 281),
     'Rg'  : Elem(111, 280, 280),
     'Cn'  : Elem(112, 285, 285),
     'Uut' : Elem(113, 284, 284),
     'Fl'  : Elem(114, 289, 289),
     'Uup' : Elem(115, 288, 288),
     'Lv'  : Elem(116, 291, 291),
     'Uus' : Elem(117, 293, 293), 
     'Uuo' : Elem(118, 294, 294),
     'Z119': Elem(119, 316, 316),
     'Z120': Elem(120, 318, 318),
     'Z121' : Elem(121, 322, 322)
}

#----- Misc utilities -----


'''
 Purpose  : from the str [start:step:end], derive start, step and end
   input  : in_str => input string, format can be [start:step:end],
                      [start:end] or [start]
            dtype  => the datatype of return, (optional, default [float])
  output  : ifrom, step, ito => [start:step:end]
'''
def bracket_to_steps(in_str, dtype=float) :
    bra = in_str.find('[')
    ket = in_str.find(']')
    index = 0
    colon = []
    while index < len(in_str) :
       index = in_str.find(':', index)
       if index == -1 :
          break
       else :
          colon.append(index)
          index += 1

    if len(colon) == 0 :
       ifrom = dtype(in_str[bra+1:ket])
       ito = ifrom
       step = 0
    elif len(colon) == 1 :
       step = 1
       ifrom = dtype(in_str[bra+1:colon[0]])
       ito = dtype(in_str[colon[0]+1:ket])
    elif len(colon) == 2 :
       ifrom = dtype(in_str[bra+1:colon[0]])
       ito = dtype(in_str[colon[1]+1:ket])
       step = dtype(in_str[colon[0]+1:colon[1]])

    return ifrom, step, ito
'''
 Purpose  : from the str [start:step:end], derive the numpy array
   input  : in_str => input string, format can be [start:step:end],
                      [start:end] or [start]
            dtype  => the datatype of return, (optional, default [float])
  output  : array  => numpy array object from start to end 
'''
def bracket_to_array(in_str, dtype=float) :
    if ':' in in_str :
       ifrom, step, ito = bracket_to_steps(in_str, dtype=dtype) 
       if step == 0 :
          numb = 1
       else :
          numb = int(float(ito - ifrom) / float(step)) + 1
       array = np.linspace(ifrom, ito, num = numb, endpoint = True,
                              retstep = False)
                              #dtype=dtype, axis = 0, retstep = False)
    else :
      tmp = (in_str[in_str.find('[')+len('['):in_str.rfind(']')]).split(',')
      array = np.array([float(i) for i in tmp])
    return array

def from_l_get_kaps(l) :
  if l == 0 :
    return [-1]
  else :
    return [l, -(l+1)]
def from_l_get_js(l) :
  if l == 0 :
    return [0.5]
  else :
    return [l+0.5, l-0.5]

def from_kap_get_lj(kap) :
  if kap > 0 :
    l = kap; j = kap - 0.5
  else :
    l = -kap -1; j = -kap - 0.5
  return l,j

def from_orb_get_nl(t_orb) :
  ia = -1
  for i, w in enumerate(t_orb) :
    if w.isalpha() :
      ia = i
      break
  if ia <= 0 : 
    print(t_orb + " is a wrong input")
    exit()
  elif ('-' in t_orb or '+' in t_orb ) and len(t_orb[ia:]) > 2 :
    print("shouldn't put something like 3spd-")
    exit()
  else :
    n = int(t_orb[0:ia])
    l = AngTab[t_orb[ia:ia+1]]
    return n, l

def print_array(array, File = None, comments = None, sep = ' ') :
  if File == None and comments == None :
    for i in array : print(i, end = '', sep = ' ')
    print('')
  elif File == None and comments != None :
    print(comments, end = '', sep = ' ')
    for i in array : print(i, end = '', sep = ' ')
    print('')
  elif File != None and comments != None :
    File.write(comments+sep)
    for i in array : File.write('{}{}'.format(i,sep))
    File.write('\n')
  else : 
    for i in array : File.write('{}{}'.format(i,sep))
    File.write('\n')

def slogan(txt, File = None, decor = None, comments = None) :
  if File == None and decor == None and comments == None :
    print(txt)
  elif File == None and decor == None and comments != None :
    print(comments+txt)
  elif File == None and decor != None and comments == None :
    print(decor[0]*decor[1]+txt+decor[0]*decor[1])
  elif File == None and decor != None and comments != None :
    print(comments+decor[0]*decor[1]+txt+decor[0]*decor[1])
  elif File != None and decor == None and comments == None :
    File.write(txt+'\n')
  elif File != None and decor == None and comments != None :
    File.write(comments+txt+'\n')
  elif File != None and decor != None and comments == None :
    File.write(decor[0]*decor[1]+txt+decor[0]*decor[1]+'\n')
  elif File != None and decor != None and comments != None :
    File.write(comments+decor[0]*decor[1]+txt+decor[0]*decor[1]+'\n')
  
def num_order(num) :
  if num == 1 : return "1'st"
  elif num == 2 : return "2'nd"
  elif num == 3 : return "3'rd"
  elif num > 0 : return "{}'th".format(num)
  else : 
    print("positive number required")
    exit()

def substr_between(string, head, tail) :
  itail = string.find(tail)
  ihead = string.find(head)
  if ihead > -1 and itail > -1 :
    sub = string[string.find(head)+1:string.find(tail)]
  elif ihead > -1 and itail == -1 :
    sub = string[string.find(head)+1:]
  else :
    print(head, tail, 'wrong')
    exit()
  return sub

def clean_dir(calc_name = 'grasptmp', FilesToDel = None) :
  if 'All' in FilesToDel :
     for i in ['mcp.*', 'rmix.out', 'rcsf.inp', 'rmcdhf.*', 'isodata', '*.stdout', '*.stderr'] :
        print('rm -f ' + calc_name + '/' + i)
        os.system('rm -f ' + calc_name + '/' + i)
  elif FilesToDel != None :
     for i in FilesToDel :
        print("rm -f "+ calc_name + '/' + i)
        os.system('rm -f ' + calc_name + '/' + i)
  else :
     pass
def get_alpha_pos(string) :
  ia = 0
  for i, w in enumerate(string) :
    if w.isalpha() :
      ia = i
      break
  return ia
def get_orbital_set(orbs) :
  orb_set = []; 
  orbs = orbs.rstrip().lstrip()
  if orbs != '' :
    t_orbs = orbs.split(',')
    for t_orb in t_orbs :
      if t_orb[0] == 'n' :
        n = t_orb[1:]
        orb = [n + AngStr[l] for l in range(0,int(n))] 
        orb_set.extend(orb)
      elif 'ano-' in t_orb :
        xx = t_orb.split('ano-')[1]
        for iorb in  xx.split(',') :
          ia = get_alpha_pos(iorb)
          n = iorb[:ia] 
          l = iorb[ia]
          orb = ["{}{}".format(pqn,l)  for pqn in range(AngTab[l]+1, int(n)+1) ]
          orb_set.extend(orb)
          #print(orb)
      else :
        ia = -1
        for i, w in enumerate(t_orb) :
          if w.isalpha() :
            ia = i
            break
        if ia <= 0 : 
          print(t_orb + " is a wrong input")
          exit()
        elif ('-' in t_orb or '+' in t_orb ) and len(t_orb[ia:]) > 2 :
          print("shouldn't put something like 3spd-")
          exit()
        elif '-' in t_orb or '+' in t_orb :
          orb_set.extend([t_orb])
        else :
          n = t_orb[0:ia]
          orb = [n + l for l in t_orb[ia:]] 
          orb_set.extend(orb)
    return orb_set
  else : return orb_set

def is_triangle(Js) :
  result = True
  for i, j in enumerate(Js) :
    OtherJs = [v for i2,v in enumerate(Js) if i2 != i] 
    if j > sum(OtherJs) or j < abs(OtherJs[0] - OtherJs[1]) :
      result = False
  return result

# For the time being, we use the table 4-5 of chap.4-17 (p127)  of Cowan's 
# The theory of atomic structure and spectra (1981)
# seniorty table for jj coupling is found from Nuclear shell theory by 
# A. de-Shalit and I. Talmi
# 
def get_ljw_cup(j,occ) :
  yes_seniority = False
  if j == 0.5  and occ in [0,2] : 
    Js = [0]
    sens = [0] # all paired
  elif j == 0.5  and occ in [1] : 
    Js = [0.5]
    sens = [1]
  elif j == 1.5  and occ in [0,4] : 
    Js = [0]
    sens = [0] # all paired
  elif j == 1.5  and occ in [1,3] : 
    Js = [1.5]
    sens = [1]
  elif j == 1.5  and occ in [2] : 
    Js = [0,2]
    sens = [0,2] # 
  elif j == 2.5  and occ in [0,6] : 
    Js = [0]
    sens = [0] # all paired
  elif j == 2.5  and occ in [1,5] : 
    Js = [2.5]
    sens = [1]
  elif j == 2.5  and occ in [2,4] : 
    Js = [0,2,4]
    sens = [0,2,2]
  elif j == 2.5  and occ in [3] : 
    Js = [1.5,2.5,4.5]
    sens = [3,1,3]
  elif j == 3.5  and occ in [0,8] : 
    Js = [0]
    sens = [0]
  elif j == 3.5  and occ in [1,7] : 
    Js = [3.5]
    sens = [1]
  elif j == 3.5  and occ in [2,6] : 
    Js = [0,2,4,6]
    sens = [0,2,2,2]
  elif j == 3.5  and occ in [3,5] : 
    Js = [1.5,2.5,3.5,4.5,5.5,7.5]
    sens = [3,3,1,3,3,3]
  elif j == 3.5  and occ in [4] : 
    Js = [0,2,2,4,4,5,6,8] # different seniority 
    sens = [0,2,4,2,4,4,2,4]
    yes_seniority = True
  elif j == 4.5  and occ in [0,10] : 
    Js = [0]
    sens = [0]
  elif j == 4.5  and occ in [1,9] : 
    Js = [4.5]
    sens = [1]
  elif j == 4.5  and occ in [2,8] : 
    Js = [0,2,4,6,8]
    sens = [0,2,2,2,2] 
  elif j == 4.5  and occ in [3,7] : 
    Js = [1.5,2.5,3.5,4.5,4.5,5.5,6.5,7.5,8.5,10.5] # seniority
    sens = [] # this will never be used on present atomic code..
    yes_seniority = True
  elif j == 4.5  and occ in [4,6] : 
    Js = [0,0,2,2,3,4,4,4,5,6,6,6,7,8,8,9,10,12]
    sens = np.ones_like(Js) * occ  # seniority
    yes_seniority = True
  elif j == 4.5  and occ in [5] : 
    Js = [0.5,1.5,2.5,2.5,3.5,3.5,4.5,4.5,4.5,5.5,5.5,6.5,6.5,\
         7.5,7.5,8.5,8.5,9.5,10.5,12.5] # seniority
    sens = np.ones_like(Js) * occ  # 
    yes_seniority = True
  else : # something wrong, but make it work around.TODO
    Js = []
    sens = []
    yes_seniority = False
  return Js, sens, yes_seniority

def get_subsh_J_sen_list(kap, occ) :
  J_list = []; sen_list = []
  l, j = from_kap_get_lj(kap)
  #print('j1j2j3(1/2,1/2,1)',is_triangle([0.5,1.5,1.0]))
  Js_list, sen_list, yes_sen = get_ljw_cup(j,occ)
  return Js_list, sen_list, yes_sen


def partition_subshell(sh) :
  orb = sh.Orbit; occ = sh.occ
  l = sh.Orbit.l
  kaps = from_l_get_kaps(sh.Orbit.l)
  # fullioccupied subshells 
  if occ == MaxOcc[orb.l] :
    J_list = [np.zeros_like(kaps)]
    senior_list = [np.zeros_like(kaps)]
    iocc_list = np.ones_like(kaps)
    for i in range(len(kaps)) :
       l, j = from_kap_get_lj(kaps[i])
       iocc_list[i] = MaxOcc_J2[int(j*2.0)]
    occ_list = [iocc_list]
    cups = [[RSubShell(orb.n, kaps[i], iocc_list[i], 0, 0) for i in range(len(kaps)) ]]
  elif orb.l == 0 : 
    J_list = [ [occ] ] # ns^0 or ns^1
    senior_list = [[occ]]
    occ_list = [[occ]]
                         # n, kap, occ, j, sen) :
    cups = [[RSubShell(orb.n, -1, occ,0.5*occ,occ) ]]
  else :
    J2_list = [];senior_list = []; occ_list = []; cups = []
    cup1 = []; cup2= []
    max_occ1 = min(2*l, occ)
    minocc = occ-2*l-2
    if minocc < 0 : 
      min_occ1 = 0
    else : min_occ1 = minocc
    l, j = from_kap_get_lj(kaps[0])
    for occ1 in range(min_occ1, max_occ1 + 1) :
      #print('l j occ1, occ2', l, j, occ1, occ-occ1)
      # present atomic code has not such cfp, cfgp, seniority... TODO
      if j == 4.5 and occ1 in [3,7,4,6,5] : continue 
      #J_sub1, J_sub2 actual Js, not J2....
      J_sub1, Sen_sub1, yes_sen1 = get_subsh_J_sen_list(kaps[0], occ1)
      J_sub2, Sen_sub2, yes_sen2 = get_subsh_J_sen_list(kaps[1], occ-occ1)
# Later avoid append... TODO
      for i1,j1 in enumerate(J_sub1) :
        for i2,j2 in enumerate(J_sub2) :
          J2_list.append(np.array([j1,j2]))
          senior_list.append(np.array([Sen_sub1[i1], Sen_sub2[i2]]))
          occ_list.append(np.array([occ1, occ-occ1]))
          cups.append([RSubShell(orb.n,kaps[0],occ1,j1,Sen_sub1[i1]),
                       RSubShell(orb.n,kaps[1],occ-occ1,j2,Sen_sub2[i2])]) # i1 i2 ....
  return cups 
# end function partition_subshell

def which_block(symblocks, Jtot, P) :
  for i,v in enumerate(symblocks) :
     if v.J == Jtot and P == v.p : return i
  return None # error message

def from_cup_chain_get_cfglist(sushells_list, symblock, orb_all, yes_debug = False) :
  norbs = 0
  orb_id_dict = {}
  for iorb in orb_all : # note orb_all might contain void place holders
    n, l = from_orb_get_nl(iorb)
    for kap in from_l_get_kaps(l) :
      orbname = '{}{}'.format(n,KapStr(kap))
      orb_id_dict[orbname] = norbs
      norbs += 1

  cfgs_group = [[]]* len(symblock)

  #print('nsym:',len(cfgs_group))
  for subsh in sushells_list :
    if yes_debug : 
      print('couple subshells to CSF:')
      print(" " +' '.join([i.label + '{}'.format(i.J) for i in subsh]))
    chain_list = couple_subsh(subsh, yes_debug) #RelCSF(subsh)
    for icfg in chain_list :
      which_blk = which_block(symblock, icfg.J, icfg.P)
      if yes_debug :
        #print(' '.join([sh.label for sh in icfg.sh_chain]))
        print('JP isym', icfg.J, icfg.P, which_blk)
        print(' '.join(["{} ".format(j12) for j12 in icfg.J12chain]))
      if not which_blk is None : 
        xx = list(cfgs_group[which_blk])
        xx.extend([icfg])
        cfgs_group[which_blk] = xx
  return cfgs_group

class Grid :
  def __init__(self, Control) :
      self.N = Control['N']
      self.H =  Control['H']
      self.HP = Control['HP']
      self.RHN =Control['RHN']

class NucInfo :

  def __init__(self, Elem, CalcDir = './', NucDetail = None) : 
    if NucDetail == None :
      self.NucSpin = 1.0; self.Dipole = 1.0; self.Qpole = 1.0; self.RedefNucForm = 'n'
    else :
      self.NucSpin, self.Dipole, self.Qpole = NucDetail['NucSpin'], \
         NucDetail['Dipole'], NucDetail['Qpole']
      if 'RNucRMS' in NucDetail and 'RNucSkin' in NucDetail:
         self.RedefNucForm = 'y'
         self.RNucRMS, self.RNucSkin = NucDetail['RNucRMS'], NucDetail['RNucSkin']
    self.Z = Elem.Z
    self.A = Elem.A
    self.mass = Elem.mass


class Orbit :
  def __init__(Orbit_self, n = None, l = None) :
    if n is not None :
      Orbit_self.n = n
    else : Orbit_self.n = -1
    if l is not None :
      Orbit_self.l = l
    else : Orbit_self.l = -1

  #def __del__(Orbit_self) :
  #  pass 

class Shell :
  def __init__(Shell_self,string = None):
    if string is not None :
      for i, v in enumerate(string) :
         if v.isalpha() : 
           n = int(string[0:i]); l = AngTab[v]
           occ = int(string[i+1:]); break
      Shell_self.Orbit = Orbit(n,l)
      Shell_self.occ = int(occ)
    else :
      Shell_self.Orbit = Orbit()
      Shell_self.occ = 0
  #def __del__(Shell_self) :
  #  pass
def from_parity_to_str(parity) :
  if parity == 1.0 :
    return '+'
  else : return '-'

def from_j_angular_str(j) :
  if j == 0.0 : return "0"
  elif(j % 1.0 == 0) : return "{}".format(int(j)) 
  else : return "{}/2".format(int(2.0*j))
def Rshell_lab(string) :
  tmp = string.split('(')
  occ = tmp[1].split(')')[0].lstrip()
  nl = tmp[0].rstrip()
  return nl+"^"+occ
class RSubShell : # relativistic -subshell
  def __init__(rsubshell_self, n, kap, occ, j, sen) :
    rsubshell_self.n = n
    rsubshell_self.kap = kap
    rsubshell_self.orb = "{}{}".format(n,KapStr(rsubshell_self.kap))
    rsubshell_self.l, rsubshell_self.j = from_kap_get_lj(kap)
    rsubshell_self.occ = occ
    rsubshell_self.J = j
    rsubshell_self.sen = sen
    rsubshell_self.label = "{}{:2s}({:2d})".format(rsubshell_self.n, \
                            KapStr(rsubshell_self.kap), rsubshell_self.occ)
    rsubshell_self.Jstr = from_j_angular_str(j)

def angular_moment_add(j1, j2) :
  return np.arange(np.abs(j1-j2), j1+j2+1.0, 1.0)

class cup_chain :
  def __init__(self, sh_chain, J12chain) :
    self.sh_chain = sh_chain
    self.J12chain = J12chain
    self.J = J12chain[-1]
    self.P = (-1) ** sum([sh.l * sh.occ for sh in sh_chain])
    
  def extend_chain(self, sh, yes_debug = False) :
    sh_chain = list(self.sh_chain) # note this is pointer arithmic
    sh_chain.extend([sh])
    Jtot = angular_moment_add(sh.J, self.J12chain[-1])
    self.P += (-1)** (sh.l * sh.occ)
    if yes_debug :print('add++j1',sh.J, 'j2',self.J12chain[-1], 'j12',Jtot)
    J12chain_new_list = []
    for J12_new in Jtot :
      J12chain_old = list(self.J12chain) 
      if yes_debug : print('old',J12chain_old)
      J12chain_old.extend([J12_new])
      if yes_debug : print('new',J12chain_old)
      J12chain_new_list.append(J12chain_old)
    return sh_chain, J12chain_new_list


def couple_subsh(rsubshs, yes_debug = False) :
  chain_list = []
  for i, sh in enumerate(rsubshs) :
    if yes_debug : print(i,'>> ++ '+sh.label)
    if i == 0 : 
       chain_list = [cup_chain([sh],[sh.J])]
       if yes_debug :
         print("J12 new:")
         print("        "+'{}'.format(sh.J))
    else : 
       chain_list_old = list(chain_list)
       chain_list = []
       for chain in chain_list_old :
         sh_chain_new, J12chain_new_list  = chain.extend_chain(sh)
         if yes_debug : 
           print("J12 new:")
           for j12chain in J12chain_new_list :
             print("        "+' '.join(["{}".format(j12) for j12 in j12chain] ))
         for j12_new in J12chain_new_list :
           chain_list.append(cup_chain(sh_chain_new, j12_new))
  return chain_list

class Config :
#Config::
  def __init__(Config_self, string = None):
    if string != None :  
      Config_self.shells = Config_self.from_ref_str_shell(string)
      Config_self.str = [string]
    else :
      Config_self.shells = []
      Config_self.str = []

#Config::
  def from_ref_str_shell(Config_self, string) :
    shells = []
    for i in string.split(shell_delm) :
      shells.append(Shell(i))
    return shells
#Config::
  def get_occ(Config_self) : 
    occ = [ sh.occ for sh in Config_self.shells]
    return occ  
#Config::
  def get_ne_act(Config_self) : 
    ne = np.sum([ sh.occ for sh in Config_self.shells])
    return ne  
#Config::
  def append_orb(Config_self) :
    pass
  #def __del__(Config_self) :
  #  pass

# TODO : set up occupation restrictions. FAC style
class CSFBasis :
#CSFBasis::
  def expand_shell_abbr(self, string) :
    shells = []
    for i, v in enumerate(string) :
       if v.isalpha() : 
         ni = string[0:i-1]
         occi = string[i+1:]
         break
    n = int(ni); occ = int(occi)     
    L = range(0,n); 
      
    return shells

#CSFBasis::
  def FAC_str_to_cfg_list(self, cfg_str) :
      cfg = [] 
      return cfg

#CSFBasis::
  def get_orblist(self, string) :
    orb_list = []
    for orb in string.split(',') :
      if 'n' in orb :
         n = int(orb[orb.find('n')+1:])
         for l in range(n) :
           orb_list.append(Orbit(n,l))
      elif ':' in orb :
         n = 0; ia = 0
         j = orb.find(':')
         for i, x in enumerate(orb) : 
           if x.isalpha() : 
             ia = i
             continue
         l = orb[ia:]
         for n in range(int(orb[:j]), int(orb[j+1:ia])+1) :
           #print(n,l)
           orb_list.append(Orbit(n,AngTab[l]))

      else :
         n = 0 
         for i, x in enumerate(orb) : 
           if x.isalpha() : 
             n = int(orb[0:i])
             continue
         for l in orb[i:] :
           orb_list.append(Orbit(n,AngTab[l]))
    return orb_list

#CSFBasis::
  def get_excite_elec_number(self, string) :
    if string == '' : return []
    else : return [ExctStr[i] for i in string.split(',')]
  
#CSFBasis::
  def quick_order_shells(self, ref) :
    nl = np.array([ 100 * sh.Orbit.n + sh.Orbit.l for sh in ref.shells])
    indx = np.argsort(nl, axis = 0, kind = 'quicksort')
    ref_ = Config()
    ref_.shells = []
    for i in range(len(ref.shells)) :
      ref_.shells.append(ref.shells[indx[i]])
    return ref_

#CSFBasis::
  def move_e_betw_orbs(self, REF, iorb, jorb) :
     REF_ = self.quick_order_shells(REF)
     SHELL = [] 
     for sh in REF_.shells : #range(len(SHELL)) :
       if sh.Orbit.n == iorb.n and sh.Orbit.l == iorb.l :
         if sh.occ - 1 > 0 :
           sh_new = Shell('{}{}{}'.format(iorb.n, AngStr[iorb.l], sh.occ - 1))
           SHELL.append(sh_new)
       elif sh.Orbit.n == jorb.n and sh.Orbit.l == jorb.l :
         sh_new = Shell('{}{}{}'.format(jorb.n, AngStr[jorb.l], sh.occ + 1))
         SHELL.append(sh_new)
       else :
         sh_new = Shell('{}{}{}'.format(sh.Orbit.n, AngStr[sh.Orbit.l], sh.occ))
         SHELL.append(sh_new)
     return SHELL
  
#CSFBasis::
  def get_shell_occ(self, cfg, orbit) :
    for ish in cfg.shells :
      if ish.Orbit.n == orbit.n and \
         ish.Orbit.l == orbit.l : return ish.occ
    return 0

#CSFBasis::
  def get_shell_indx_in_cfg(self, cfg, orbit) :
    for i, sh in enumerate(cfg.shells) :
      if sh.Orbit.n == orbit.n and \
         sh.Orbit.l == orbit.l : return i
    return -1
 
#CSFBasis::
  def shell_list_to_string(self, shells) :
    string = ''
    for i, sh in enumerate(shells) :
      string += '{:d}{:s}{:d}'.format(sh.Orbit.n, AngStr[sh.Orbit.l], sh.occ)
      if i != len(shells) -1 : string += shell_delm
    #string += '\b'
    return string

#CSFBasis::
  def meet_excite_restric(self, cfg, excite_restric) :
    if excite_restric == '' : return True

    criteria = excite_restric.split(',')
    #print(excite_restric, criteria)
    for icr in criteria :
      if '<=' in icr :
        condi = '<='
      elif '>=' in icr : 
        condi = '>='
      elif '<' in icr :
        condi = '<'
      elif '>' in icr :
        condi = '>'
      elif '=' in icr :
        condi = '='
      else : 
        print('wrong input for CSFBasis restrict')
        exit()
      lhs, rhs = icr.split(condi)[0], icr.split(condi)[1]
      #print(condi, rhs)
      nocc = int(rhs)
      orbs = np.empty(0, dtype = str)
      for i in lhs.split('+') :
        orbs = np.append(orbs, self.get_orblist(i.rstrip().lstrip()))
      nocc_sum = 0
      for iorb in orbs :
        #print(iorb)
        for sh in cfg.shells :
          if sh.Orbit.n == iorb.n and sh.Orbit.l == iorb.l :
           nocc_sum += sh.occ
      if condi == '<=' and nocc_sum > nocc : return False
      if condi == '>=' and nocc_sum < nocc : return False
      if condi == '<' and nocc_sum >= nocc : return False
      if condi == '>' and nocc_sum <= nocc : return False
      if condi == '=' and nocc_sum != nocc : return False
    return True

#CSFBasis::
  def ref_str_to_cfg_list(self, ctr_str) :
    if 'Excite' in ctr_str :
      ref_cfg = substr_between(ctr_str.split('ref')[1],':',';')
    else :
      ref_cfg = ctr_str.split('ref')[1].split(':')[1]
    if 'orbs' not in ctr_str : orb_set = ''
    else : orb_set = substr_between(ctr_str.split('orbs')[1], '(',')')

    if 'restrict' not in ctr_str : excite_restric = ''
    else : excite_restric = substr_between(ctr_str.split('restrict')[1], ':',';')

    yes_debug = hasattr(self, 'dbg') and 'cfg' in self.dbg and self.dbg['cfg'] 
    if yes_debug : print('interested orbs :',orb_set)
    self.orbs = get_orbital_set(orb_set)
    for iorb in self.orbs :
       if iorb in self.inact_str: 
          print(ctr_str+" contains a closed shell ", self.inact_str )
          print("Hint: please double check orbs:()")
          exit()
       if iorb not in self.orb_all : 
         self.orb_all.append(iorb)
         n, l = from_orb_get_nl(iorb)
         if l == 0 : 
           iorbmax = "{}{} ".format(n,AngStr[l])
           self.orb_all_rel.append(iorbmax)
         else : 
           iorbmin = "{}{}-".format(n,AngStr[l])
           iorbmax = "{}{} ".format(n,AngStr[l])
           self.orb_all_rel.extend([iorbmin,iorbmax])
    if yes_debug : print('ref_config :'+ ref_cfg)
    #print(self.orb_all_rel, 'self.orb_all')
    excite_from = []; excite_to = []
    if 'Excite:' not in ctr_str : 
      excite = ''
      act_orb = ''
    else : 
      ext = substr_between(ctr_str.split('Excite')[1],':', ';')
      act_orb, excite = ext.split('(')[0], ext.split('(')[1].split(")")[0]
      T_excite_from = self.get_orblist(act_orb.split('->')[0])
      T_excite_to = self.get_orblist(act_orb.split('->')[1])
      for iorb in T_excite_from :
        xorb = str(iorb.n)+AngStr[iorb.l]
        if xorb in self.orbs : excite_from.append(iorb)
      for iorb in T_excite_to :
        #print(iorb.n,iorb.l)
        xorb = str(iorb.n)+AngStr[iorb.l]
        if xorb in self.orbs : excite_to.append(iorb)

    excit_ele = self.get_excite_elec_number(excite)
    REF_ = Config(ref_cfg)
    self.ne_act = REF_.get_ne_act()
    cfg = [REF_]
    ref_parity = (-1)** sum([iorb.Orbit.l * iorb.occ for iorb in REF_.shells])
    if yes_debug : print('Parity : ', ref_parity); 
    #print('parity', self.Parity, ref_parity)
    if not ref_parity in self.Parity : 
      return [] #####
    head = 0; 
    for ne_excite in excit_ele :
      tail = len(cfg)
      if yes_debug : print('Move nele_exc: ',num_order(ne_excite), 
            ' electron based on previous step from Line :(',head, '->',tail,')')
      for iref_cfg in range( head, tail) :
        for iorb in reversed(excite_from) :
          iocc = self.get_shell_occ(cfg[iref_cfg], iorb)
          iorb_indx = self.get_shell_indx_in_cfg(cfg[iref_cfg], iorb)
          li = cfg[iref_cfg].shells[iorb_indx].Orbit.l
          ni = cfg[iref_cfg].shells[iorb_indx].Orbit.n
          if iocc <=0 : continue
          for jorb in excite_to :
            # filter out the transition between orbitals of different parity 
            #if abs(jorb.l - iorb.l) % 2 !=  0 : continue # check later on because 2-electron transition .
            jorb_indx = self.get_shell_indx_in_cfg(cfg[iref_cfg], jorb)
            if jorb_indx == iorb_indx : continue
            # excite to a new orbital.
            T_cfg = Config()
            T_cfg.shells = copy.deepcopy(cfg[iref_cfg].shells[:])
            SSS = '  From {} :'.format(iref_cfg)+self.shell_list_to_string(T_cfg.shells)
            if jorb_indx == -1 :
              T_cfg.shells.append(Shell())
              T_cfg.shells[-1].occ = 0
              T_cfg.shells[-1].Orbit = jorb
              jorb_indx = len(T_cfg.shells) - 1
            lj = T_cfg.shells[jorb_indx].Orbit.l
            jocc= self.get_shell_occ(T_cfg, jorb)
            nj = T_cfg.shells[jorb_indx].Orbit.n
            if nj < ni : continue # excite upward only to avoid double counting
            elif nj == ni and lj < li : continue
            if jocc >= MaxOcc[lj] : continue
            SSS += " ({:d}{:s}->{:d}{:s})".format(ni, AngStr[li], nj, AngStr[lj])
            result = self.move_e_betw_orbs(T_cfg, iorb, jorb)
            # if not repeated then put in the stack. 
            T2 = Config()
            T2.shells = result
            T2.str = self.shell_list_to_string(result)
            stamp = [i.str for i in cfg]
            if T2.str not in stamp :
              cfg.append(T2)
              SSS += ' = ' + self.shell_list_to_string(result)
            elif T2.str in stamp :
              SSS += ' = ' + self.shell_list_to_string(result) + '[X]:repeat'
            if yes_debug : print(SSS)
            # clean up
            del T_cfg; del T2
      head = tail; tail = len(cfg)
    cfg_ = []
    for icfg in cfg :
      this_parity = (-1)** sum([iorb.Orbit.l * iorb.occ for iorb in icfg.shells])
      if this_parity == ref_parity and self.meet_excite_restric(icfg,excite_restric) : cfg_.append(icfg)
    return cfg_


#CSFBasis::
  def expand(self, CSFDetail) :
    cfg = []
    self.orb_all = []
    self.orb_all_rel = []
    for ctr_str in CSFDetail['config'] :
      if 'ref:' not in ctr_str and \
         'FAC'  not in ctr_str : 
         print("Config str wrong: " + ctr_str +
               "\n <at least one reference cfg should be given>\n"
               " Or give FAC style config strings")
         exit()
      elif 'ref' in ctr_str :
        cfg.extend(self.ref_str_to_cfg_list(ctr_str))
      elif 'FAC' in ctr_str :
        cfg.extend(self.FAC_str_to_cfg_list(ctr_str))
    yes_debug = hasattr(self, 'dbg') and 'cfg' in self.dbg and self.dbg['cfg'] 
    if yes_debug : print('#all orbs:', self.orb_all)
    if yes_debug : print("# summarize")
    self.actorb = {}
    for iorb in self.orb_all :
      n, l = from_orb_get_nl(iorb)
      L_ = AngStr[l] 
      if L_ not in self.actorb :
        self.actorb[L_] = n
      elif L_ in self.actorb and n > self.actorb[L_] :
        self.actorb[L_] = n
 
    stamp = []
    index = []
    for idx, icfg in enumerate(cfg):
      string = self.shell_list_to_string(icfg.shells) 
      if string not in stamp : 
        index.append(idx)
        stamp.append(string)
        if yes_debug : print(string + ' fresh')
      else :
        if yes_debug : print(string + ' repeated')

    return [cfg[i] for i in index] 

#CSFBasis::
  def count_elec(self) :
    self.ne_core = Nelec_of_CloseCore[self.CloseCore]
    self.nelec = self.ne_act + self.ne_core
    return self.nelec

#CSFBasis::
  def get_symblocks(self, CSFDetail) :
    if 'J2Low' in CSFDetail and 'J2High' in CSFDetail :
      self.J2Low = str(CSFDetail['J2Low']) # 2J 
      self.J2High = str(CSFDetail['J2High']) # 2J 
      J2list = np.arange(CSFDetail['J2Low'], CSFDetail['J2High'] + 2,2)
    elif 'JLow' in CSFDetail and 'JHigh' in CSFDetail : 
      self.J2Low = str(CSFDetail['JLow'] * 2.0) # 2J 
      self.J2High = str(CSFDetail['JHigh'] * 2.0) # 2J 
      #print(self.J2Low, self.J2High)
      num = int(CSFDetail['JHigh'] - CSFDetail['JLow'] + 1)
      J2list = np.linspace(CSFDetail['JLow'] * 2.0 , CSFDetail['JHigh'] *2.0 , num = num) 
    elif 'JList' in CSFDetail :
      J2list = np.array(CSFDetail['JList'])*2.0
    elif 'J2List' in CSFDetail :
      J2list = np.array(CSFDetail['J2List'])
    else :
      self.J2Low = None
      self.J2High = None
      nelec = self.count_elec()
      if nelec % 1 == 0 : 
         JLow = 0; JHigh = 0
      else :
         JLow = 0.5; JHigh = 0.5
      J2list = range(Jlow * 2.0, JHigh * 2.0 + 2, 2.0)

    #print( J2list)
    symblock_allow = []
    for i in J2list :
       #for j in self.Parity :
      if 1 in self.Parity : symblock_allow.append(symmetry(i/2.0,1))
      if -1 in self.Parity : symblock_allow.append(symmetry(i/2.0,-1))
         #print(i/2.0,j)
    #print(symblock_allow)
    return symblock_allow

#CSFBasis::
  def __init__(self, CSFDetail, calc_name = 'grasptmp') :
    if 'InactShell' in CSFDetail :
      Inact_shell_str = CSFDetail['InactShell'].split(shell_delm)
      Shell_list = []
      for sh_str in Inact_shell_str :
        Shell_list.append(Shell(sh_str))
      self.InactShell = Shell_list
    else :
      self.InactShell = []
    if 'CloseCore' in CSFDetail :
      self.CloseCore = CloseCoreTab[CSFDetail['CloseCore']]
    else :
      self.CloseCore = 0 # No close core specified.

    self.inact_str = np.array(['{}{}'.format(i.Orbit.n, AngStr[i.Orbit.l]) for i in self.InactShell])
    if RelConf_of_CloseCore[self.CloseCore] != '':
      self.inact_str = np.append(self.inact_str, RelConf_of_CloseCore[self.CloseCore].split('_'))
    print('inact',self.inact_str)

    if 'Parity' in CSFDetail :
      if isinstance(CSFDetail['Parity'], int) :
        self.Parity = [CSFDetail['Parity']]
      else : self.Parity = CSFDetail['Parity']
    else : self.Parity = [1,-1] 

    self.cfg = self.expand(CSFDetail)
    self.symblock_allow = self.get_symblocks(CSFDetail)

  #def __del__(self) :
  #  pass
  
  def extend(self) :
    pass
  
  def tailor(self) :
    pass 


class WaveFunc :
#WaveFunc::
  def get_wavefunc_type(self, orb_set, inact, ctr_str) :
    wave_type = {}
    for istr in ctr_str.split(';') :
      wf = []
      xx = istr.split(':')
      orb, typ = xx[0], xx[1]
      orbs = get_orbital_set(orb)
      print(orb, orbs)
      print(orb_set)
      if len(inact) != 0 :
        orb_set_core = np.concatenate((orb_set, inact))
      else : 
        orb_set_core = orb_set.copy()
      for iorb in orbs :
        for jorb in orb_set_core :
          if jorb in iorb and (not jorb in wf) : wf.append(iorb) # avoid repeated orbitals
      wave_type[typ] = wf
    self.wave_type = wave_type

#WaveFunc::
  def __init__(self, OrbSet = None, CloseCore = None, Control = None) :
    if 'type' == None or OrbSet == None : 
      print('No initial guess of orbitals find')
      exit()
    else : self.get_wavefunc_type(OrbSet, CloseCore, Control['type'])
    
  #def __del__(self) :
  #  pass

class level :
  def __init__(self, E = None, mix = None, cf_id = None, J = None, PI = None, sym_id = None) :
    self.E = E
    self.mix = mix
    self.cf_id = cf_id
    self.J = J
    self.P = PI
    self.JP = J+PI
    self.sym = sym_id

class Angular :
  def __init__(self, Control) :
    if 'kind' in Control :
      self.kind = Control['kind']
    else :
      self.kind = 'parallel' # parallelel
    if 'interact' in Control :
      self.interact = Control['interact']
    else :
      self.interact = 'full'
class Sym :
  def __init__(self, sym, ncsf) :
    self.ncsf = ncsf
    self.sym = sym

class SCF :
#SCF::
  def __init__(self, Control) :
    print('init SCF.......')
    if 'QED' in Control :
      self.QED = Control['QED']
    else : self.QED = None
    if 'converg' in Control :
      self.converg = Control['converg']
    if 'maxiter' in Control :
      self.maxiter = Control['maxiter']
    else :
      self.maxiter = 0
    if 'block' in Control :
      print(Control['block'])
      tt = Control['block']
      self.weight = tt['weight']
      self.level = tt['level']
      print(self.level)
      self.num_optim_level = 0
      for i in self.level : self.num_optim_level += len(i)
    else :    
      self.blocks = None
    if 'spec_orb' in Control :
      self.spec_orb = Control['spec_orb'] 
    else : self.spec_orb = '*'
    if 'update_orb' in Control :
      self.update_orb = Control['update_orb'] 
    else : self.update_orb = '*'
    if 'order' in Control :
      self.order = Control['order'] 
    else : self.order = 'update'
    if 'accurary' in Control :
      self.accuracy = Control['accuracy'] 

class CI :
#CI::
  def __init__(self, Control) :
    print('init CI.......')
    if 'QED' in Control :
      self.QED = Control['QED']
    else : self.QED = None
    if 'restart' in Control :
      self.restart = Control['restart']
    if 'perturb' in Control :
      self.perturb = Control['perturb'] # a dictionary
    if 'block' in Control :
      self.level = Control['block']
    else :    
      self.level = None

def get_num_meaningful_shells(sh_chain) :
   for i, sh in enumerate(reversed(sh_chain)) :
     if sh.occ != 0 : break
   return len(sh_chain) - i

def Dirac_Eorb(sh, Ze) :
    alpha = 1./137.0
    n = float(sh.n)
    j = float(from_kap_get_lj(sh.kap)[1])
    d = j + 0.5 - ((j+0.5)**2 - Ze**2 * alpha **2)**0.5
    Eorb = 1.0 / (1.0 + Ze**2 * alpha**2 / (n - d)**2 )**0.5
    return Eorb

class calc_setup :
  def __init__(self, calc_name, clear = None, clear_what = None, exec_grasp = False, version = 'default', **Reigen) :
    self.version = 'default' #self.Version(version)
    self.yes_Reigen = False
    self.exec_grasp = exec_grasp
    if len(Reigen) > 0 : self.yes_Reigen = True
    if self.yes_Reigen :
      if 'kcmax' in Reigen : self.kcmax = Reigen['kcmax']
      else : self.kcmax = 9 
      if 'nrang2' in Reigen : self.nrang2 = Reigen['nrang2']
      else : self.nrang2 = 50 
      if 'n_phy_targ' in Reigen : self.n_phy_targ = Reigen['n_phy_targ']
      else : self.n_phy_targ =  None
      if 'sym_blocks' in Reigen : self.sym_blocks = Reigen['sym_blocks']
      else : self.sym_blocks = None
      if 'opt' in Reigen : self.opt = Reigen['opt']
      else : self.opt = 7
      if 'ipolph' in Reigen : self.ipolph = Reigen['ipolph']
      else : self.ipolph = 2
      if 'idiag' in Reigen : self.idiag = Reigen['idiag']
      else : self.idiag = 0

      if self.kcmax %2 == 0 :
        print('kcmax should be odd number!')
        exit()

    self.calc_name = calc_name
    if not os.path.isdir(calc_name) :
      os.mkdir(calc_name)
    elif clear is not None and clear:
      slogan('Tidy up b4 calc.', File = None, decor = ('*', 10), comments = '#')
      if clear_what == None : clear_what = ['All']
      clean_dir(calc_name, clear_what)
    if (not os.path.isdir(calc_name+'/Reigen-inner/')) and self.yes_Reigen:
      os.mkdir(calc_name+'/Reigen-inner/')

    self.log = open(calc_name+'/calc.log', 'a')
    if clear is not None and clear:
      slogan("Tidy up: {} ".format(self.calc_name), File = self.log, decor=('', 0), comments = '#')
      for i in clear_what : self.log.write("{} ".format(i) )
      self.log.write('\n')
#calc_setup::
  def __del__(self) :
    if hasattr(self, 'scf') : 
       print('delet scf')
       delattr(self, 'scf')
    if hasattr(self, 'grid') : 
       print('delet grid')
       delattr(self, 'grid')
    if hasattr(self, 'dbg') : 
       print('delet dbg')
       delattr(self, 'dbg')
    if hasattr(self, 'clight') : 
       print('delet clight')
       delattr(self, 'clight')
    if hasattr(self, 'Nuc') : 
       print('delet Nuc')
       delattr(self, 'Nuc')

    print("Clearing up calculation setup")
    slogan("Clearing up calculation setup", self.log, decor = ('*',10), comments = '#')
    self.log.close()
    print('*'*10)
#calc_setup::
  def Clight(self, clight) :
    self.clight = clight
#calc_setup::
  def Grid(self, Control) :
    self.grid = Grid(Control)
#calc_setup::
  def Version(self, Control = "default") :
    self.version = Control
    print('Version:', self.version)
#calc_setup::
  def Debug(self, Control) :
    self.dbg = Control

#calc_setup::
  def execute(self, control) :
    print(self.version)
    print(control)
    if self.version == 'default' : self.grasp_exe = grasp_exe_deft
    elif self.version == 'mem' : self.grasp_exe = grasp_exe_deft
    elif self.version == 'big' : self.grasp_exe = grasp_exe_big
    elif self.version == 'mpi' : self.grasp_exe = grasp_exe_mpi
    CMD_LIST = 'nuc,csf,wave,angular,scf,ci,rmat-target'
    control = control.lower()
    self.final_key = 0
    Purpose = {'nuc':'\tGenerate nuclear infomation',
               'csf':'\tGenerate Atomic State Functions',
               'split':'\trcsfsplit',
               'wave':'\tEstimate test orbital function basis',
               'angular_mpi':'\tAngular integral',
               'angular':'\tAngular integral',
               'scf_mpi':"\tscf calculation for a limited set of lower states [mpi]",
               'scf_mem':"\tscf calculation for a limited set of lower states [memory]",
               'scf':"\tscf calculation for a limited set of lower states [single]",
               'ci_mpi': "\t\tConfiguration Interation of full configuration set",
               'ci': "\t\tConfiguration Interation of full configuration set"}
    exe = {'nuc': 'rnucleus',
           'csf': 'rcsfgenerate',
           'split':'rcsfsplit',
           #'guess':'rcsfinteract',
           'wave': 'rwfnestimate',
           'angular_mpi':'rangular_mpi',
           'angular':'rangular',
           'scf_mpi':'rmcdhf_mpi',
           'scf_mem':'rmcdhf_mem',
           'scf':'rmcdhf',
           'ci_mpi': 'rci_mpi',
           'ci': 'rci'
           }
    File = {'nuc': 'iso',
            'csf': 'rcfg',
            'split':'split',
            #'guess':'rcfginter',
            'wave': 'erwf',
            'angular_mpi':'ang',
            'angular':'ang',
            'scf_mpi':'rscf',
            'scf_mem':'rscf',
            'scf':'rscf',
            'ci_mpi': 'rci',
            'ci': 'rci'}
    Result = {
            'nuc': ['isodata'],
            'csf': ['rcsf.out', 'clist.new', 'rcsf.log', 'rcsfgenerate.log'],
            'split':['rcsf.out'],
            #'guess':'rcfginter',
            'wave': ['rwfn.inp', 'erwf.dbg', 'erwf.sum'],
            'angular_mpi':['mcp.*', 'rangular.log'],
            'angular':['mcp.*', 'rangular.log'],
            'scf_mpi':['rwfn.out','rmix.out', 'TARGET.INP', 'rmcdhf.sum', 'rmcdhf.log'],
            'scf_mem':['rwfn.out','rmix.out', 'TARGET.INP', 'rmcdhf.sum', 'rmcdhf.log'],
            'scf':['rwfn.out','rmix.out', 'TARGET.INP', 'rmcdhf.sum', 'rmcdhf.log'],
            'ci_mpi': [self.calc_name+'.csum', self.calc_name+'.cm', self.calc_name+'.clog',
                   self.calc_name+'.w', self.calc_name+'.c'],
            'ci': [self.calc_name+'.csum', self.calc_name+'.cm', self.calc_name+'.clog',
                   self.calc_name+'.w', self.calc_name+'.c']
    }
    
    Depend = {
            'nuc': {'exe':'cp', 'in':[], 'out':[],'backup_inp':[]},
            'csf': {'exe':'cp', 'in':[], 'out':[], 'backup_inp':[]},
            'split':{'exe':'cp', 'in':['rcsf.out'], 'out':['rcsf.inp'], 'backup_inp':[]},
            'wave':{'exe':'cp', 'in':['rcsf.out'], 'out':['rcsf.inp'], 'backup_inp':[]},
            'angular_mpi':{'exe':'cp', 'in':['rcsf.out'], 'out':['rcsf.inp'], 'backup_inp':[]},
            'angular':{'exe':'cp', 'in':['rcsf.out'], 'out':['rcsf.inp'], 'backup_inp':[]},
            'scf_mpi':{'exe':'cp', 'in':[], 'out':[], 'backup_inp':[]},
            'scf_mem':{'exe':'cp', 'in':[], 'out':[], 'backup_inp':[]},
            'scf':{'exe':'cp', 'in':[], 'out':[], 'backup_inp':[]},
            'ci_mpi': {'exe':'cp', 'in':['rcsf.out', 'rwfn.out'], 'out':[self.calc_name+'.c', self.calc_name+'.w'],
                               'backup_inp':['rcsf.out', 'rwfn.inp']},
            'ci': {'exe':'cp', 'in':['rcsf.out', 'rwfn.out'], 'out':[self.calc_name+'.c', self.calc_name+'.w'],
                               'backup_inp':['rcsf.out', 'rwfn.inp']}
    }
    Report = {
            'nuc': {'file':[], 'key':[]},
            'csf': {'file':['rcfp.stdout'], 'key':['']},
            'split':{'file':[], 'key':[]},
            #'guess':'rcfginter',
            'wave':{'file':[], 'key':[]},
            'angular_mpi':{'file':[], 'key':[]},
            'angular':{'file':[], 'key':[]},
            'scf_mpi':{'file':[], 'key':[]},
            'scf':{'file':[], 'key':[]},
            'ci_mpi': {'file':[], 'key':[]},
            'ci': {'file':[], 'key':[]}
    }
    cwd = os.getcwd()
    os.chdir(self.calc_name)
    for cmd in CMD_LIST.split(',') :
      print(cmd)
      if cmd in control :
         print("\nrun "+cmd + ":" + Purpose[cmd])
         slogan("run "+cmd, File = self.log,  decor = ('*', 10), comments = '#')
         slogan(Purpose[cmd], File = self.log, decor = ('', 0), comments = '#')
         
         print('now in :'+ self.calc_name )
         #File_in = open("{}/{}.inp".format(self.calc_name, File[cmd]),'r')
         File_in = open("{}.inp".format( File[cmd]),'r')
         File_out = open("{}.stdout".format( File[cmd]),'w')
         File_err = open("{}.stderr".format(File[cmd]),'w')
         if 'csf' not in control and cmd == 'scf' : self.get_sym('./')
         for i, pre in enumerate(Depend[cmd]['in']) :
           if os.path.isfile(pre) :
             exec_cmdl = "{} {} {}".format(Depend[cmd]['exe'], 
                         pre, Depend[cmd]['out'][i])
           elif os.path.isfile(Depend[cmd]['backup_inp'][i]) :
             exec_cmdl = "{} {} {}".format(Depend[cmd]['exe'], 
                         Depend[cmd]['backup_inp'][i], Depend[cmd]['out'][i])

           self.log.write('\t'+exec_cmdl)
           print(exec_cmdl)
           os.system(exec_cmdl)
         if 'mpi' in self.version and cmd in ['scf','angular','ci']:
           exec_cmdl = "mpirun -np {} {}/{}_mpi".format(NCPUCORES, self.grasp_exe, exe[cmd])
         elif 'mem' in self.version and cmd in ['scf'] :
           exec_cmdl = "{}/{}_mem".format(self.grasp_exe, exe[cmd])
         else :
           exec_cmdl = "{}/{}".format(self.grasp_exe, exe[cmd])
         self.log.write('\t'+exec_cmdl)
         print(exec_cmdl)
         process = Popen(exec_cmdl.split(), stdout=File_out, stdin = File_in, stderr = File_err)
         exit_code = process.wait()         
         self.final_key += exit_code
         print('input  \t: {}/{}.inp'.format(self.calc_name, File[cmd]))
         print('output \t: {}/{}.stdout'.format(self.calc_name, File[cmd]))
         print('error  \t: {}/{}.stderr'.format(self.calc_name, File[cmd]))
         print('exit_code \t\t: {}'.format(exit_code))
         self.log.write('\n\t\tinput  : {}/{}.inp '.format(self.calc_name, File[cmd]))
         self.log.write('\n\t\toutput : {}/{}.stdout'.format(self.calc_name, File[cmd]))
         self.log.write('\n\t\terror  : {}/{}.stderr'.format(self.calc_name, File[cmd]))
         self.log.write('\n\t\texit_code: {} \n'.format(exit_code))
         if exit_code == 0 : 
           for res in Result[cmd] : 
             if res == 'TARGET.INP' :
               if self.yes_Reigen :
                 mv_file = "mv {} Reigen-inner/".format(res)
                 print(mv_file)
                 self.log.write('\t'+mv_file+'\n')
                 os.system(mv_file)
         else : 
           print("Fail!")
           exit()
    if self.final_key == 0 : 
      sss = '==>All right '
    else : sss = '==> Something wrong'
    print(sss)
    slogan(sss, File = self.log, decor = ('', 0), comments = '#')
    os.chdir(cwd)
    print('cwd '+os.getcwd())
#calc_setup::
  def print_nucleus(self) :
    if self.Nuc.RedefNucForm == 'n' :
       txt = \
           "{}  # Z\n".format(self.Nuc.Z) + \
           "{}  # A\n".format(self.Nuc.A) + \
           "{}  # Redefine Nuclear Shape?\n".format(self.Nuc.RedefNucForm) + \
           "{}  # mass\n".format(self.Nuc.mass) + \
           "{}  # Nuclear Spin (hbar)\n".format(self.Nuc.NucSpin) + \
           "{}  # Nuclear dipole momentum (Barn)\n".format(self.Nuc.Dipole) + \
           "{}  # Nuclear quadropole momentum (Barn)\n".format(self.Nuc.Qpole) 
    elif self.Nuc.RedefNucForm == 'y' :
      txt = \
           "{}  # Z\n".format(self.Nuc.Z) + \
           "{}  # A\n".format(self.Nuc.A) + \
           "{}  # Redefine Nuclear Shape?\n".format(self.Nuc.RedefNucForm) + \
           "{}  # Nuclear radius root mean squared\n".format(self.Nuc.RNucRMS) + \
           "{}  # skin thickness of Nuclear radius\n".format(self.Nuc.RNucSkin) + \
           "{}  # mass\n".format(self.Nuc.mass) + \
           "{}  # Nuclear Spin (hbar)\n".format(self.Nuc.NucSpin) + \
           "{}  # Nuclear dipole momentum (Barn)\n".format(self.Nuc.Dipole) + \
           "{}  # Nuclear quadropole momentum (Barn)\n".format(self.Nuc.Qpole) 

    NF = open(self.calc_name+"/iso.inp", 'w'); NF.write(txt); NF.close()

    comment = "#---- Get nuclear info ---- "+self.calc_name+"/iso.inp\n"
    comment += txt
    comment += "#---- Output file : " + self.calc_name + '/isodata\n' 
    yes_debug = hasattr(self, 'dbg') and 'nuc' in self.dbg and self.dbg['nuc'] 
    if yes_debug : print(comment)

#calc_setup::
  def NucInfo(self, Elem, NucDetail = None) : 
    self.Nuc = NucInfo(Elem, self.calc_name, NucDetail)
    self.print_nucleus()
    if self.exec_grasp :
      self.execute('Nuc')
    else :
      pass

#calc_setup::
  def is_orb_Inact(self, n, l) :
    sh2 = '{}{}'.format(n, AngStr[l])
    for ish, sh in enumerate(self.CSF.InactShell) :
      if n == sh.Orbit.n and l == sh.Orbit.l : return ish
    for sh in RelConf_of_CloseCore[self.CSF.CloseCore].split('_') :
      if sh == sh2 : return ish
    return -1 

#calc_setup::
  def is_orb_in_cfg(self, n, l, cfg) :
    for ish, sh in enumerate(cfg.shells) :
      if n == sh.Orbit.n and l == sh.Orbit.l : return ish
    return -1
#calc_setup::
  def get_Rel_Eorbs(self, cfg) :
    #for ic in cfg : print(ic)
    if cfg == [] : 
      return 0.0
    else :
      Eorbs = [Dirac_Eorb(sh, self.Ze) * sh.occ for sh in cfg.sh_chain]
      #print([sh.label for sh in cfg.sh_chain])
      #print(Eorbs)
      return np.sum(Eorbs)

#calc_setup::
  def jjcup_rcfg_list(self,symblock_allow) :
    yes_debug = hasattr(self, 'dbg') and 'cfg' in self.dbg and self.dbg['cfg']
    rcfg_list =[ [] ]* len(symblock_allow) 
    sym_actual = np.zeros(len(symblock_allow), dtype = int)
    print('number symblock allowed', len(symblock_allow))
    #rcfg_list = []
    print('building ASF chain for self.CSF.cfg ( # =', len(self.CSF.cfg))
    start = time.time()
    for icfg in self.CSF.cfg :
      cup_chain_list = []
      for sh in icfg.shells :
        n = sh.Orbit.n
        if sh.Orbit.l > 0 : n_subsh = 2
        else : n_subsh = 1
        shell_cup = partition_subshell(sh)
        cup_chain_list_old = list(cup_chain_list)
        cup_chain_list = []
        if cup_chain_list_old == [] :
          if yes_debug : print("First:"+'shell couple schemes:',len(shell_cup))
          for new_cup in shell_cup : 
            cups = []
            cups.extend(new_cup) # subshells
            if yes_debug :
               print(" " +' '.join([i.label + '{}'.format(i.J) for i in cups]))
               print("----")
            cup_chain_list.append(cups)
        else : 
          if yes_debug :
            print('Push: shell couple schemes:',len(shell_cup))
            print("++ {}{} --> ".format(n,AngStr[sh.Orbit.l]))
          for cups_old in cup_chain_list_old : # looping all occ's, J's and (nu's)
            if yes_debug :
              print("old:"+' '.join([i.label + '{}'.format(i.J) for i in cups_old]))
              print('----') 
              print('new :')
            for new_cup in shell_cup : 
               cups_now = list(cups_old)
               cups_now.extend(new_cup) # stiching subshells
               if yes_debug : print(" " +' '.join([i.label + '{}'.format(i.J) for i in cups_now]))
               cup_chain_list.append(cups_now)
            if yes_debug :print('----') 
      cfg_group = from_cup_chain_get_cfglist(cup_chain_list, symblock_allow, self.CSF.orb_all, yes_debug)
      if yes_debug : print('***********')
      for ii, igroup in enumerate(cfg_group) : 
        #print('group',ii,'has ',len(igroup))
        #for isym in range(len(rcfg_list)) : print('isym',isym,'has',len(rcfg_list[isym]))
        for jj, config in enumerate(igroup) :
          isym = which_block(symblock_allow, config.J, config.P)
          if not isym is None : 
              xx = list(rcfg_list[isym])
              xx.extend([config])
              rcfg_list[isym] = xx
              sym_actual[isym] += 1
          if yes_debug : 
            print('  conf',jj,'JP=',config.J, config.P,'isym', isym)
            label = ' '.join([ '{}{}'.format(sh.label, sh.J) for sh in config.sh_chain ])
            J12   = ' '.join([ '{}  '.format(j12) for j12 in config.J12chain ])
            print(' '*5+label)
            print(' '*5+J12)
        if yes_debug : 
          for isym in range(len(rcfg_list)) : print('isym',isym,'has',len(rcfg_list[isym]))
      if yes_debug : print('***********')
    end = time.time()
    print('jjcup took {} s'.format(end-start))
    print("Sort the configurations in each block accod. to Rel. Eorb")
    start = time.time()
    rcfg_list2 = list(rcfg_list)
    self.nele = self.CSF.count_elec()
    self.Ze = self.Nuc.Z - self.nele + 1. # Gauss law.
    #print(rcfg_list2[0])
    for isym, cfgs in enumerate(rcfg_list2) : 
      Eorbs = [self.get_Rel_Eorbs(cfg) for cfg in cfgs ]
      indx = np.argsort(Eorbs)
      #print(Eorbs-Eorbs[0])
      #print('indx', indx)
      rcfg_list[isym] = [rcfg_list2[isym][i] for i in indx]
    end = time.time()
    print('sorting took {} s'.format(end-start))
    return rcfg_list, sym_actual
# end function jjcup_rcfg_list

#calc_setup::
  def print_CSF(self) :
    FL = open(self.calc_name + '/rcfg.inp', 'w')
    txt = '*\n'  # default ordering.
    txt += '{}\n'.format(self.CSF.CloseCore) # core configuration

    common_inact_str = ''
    for sh in self.CSF.InactShell :
      if sh.occ <= 0 : continue
      common_inact_str += "{}{}({},i)".format(sh.Orbit.n, AngStr[sh.Orbit.l], sh.occ)

    for icfg in self.CSF.cfg : 
      str_cfg = common_inact_str
      for sh in icfg.shells :
        if sh.occ <= 0 : continue
        shell_str = "{}{}({},i)".format(sh.Orbit.n, AngStr[sh.Orbit.l], sh.occ)
        str_cfg += shell_str
      txt += str_cfg + '\n'
    FL.write(txt+'\n');  #\n to terminate the cfg list
    actorb = [str(self.CSF.actorb[l])+l for l in self.CSF.actorb]
    FL.write(','.join(actorb))
    FL.write('\n') # activa orbital
    FL.write("{}, {}\n".format(int(float(self.CSF.J2Low)), int(float(self.CSF.J2High)))) # Always note that J is here 2*J
    FL.write('0\nn') # 0 excitation number, no need to specify again. n : don't generate further.
    FL.close()
    # genreate input files for 'rwfp.x'
    FL = open(self.calc_name + '/rwf.in', 'w')
    norbs = 0
    for iorb in self.CSF.orb_all :
      n, l = from_orb_get_nl(iorb)
      norbs += len(from_l_get_kaps(l))

    FL.write('{} {}\n'.format(norbs, 0.0)) # norbs, nmin <- not useful..
    for iorb in self.CSF.orb_all :
      n, l = from_orb_get_nl(iorb)
      for j in from_l_get_js(l) : 
        FL.write("{:.1f} {:.1f} {:.1f} \n".format(n,l,j))
    FL.close()

    if self.yes_Reigen :
      FL = open(self.calc_name + '/Reigen-inner/orbcsf.inp', 'w')
      ncfg = len(self.CSF.cfg)
      norbs = len(self.CSF.orb_all)
      txt = '{} '.format(ncfg)  #number of NR-configurations
      txt += '{} #number of NR-cfgs and number of NR-orbtials\n'.format(norbs) #number of NR-orbtials
      
      for iorb in self.CSF.orb_all : 
        n, l = from_orb_get_nl(iorb)
        txt += '{} {} #n and kappa for {}{}{}\n'.format(n, -(l+1),n,AngStr[l],l+0.5) # write kappa for the j+1/2 spinor
        orb = self.is_orb_Inact(n, l) 
        if orb >= 0 :
           for i in range(0, ncfg) : txt += '{} '.format(self.CSF.InactShell[orb].occ)
           txt +='\n'
        elif iorb in Conf_of_CloseCore[self.CSF.CloseCore]:
           for i in range(0, ncfg) : txt += '{} '.format(MaxOcc[l])
           txt +='\n'
        else :
           for i in range(0, ncfg) : 
             orb = self.is_orb_in_cfg(n, l, self.CSF.cfg[i]) 
             if orb >= 0 :  
               txt += '{} '.format(self.CSF.cfg[i].shells[orb].occ)
             else : txt += '0 '
           txt +='\n'
             
      FL.write(txt+'\n');  #\n to terminate the cfg list
      FL.close()
      FL = open(self.calc_name + '/Reigen-inner/ORBS.INP', 'w')
      nelec = sum([sh.occ for sh in self.CSF.cfg[0].shells]) + \
              Nelec_of_CloseCore[self.CSF.CloseCore]
      occ_kappa = []; kbmax = 0
      for iorb in self.CSF.orb_all :
        n, l = from_orb_get_nl(iorb)
        if kbmax < l * 2 + 1 :
          if l == 0 : occ_kappa.extend([n])
          else : occ_kappa.extend([n,n])
        else :
          if l == 0 : occ_kappa[0] = max(n, occ_kappa[0])
          else : 
            occ_kappa[2*l-1] = max(n, occ_kappa[2*l-1])
            occ_kappa[2*l] = max(n, occ_kappa[2*l])
        kbmax = max(kbmax, l * 2 + 1)
      txt = 'DSTG1 {} \n'.format(self.calc_name)  #Title
      txt += '&ORBS\n' # Fortran namespace 
      txt += '   KBMAX  = {} \n'.format(kbmax)
      txt += '   KCMAX  = {} \n'.format(self.kcmax)
      txt += '   MINNQN = '
      for i in range(0, kbmax) : txt +="{} ".format(0)
      txt += '\n'
      txt += '   MAXFUL = '
      for i in range(0, kbmax) : txt +="{} ".format(0)
      txt += '\n'
      txt += '   MAXNLG = '
      for i in range(0, kbmax) : txt +="{} ".format(occ_kappa[i])
      txt += '\n'
      txt += '   MAXNQN = '
      for i in range(0, kbmax) : txt +="{} ".format(occ_kappa[i])
      txt += '\n'
      txt += '   NELC   = {} \n'.format(nelec)
      txt += '   NRANG2 = {} \n'.format(self.nrang2)
      txt += '   NZ     = {} \n'.format(self.Nuc.Z)
      txt += '&END'
      FL.write(txt)
      FL.close()

      FL = open(self.calc_name + '/Reigen-inner/INTS.INP', 'w')
      FL.write('&INTS  \n   \n&END')
      FL.close()

      FL = open(self.calc_name + '/Reigen-inner/DSTG2.INP', 'w')
      txt = 'DSTG2 {} \n'.format(self.calc_name)  #Title
      txt += '&DSTG2  IPOLPH={} NMAN={} OPT={} NWM={} '.format(self.ipolph, ncfg, self.opt, norbs)
      if self.n_phy_targ is not None :
        txt += 'NAST={} '.format(self.n_phy_targ)
      else : txt += 'NAST= '
      if self.idiag is not None :
        txt += 'idiag={} '.format(self.idiag)
      else : txt += 'idiag= '
      txt += '&END\n'
      txt += '&ANGOPT &END\n'
      txt += '&JVALUE &END\n'
      if self.sym_blocks is not None :
        for sym in self.sym_blocks :
          txt += '&SYM JTOT={} NPTY={} &END\n'.format(sym.J, sym.p)
      txt += '&SYM &END\n' # terminate input file 
      FL.write(txt)
      FL.close()
      
      FL = open(self.calc_name + '/Reigen-inner/dto3.inp', 'w')
      FL.write('{} {}'.format(len(self.sym_blocks),1))
      FL.close()

#calc_setup::
  def get_sym(self, where_to_read = None) :
    if where_to_read == None :
      FL = open('./rcfg.stdout','r')
    else : FL = open(where_to_read+'/rcfg.stdout','r')
    lines = FL.readlines()
    for i, line in enumerate(lines) :
      if 'block  J/P            NCSF' in line :
        break
    block = []
    for line in lines[i+1:] :
      tt = line.split()
      block.append(Sym(tt[1],int(tt[2])))
    self.block  = block

#calc_setup::
  def CSFBasis(self, CSFDetail) :
    #if self.exec_grasp :
      start = time.time()
      self.CSF = CSFBasis(CSFDetail, self.calc_name)
      self.print_CSF()
      end = time.time()
      print("CSFBasis took :{:.1f} sec".format(end - start))
      start = time.time()
      self.csf_list, self.sym_actual = self.jjcup_rcfg_list(self.CSF.symblock_allow)
      end = time.time()
      self.gen_csl_list()
      self.get_sym(self.calc_name)
      start = time.time()
      #print('printing took {}s'.format(start - end))
    #else : pass

  def gen_csl_list(self) :
    FL = open(self.calc_name +'/rcfg.stdout', 'w')
    FL.write('block  J/P            NCSF\n')
    i = 0
    print(self.sym_actual)
    self.csf_compact = {} 
    for j, val in enumerate(self.sym_actual) :
      if val > 0 :
        i += 1
        sym = self.CSF.symblock_allow[j]
        #print(j, i, sym.J, sym.p, val)
        FL.write("{} {}{} {}\n".format(i, from_j_angular_str(sym.J), from_parity_to_str(sym.p), val))
    FL.close()
    FL = open(self.calc_name +'/rcsf.out','w')
    FL.write('Core subshells:\n')
    #FL.write(" ".join(["{:>5s}".format(i) for i in RelConf_of_CloseCore[self.CSF.CloseCore].split('_')]))
    print(self.CSF.inact_str, 'inact')
    FL.write(" ".join(["{:>5s}".format(i) for i in self.CSF.inact_str]))
    FL.write('\n')
    FL.write('Peel subshells:\n')
    X = ''
    for i in self.CSF.orb_all_rel : 
       if not i in self.CSF.inact_str : X += "{:>5s}".format(i)
    FL.write(X+'\n')
    FL.write("CSF(s):\n")

    csf_blocks = self.csf_list
    len_shell = 9
    print('print nsym', len(csf_blocks))
    isym_atcual = 0
    for isym, block in enumerate(csf_blocks) :
      if isym_atcual != 0 and len(block) > 0 : FL.write(' *\n')
      if len(block) > 0 : isym_atcual += 1
      #print('isym', isym, 'ncfg', len(block) )
      start = time.time()
      if len(block) > 0 :
        JP = from_j_angular_str(block[0].J12chain[-1]) + from_parity_to_str(block[0].P)
        self.csf_compact[JP] = np.empty(len(block), dtype = object)
      for icfg, config in enumerate(block) :
        label = ''; JJ = ''; J12 = ''
        num_non_vanishJ = 0
        num_shell_trim = get_num_meaningful_shells(config.sh_chain)
        string = '}'.join(["{}[{}]{}".format(Rshell_lab(sh.label), \
                               from_j_angular_str(sh.J), \
                               from_j_angular_str(config.J12chain[i])) \
                               for i, sh in enumerate(config.sh_chain) if sh.occ != 0])
        self.csf_compact[JP][icfg] = string 

        for i, sh in enumerate(config.sh_chain[:num_shell_trim]) :
          this_shell_is_shown = False
          #if sh.J != 0.0 : num_non_vanishJ += 1
          if not sh.occ in [0,MaxOcc_J2[int(sh.j*2.0)]] : num_non_vanishJ += 1
          if sh.occ == 0 :
            label += '' 
          else : 
            label += '{:>9s}'.format(sh.label)
            this_shell_is_shown = True
          # RSubshell.j is the orbital j (J is the subshell one)
          if sh.J == 0.0 and sh.occ in [MaxOcc_J2[int(sh.j*2.0)]]: 
            JJ += ' ' * len_shell
          elif sh.J == 0.0 and sh.occ in [0]: 
            JJ += ''
          elif sh.J == 0.0 :  # ^1S shell with even-number of electrons
            JJ += '{:9d}'.format(sh.sen, 0)
          elif sh.j == 3.5 and sh.occ == 4 and sh.J in [4.0, 2.0] : 
            JJ += '{:4d};{:>4s}'.format( sh.sen, from_j_angular_str(sh.J) )
          else : JJ += '{:>9s}'.format( from_j_angular_str(sh.J) )

          # 
          if num_non_vanishJ < 2 : 
            if num_shell_trim == 1 :
              #J12 += '{:>10s}'.format(from_j_angular_str(config.J12chain[i]))
              J12 += '{:>9s}'.format(from_j_angular_str(config.J12chain[i]))
            elif i == num_shell_trim - 1:
              #J12 += '{:>10s}'.format(from_j_angular_str(config.J12chain[i]))
              J12 += '{:>7s}'.format(from_j_angular_str(config.J12chain[i]))
            #elif i > 1 and config.J12chain[i-1] == 0.0 and config.J12chain[i] != 0.0:
            #  J12 += '{:>10s}'.format(from_j_angular_str(config.J12chain[i]))
            elif sh.occ != 0 :
              J12 += ' ' *  (len_shell + 1)
          else : 
            # Always putout the last shell, only if they are occupied, naturally
            if i == num_shell_trim - 1: 
              #J12 += '{:>10s}'.format(from_j_angular_str(config.J12chain[i]))
              J12 += '{:>7s}'.format(from_j_angular_str(config.J12chain[i]))
            elif sh.J != 0.0 and not sh.occ in [0]:
              #J12 += '{:>10s}'.format(from_j_angular_str(config.J12chain[i]))
              J12 += '{:>9s}'.format(from_j_angular_str(config.J12chain[i]))
            else :
              J12 += ''
              #if sh.occ in [0]:
              #  J12 += ''
              #if sh.J == 0.0 : 
              #  J12 += ' ' * len_shell

        J12 += from_parity_to_str(config.P)
        FL.write(label+'\n')
        FL.write(JJ+'\n')
        FL.write(J12+'\n')
      end = time.time()
      #print('took {}s'.format(end -start))
    FL.close()

#calc_setup::
  def print_wavefunc(self) :
    yes_debug = hasattr(self, 'dbg') and 'wave' in self.dbg and self.dbg['wave'] 
    if yes_debug : print(self.Wave.wave_type)
    FL = open(self.calc_name+'/erwf.inp', 'w')
    yes_default = False
    if (not hasattr(self,'dbg') or not self.dbg['wave']) and \
       not hasattr(self,'grid') and not hasattr(self,'clight') : 
       FL.write('y\n')  # do as default
       yes_default = True
    else : FL.write('n\n')  

    if hasattr(self, 'dbg') and self.dbg['wave'] : 
      FL.write('y\n') # print debug
      FL.write('\n') # default debug file name erwf.dbg
      # default debug option all allowed. #machine constants
      # physical constants # RADGRD # NUCPOT # TFPOT # LODCSL
      FL.write('y\ny\ny\ny\ny\ny\n') 
      FL.write('\n') # keep default erwf.sum
    elif not yes_default : FL.write('n\n\n') # dont print debug and keep default erwf.sum
   
    if hasattr(self, 'clight') or hasattr(self, 'grid') :
      FL.write('y\n') # change c-light or grid
    elif not yes_default : FL.write('n\n')

    if hasattr(self, 'clight') :
      FL.write('y\n{}\n'.format(self.clight)) # change c-light 
    elif not yes_default : FL.write('n\n')
    
    if hasattr(self, 'grid') :
      FL.write('y\n{}\n{}\n{}\n{}\n'.format(self.grid.RHN, 
               self.grid.H, self.grid.HP,self.grid.N)) # change grid
    elif not yes_default : FL.write('n\n')

    
    for typ in self.Wave.wave_type.keys() :
      if typ == 'TF' :
        FL.write('{}\n'.format(2))
      elif typ == 'H' :
        FL.write('{}\n'.format(3))
      else :
        FL.write('{}\n'.format(1))
        FL.write('{}\n'.format(typ))
      for iorb in self.Wave.wave_type[typ] : 
        if '-' in iorb or '+' in iorb:
          FL.write('{} '.format(iorb))
        elif 's' in iorb : 
          FL.write('{} '.format(iorb))
        else : FL.write('{}* '.format(iorb))
      FL.write('\n')
    FL.write('n\n')  # further revise?

#calc_setup::
  def WaveFunc(self, Control) :
    self.Wave = WaveFunc(self.CSF.orb_all, self.CSF.inact_str, Control)
    self.print_wavefunc()
    if self.exec_grasp :
      self.execute('wave')
    else :
      pass

#calc_setup::
  def print_angular(self) :
    yes_debug = hasattr(self, 'dbg') and 'angular' in self.dbg and self.dbg['angular'] 
    if yes_debug : print(self.angular)
    FL = open(self.calc_name+'/ang.inp', 'w')
    if self.angular.interact == 'full' :
      FL.write('{}\n'.format('y'))
    else :
      FL.write('{}\n'.format('n'))
    FL.close()

#calc_setup::
  def Angular(self, Control) :
    self.angular = Angular(Control)
    self.print_angular()
    if self.exec_grasp :
      self.execute('angular')
    else :
      pass 

#calc_setup::
  def print_scf(self) :
    scf = self.scf
    yes_default = False
    yes_debug = hasattr(self, 'dbg') and 'scf' in self.dbg and self.dbg['scf'] 
    if yes_debug : print('scf debug')

    FL = open(self.calc_name+'/rscf.inp', 'w')
    if (not hasattr(self, 'dbg') or not self.dbg['scf']) and \
       not hasattr(self, 'clight') and \
       not hasattr(self, 'grid') and not hasattr(scf, 'accuracy') \
       and not hasattr(scf, 'converg') :
      FL.write('y\n') # Default input
      yes_default = True
    else :
      FL.write('n\n') # Default input
    
    if hasattr(self, 'dbg') and self.dbg['scf'] : 
      FL.write('y\n') # Debug here
      FL.write('\n') # Default debug name
      print('dbg scf')
      #machine physic FNDBLK Hamiltonian 
      #eigenvectors RADGRD NUCPOT LODRWF 
      #I(ab) Slater progress plots 
      #plot*2 exchange plot_Vx 
      #direct plot_VJ  LODCSL T 
      #V
      for i in range(0,21) : FL.write('y\n') 
    elif not yes_default : FL.write('n\n')
    if hasattr(self, 'clight') or hasattr(self, 'grid') :
      FL.write('y\n')
    elif not yes_default : FL.write('n\n')
    if hasattr(self, 'clight') :
      FL.write('y\n{}\n'.format(self.clight))
    elif not yes_default : FL.write('n\n')

    if hasattr(self, 'grid') :
      FL.write('y\n{}\n{}\n{}\n{}\n'.format(self.grid.RHN, 
                 self.grid.H, self.grid.HP,self.grid.N)) # change grid
    elif not yes_default : FL.write('n\n')

    if hasattr(scf, 'accuracy') :
      FL.write('y\n{}\n'.format(self.accuracy))
    elif not yes_default : FL.write('n\n')

    for ib in self.block : 
      sym = ib.sym; ncsf = ib.ncsf
      if sym in scf.level :
        print_array(scf.level[sym], FL)
      else :
        FL.write('\n') # don't optimize this block
    if scf.num_optim_level > 1 : 
      weight_kind ={'standard':5, 'user':9, 'equal':1}
      sel_kind = weight_kind[scf.weight['kind']]
      FL.write('{}\n'.format(sel_kind)) # weight of levels.
      if scf.weight['kind'] == 'user' :
        print_array(scf.weight['ratio'], FL)
   
    print_array(scf.update_orb, FL)
    print_array(scf.spec_orb, FL)
    FL.write('{}\n'.format(scf.maxiter))
    if not yes_default and not hasattr(scf, 'converg') : 
      FL.write('n\n')
      order = {'update':1,'scc':2}
      FL.write('{}'.format(order[scf.order]))
    elif not yes_default : 
      FL.write('xxx')
  
#calc_setup::
  def SCF(self, Control) :
    self.scf = SCF(Control)
    self.print_scf()
    if self.exec_grasp :
      self.execute('scf')
    else :
      pass 

#calc_setup::
  def print_ci(self) :
    ci = self.ci
    yes_default = False
    yes_debug = hasattr(self, 'dbg') and 'ci' in self.dbg and self.dbg['ci'] 
    if yes_debug : print('ci debug')

    FL = open(self.calc_name+'/rci.inp', 'w')
    if (not hasattr(self, 'dbg') or 'ci' not in self.dbg or not self.dbg['ci'] ) and \
       not hasattr(self, 'clight') and \
       not hasattr(ci, 'restart') \
       and not hasattr(ci, 'perturb') :
      FL.write('y # Default options\n') # Default input
      yes_default = True
    else :
      FL.write('n  # Default options\n') # Default input
    FL.write("{}\n".format(self.calc_name))
    if hasattr(ci, 'restart') and ci.restart : FL.write("y # restart \n")
    else : FL.write("n  # restart \n")

    if hasattr(self, 'clight') :
      FL.write('y # modify light speed\n{}\n'.format(self.clight))
    elif not yes_default : FL.write('n # modify light speed\n')


    if hasattr(ci, 'perturb') :
      FL.write('y # CFG perturbation \n')
      for ib in self.block : 
        sym = ib.sym; ncsf = ib.ncsf
        if sym in ci.perturb :
          print_array(ci.perturb[sym], FL)
        else :
          FL.write('\n') # don't optimize this block
    elif not yes_default : FL.write('n # CFG perturbation \n')
    if hasattr(ci, 'QED') : 
      if 'HTrans' in ci.QED and ci.QED['HTrans'] : FL.write('y # H-transverse\n')
      else : FL.write('n # H-transverse\n')
      if 'TransFreq' in ci.QED and ci.QED['TransFreq'] : FL.write('y # Modify transverse frequency\n')
      else : FL.write('n # Modify transverse frequency\n')
      if 'VacPol' in ci.QED and ci.QED['VacPol'] : FL.write('y # Vaccum Polarization\n')
      else : FL.write('n # Vaccum Polarization\n')
      if 'NormMShift' in ci.QED and ci.QED['NormMShift'] : FL.write('y # Normal mass shift\n')
      else : FL.write('n # Normal mass shift\n')
      if 'SpecMShift' in ci.QED and ci.QED['SpecMShift'] : FL.write('y # Specific mass shift\n')
      else : FL.write('n # Specific mass shift\n')
      if 'Self' in ci.QED and ci.QED['Self'] : FL.write('y # Self energy\n')
      else : FL.write('n # Self energy\n')
      if 'Self' in ci.QED and ci.QED['Self'] : FL.write('{}\n'.format(ci.QED['SelfEnergyMaxN']))
    self.n_ci_block_act = 0
    for ib in self.block : 
      sym = ib.sym; ncsf = ib.ncsf
      if sym in ci.level :
        print_array(ci.level[sym], FL)
        self.n_ci_block_act += 1
      else :
        FL.write('\n') # don't optimize this block

#calc_setup::
  def CI(self, Control) :
    if not Control is {} :
      self.ci = CI(Control)
      self.print_ci()
      if self.exec_grasp :
        self.execute('ci')
 

#calc_setup::
  def Read_rmcdhf(self) :
    with open(self.calc_name + '/rmcdhf.sum', 'r') as FL :
      lines = FL.readlines()
      pos_lev_begin = -1; pos_mix = -1; pos_lev_end = -1
      for i, line in enumerate(lines) :
         if 'Level  J Parity       Hartrees'+\
            '              Kaysers         '+\
            '       eV' in line : pos_lev_begin = i + 2 # there is a blank line afterwards
         #if pos_lev_begin !=  -1 and line.rstrip() == '' : 
         if 'Weights of major contributors to ASF:' in line : 
            pos_lev_end = i - 1
         if 'Block Level J Parity      CSF contributions' in line :
            pos_mix = i + 2 
            break
      levels = []
      for i,j in enumerate(range(pos_lev_begin, pos_lev_end)) :
        E = np.NaN 
        tmp = lines[j].replace('D', 'E').split()
        E = float(tmp[5])
        J = tmp[1]; PI = tmp[2]
        tmp = lines[i*2+pos_mix].split()
        sym_id = int(tmp[0]) - 1
        mix = np.array([float(coef) for coef in tmp[4:]])       
        tmp = lines[i*2+1+pos_mix].split()
        cf_id = np.array([int(idx)-1 for idx in tmp])
        levels.append(level(E, mix, cf_id, J, PI, sym_id))
    return levels
#calc_setup::
  def Read_rci92(self) :
    with open(self.calc_name + '/'+self.calc_name+'.csum', 'r') as FL :
      lines = FL.readlines()
      imark = 0 
      levels = []
      #print('self.n_ci_block_act', self.n_ci_block_act)
      for ib in range(self.n_ci_block_act) :
        pos_lev_begin = -1; pos_mix = -1; pos_lev_end = -1
        #print('ib',ib)
        pos_weight = -1
        for i, line in enumerate(lines[imark:]) :
           if 'Eigenenergies:' in line : pos_lev_begin = i + 4 # there is a blank line afterwards
           if 'Weights of major contributors to ASF:' in line : pos_weight = i 
           if 'Energy of each level relative to immediately lower level:' in line : 
              pos_lev_end = i - 1 
           if 'Level J Parity      CSF contributions' in line :
              pos_mix = i + 2 
              break
        imark0 = imark
        if pos_lev_end == -1 and pos_weight != -1 : pos_lev_end = pos_weight - 1
        #print('imark',imark, 'pos_lev_end',pos_lev_end, 'pos_lev_begin',pos_lev_begin)
        imark += pos_mix + (pos_lev_end- pos_lev_begin) * 2 + 1
        pos_lev_begin += imark0; pos_lev_end += imark0; pos_mix += imark0
        for i,j in enumerate(range(pos_lev_begin, pos_lev_end)) :
          E = np.NaN 
          tmp = lines[j].replace('D', 'E').split()
          E = float(tmp[5])
          J = tmp[1]; PI = tmp[2]
          tmp = lines[i*2+pos_mix].split()
          J, P = tmp[1], tmp[2]
          sym_id = -1
          for x, ib in enumerate(self.block) :
            sym = ib.sym;
            if sym == J+P :
              sym_id = x; break
          mix = np.array([float(coef) for coef in tmp[3:]])       
          #print('line', i*2+1+pos_mix)
          #print('pos_mix', pos_mix)
          tmp = lines[i*2+1+pos_mix].split()
          cf_id = np.array([int(idx)-1 for idx in tmp])
          #print('sym_id',sym_id, 'cf_id',cf_id)
          levels.append(level(E, mix, cf_id, J, PI, sym_id))
    return levels
#

#calc_setup::
  def print_lev(self, what = 'scf') :
    if what == 'scf' : fn = self.calc_name + '/level.txt'
    else : fn = self.calc_name + '/ci-level.txt'
    lab = []; Elev = []
    with open(fn, 'w') as FL :
      print('there are {} levels'.format(len(self.levs)))
      Emin = 10000; Eminlab =''
      for i, lev in enumerate(self.levs) :
        ket = '|E{}>'.format(i)
        FL.write("{}{} E{:<4d} {:>13.2f};{:7s} =".format(lev.J, lev.P, i, lev.E, ket)) 
        lab.append("{}{} E{:<4d}".format(lev.J, lev.P, i))
        Elev.append(lev.E)
        if lev.E < Emin :
          Emin = lev.E; Eminlab = ket
        for j, co in enumerate(lev.mix) :
          ket = '|{}>'.format(lev.cf_id[j]) # python fortran index convention
          if co < 0 : FL.write("{:>6.3f}*{:6s}".format(co, ket)) 
          else : FL.write("+{:>5.3f}*{:6s}".format(co, ket)) 
        FL.write('\n')
      FL.write('#----- Minimum ----\n')
      FL.write('{} {}\n'.format(Emin, Eminlab))
      FL.write('#----- Relative energy to the minimum ----\n')
      dE = np.array(Elev) - Emin
      indx = np.argsort(dE)
      for idx in indx :
        FL.write("{:.3f} {:6s}\n".format(dE[idx], lab[idx])) 

    if what == 'scf' : fn = self.calc_name + '/state_expand.txt'
    else : fn = self.calc_name + '/ci-state_expand.txt'
    with open(fn, 'w') as FL :
      for i, lev in enumerate(self.levs) :
        ket = '|E{}>'.format(i)
        FL.write("{}{} E{:<4d} {:>13.10e};{:7s} = ".format(lev.J, lev.P, i, lev.E, ket)) 
        #print('lev',i,'lev.sym',lev.sym, lev.J, lev.P) #, lev.cf_id[0], self.csf_compact[lev.sym][lev.cf_id[0]])
        for j, co in enumerate(lev.mix) :
          #print(lev.sym, lev.cf_id[j])
          #print(self.csf_compact[lev.JP])
          ket = '|{}>'.format(self.csf_compact[lev.JP][lev.cf_id[j]])
          if j != 0 : FL.write(" " * 39 )
          if co < 0 : FL.write("{:>6.3f}*{:6s}\n".format(co, ket)) 
          else : FL.write("+{:>5.3f}*{:6s}\n".format(co, ket)) 
        FL.write('\n')
      FL.write('#----- Minimum ----\n')
      FL.write('{} {}\n'.format(Emin, Eminlab))
#calc_setup::
  def report(self, Control) :
    if 'scf' in Control :
      self.levs = self.Read_rmcdhf()
      self.print_lev('scf')
    if 'ci' in Control :
      self.levs = self.Read_rci92()
      self.print_lev('ci')

class transit :
  def __init__(self, init_name, final_name, opt = 'modify', version = 'default', clear = None, clear_what = None, exec_grasp = False) :
    self.exec_grasp = exec_grasp
    self.version = version
    self.init_name = init_name
    self.final_name = final_name
    self.calc_name = init_name+'---'+final_name
    if not os.path.isdir(self.calc_name) :
      os.mkdir(self.calc_name)
    elif clear is not None and clear:
      slogan('Tidy up b4 calc.', File = None, decor = ('*', 10), comments = '#')
      if clear_what == None : clear_what = ['All']
      clean_dir(self.calc_name, clear_what)

    self.log = open(self.calc_name+'/calc.log', 'a')
    if clear is not None and clear:
      slogan("Tidy up: {} ".format(self.calc_name), File = self.log, decor=('', 0), comments = '#')
      for i in clear_what : self.log.write("{} ".format(i) )
      self.log.write('\n')
    if self.version == 'default' : self.grasp_exe = grasp_exe_deft
    elif self.version == 'mem' : self.grasp_exe = grasp_exe_deft
    elif self.version == 'big' : self.grasp_exe = self.grasp_exe_big
    elif self.version == 'mpi' : self.grasp_exe = self.grasp_exe_mpi
    self.rbiotr()
    self.rtrans(opt)
    #self.execute() # left the user with more control
#transit::
  def rbiotr(self) :
    with open(self.calc_name + '/biotr.inp', 'w') as FL :
      FL.write("y  # Default \ny  # use CI mix\n")
      FL.write("{}\n{}\n".format(self.init_name, self.final_name))
      FL.write("y #transform all J\n")
      self.log.write("# genrate rbiotran inputfile "+ self.calc_name + '/biotr.inp\n')

  def rtrans(self, opt) :
    with open(self.calc_name + '/trans.inp', 'w') as FL :
      if 'default' in opt : 
        FL.write("y  # Default \ny  # use CI mix\n")
        FL.write("{}\n{}\n".format(self.init_name, self.final_name))
        # E1 mode
        FL.write("E1\n")
      else :
        self.log.write("# genrate rtransition inputfile "+ self.calc_name + '/trans.inp\n')
        FL.write("n  # Default \nn  #dump angular \ny  # use CI mix\n")
        FL.write("{}\n{}\n".format(self.init_name, self.final_name))
        FL.write("n #modify Clight\n E1\n")
        FL.write("eV\ny #use a.u. for A B coeff\nn #grid\n")
        
      self.log.write("# genrate rtransition inputfile "+ self.calc_name + '/trans.inp\n')

  def execute(self, control) :
      FLstderr = open(self.calc_name+'/rbiotransform.stderr', 'w')
      FLstdout = open(self.calc_name+'/rbiotransform.stdout', 'w')
      if not os.path.isfile(self.calc_name+'/isodata') :
        cmdl = 'cp -v ' +self.init_name+'/isodata ' + self.calc_name+'/isodata' 
        self.log.write(cmdl+'\n')
        os.system(cmdl)
 
      if not os.path.isfile(self.calc_name+'/'+self.init_name+'.c') :
        cmdl = 'cp -v {}/{}.* {}'.format(self.init_name, self.init_name, self.calc_name)
        self.log.write(cmdl+'\n')
        os.system(cmdl)
      if not os.path.isfile(self.calc_name+'/'+self.final_name+'.c') :
        cmdl = 'cp -v {}/{}.* {}'.format(self.final_name, self.final_name, self.calc_name)
        self.log.write(cmdl+'\n')
        os.system(cmdl)
      os.chdir(self.calc_name)
      if 'rbiotr' in control :
        File_in = open('biotr.inp', 'r')
        if 'mpi' in self.version :
          cmdl = "{}/rbiotransform_mpi".format(self.grasp_exe)
          #process = Popen(cmdl.split(), stdout=FLstdout, stdin = File_in, stderr = FLstderr)
          os.system("{}/rbiotransform_mpi < {} > {}  ".format(self.grasp_exe, 'biotr.inp', 'rbiotransform.stdout' ))
          print('rbiotr_mpi')
          self.log.write("rbiotr_mpi \n")
        else :
          cmdl = "{}/rbiotransform".format(self.grasp_exe)
          #process = Popen(cmdl.split(), stdout=FLstdout, stdin = File_in, stderr = FLstderr)
          os.system("{}/rbiotransform< {} > {}  ".format(self.grasp_exe, 'biotr.inp', 'rbiotransform.stdout' ))
          print('rbiotr ')
          self.log.write("rbiotr \n")
        FLstderr.close(); FLstdout.close(); File_in.close()

      if 'trans' in control :
        FLstderr = open('rtransition.stderr', 'w')
        FLstdout = open('rtransition.stdout', 'w')
        File_in = open('trans.inp', 'r')
        if 'mpi' in self.version :
          cmdl = "{}/rtransition_mpi".format(self.grasp_exe)
          #process = Popen(cmdl.split(), stdout=FLstdout, stdin = File_in, stderr = FLstderr)
          os.system("{}/rtransition_mpi < {} > {}  ".format(self.grasp_exe, 'trans.inp', 'rtransition.stdout' ))
          #exit_code = process.wait()
          print('rtransition_mpi ')
          self.log.write("rtransition_mpi \n")
        else :
          cmdl = "{}/rtransition".format(self.grasp_exe)
          #process = Popen(cmdl.split(), stdout=FLstdout, stdin = File_in, stderr = FLstderr)
          os.system("{}/rtransition < {} > {}  ".format(self.grasp_exe, 'trans.inp', 'rtransition.stdout' ))
          #exit_code = process.wait()
          print('rtransition ')
          self.log.write("rtransition \n")
        FLstderr.close(); FLstdout.close(); File_in.close()
      os.chdir('../')
#transit::
  def __del__(self) :
    print("Clearing up calculation setup")
    slogan("Clearing up calculation setup", self.log, decor = ('*',10), comments = '#')
    self.log.close()
    print('*'*10)
#transit::
  def Clight(self, clight) :
    self.clight = clight
