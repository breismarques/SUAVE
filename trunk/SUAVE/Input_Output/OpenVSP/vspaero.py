#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 22:59:23 2017

@author: root
"""

import SUAVE
from SUAVE.Core import Units, Data

try:
    import sys
    sys.path.insert(0, '/Users/Bruno/OpenVSP/build/python_api')
    import vsp_g as vsp

except ImportError:
    # This allows SUAVE to build without OpenVSP
    pass
import numpy as np


## @ingroup Input_Output-OpenVSP
def analysis(tag):
    
    try:
        vsp.ClearVSPModel()
    except NameError:
        print 'VSP import failed'
        return -1
    
    #open the file created in vsp_write
    
    vsp.ReadVSPFile(tag)
    
    #==== Analysis: VSPAero Compute Geometry ====//
    
    analysis_name="VSPAEROComputeGeometry"
    
    #Set defaults
    
    vsp.SetAnalysisInputDefaults(analysis_name)
    
    #Change some input values
    #    Analysis method
    
    analysis_method1 = vsp.GetIntAnalysisInput( analysis_name, "AnalysisMethod" )

    
    analysis_method=list(analysis_method1)
    
    analysis_method[0] = ( vsp.VORTEX_LATTICE )
    
    
    vsp.SetIntAnalysisInput( analysis_name, "AnalysisMethod", analysis_method )
    
    #list inputs, type, and current values
    
    vsp.PrintAnalysisInputs(analysis_name)
    
    #Execute
    
    rid = vsp.ExecAnalysis( analysis_name );
            
    
    #Get & Display Results
    
    a=vsp.PrintResults(rid);
                      
    print a
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    return 0