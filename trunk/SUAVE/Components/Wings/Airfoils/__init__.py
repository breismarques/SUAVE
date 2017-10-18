## @defgroup Components-Wings-Airfoils Airfoils
# @ingroup Components-Wings
#
# __init__.py
# 
# Created:  
# Modified: Feb 2016, T. MacDonald

# classes
from Airfoil import Airfoil

# functions
from load_airfoils import load_airfoils
from load_airfoils_2D import load_airfoils_2D

# load airfoils
import os
__dir__ = os.path.split(__file__)[0]
_airfoils = load_airfoils(__dir__)
for k,v in _airfoils.items():
    exec('%s = v'%k)
    
import os
__dir__ = os.path.split(__file__)[0]
_airfoils = load_airfoils_2D(__dir__)
for k,v in _airfoils.items():
    exec('%s = v'%k)
#del os, _airfoils, k, v
