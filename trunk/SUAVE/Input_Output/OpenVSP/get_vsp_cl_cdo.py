#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 22:59:23 2017
@author: root
"""

import SUAVE
from SUAVE.Core import Units, Data

import xlwt
import string
from openpyxl import Workbook

try:
    import sys
    sys.path.insert(0, '/Users/Bruno/OpenVSP/build/python_api')
    import vsp_g as vsp
    import vsp as vsp1

except ImportError:
    # This allows SUAVE to build without OpenVSP
    pass
import numpy as np


## @ingroup Input_Output-OpenVSP
def get_vsp_cl_cdo(vehicle,AOA,mach_number):
    
    if 1==1:

        try:
            
            vsp.ClearVSPModel()
            
        except NameError:
            print 'VSP import failed'
            
        vsp.VSPCheckSetup()
        vsp.VSPRenew()


        #open the file created in vsp_write
    
        vsp.ReadVSPFile(tag)
        
        #==== Analysis: VSPAero Compute Geometry to Create Vortex Lattice DegenGeom File ====//
        
        compgeom_name = "VSPAEROComputeGeometry";

        # Set defaults
        vsp.SetAnalysisInputDefaults(compgeom_name);

        # list inputs, type, and current values
        vsp.PrintAnalysisInputs(compgeom_name);

        # Execute
        compgeom_resid=vsp.ExecAnalysis(compgeom_name);

        # Get & Display Results
        vsp.PrintResults( compgeom_resid );
        
    
        #==== Analysis: VSPAero Compute Geometry ====//
    
        analysis_name="VSPAEROSweep"
    
        #Set defaults
    
        vsp.SetAnalysisInputDefaults(analysis_name)
    
        #Change some input values
        #    Analysis method
    
        analysis_method = [vsp.VORTEX_LATTICE]
    
    
        vsp.SetIntAnalysisInput( analysis_name, "AnalysisMethod", analysis_method, 0 )
        
        #Reference geometry set
        
        geom_set=[0]
        vsp.SetIntAnalysisInput( analysis_name, "GeomSet", geom_set );
                               
        #Reference areas, lengths
        
        wing_id=vsp.FindGeomsWithName("main_wing")
        
        sref=[float(0)]*1
        bref=[float(0)]*1
        cref=[float(0)]*1
        
        
        sref[0]=(vsp.GetParmVal(wing_id[0],"TotalArea", "WingGeom"))
        bref[0]=(vsp.GetParmVal(wing_id[0],"TotalSpan", "WingGeom"))
        cref[0]=(vsp.GetParmVal(wing_id[0],"TotalChord", "WingGeom"))
        
        ref_flag=[3]
        
        
        vsp.SetDoubleAnalysisInput( analysis_name, 'Sref', sref )
        vsp.SetDoubleAnalysisInput( analysis_name, 'bref', bref )
        vsp.SetDoubleAnalysisInput( analysis_name, 'cref', cref )
        vsp.SetIntAnalysisInput( analysis_name, "RefFlag", ref_flag )
        
                                 
        #Freestream parameters
        #Alpha
        
        alpha_start=[AOA]
        alpha_end=[AOA]
        alpha_npts=[1]
        
        vsp.SetDoubleAnalysisInput( analysis_name, "AlphaStart", alpha_start )
        vsp.SetDoubleAnalysisInput( analysis_name, "AlphaEnd", alpha_end )
        vsp.SetIntAnalysisInput( analysis_name, "AlphaNpts", alpha_npts )
        
        #Beta
        beta_start=[float(0)]
        beta_end=[float(0)]
        beta_npts=[1]
        
        
        vsp.SetDoubleAnalysisInput( analysis_name, "BetaStart", beta_start )
        vsp.SetDoubleAnalysisInput( analysis_name, "BetaEnd", beta_end )
        vsp.SetIntAnalysisInput( analysis_name, "BetaNpts", beta_npts );
                               
        #Mach
        
        mach_start=[mach_number]
        mach_end=[mach_number]
        mach_npts=[1]
        
        vsp.SetDoubleAnalysisInput( analysis_name, "MachStart", mach_start )
        vsp.SetDoubleAnalysisInput( analysis_name, "MachEnd", mach_end )
        vsp.SetIntAnalysisInput( analysis_name, "MachNpts", mach_npts )
                                
        vsp.Update()
                  
        ##Case Setup
        
        wakeNumIter=[5]
        wakeSkipUntilIter=[6]
        batch_mode_flag=[1]
        
        vsp.SetIntAnalysisInput( analysis_name, "WakeNumIter", wakeNumIter )
        vsp.SetIntAnalysisInput( analysis_name, "WakeSkipUntilIter", wakeSkipUntilIter )
        vsp.SetIntAnalysisInput( analysis_name, "BatchModeFlag", batch_mode_flag )
                                
        vsp.Update()
    
    
        #list inputs, type, and current values
    
        vsp.PrintAnalysisInputs(analysis_name)
        
    
        #Execute
    
        rid = vsp.ExecAnalysis(analysis_name)
            
    
        #Get & Display Results
    
        #vsp.PrintResults(rid)
                        
        #Write in CSV
        
        csvname='Simulation'
        
        vsp.WriteResultsCSVFile(rid,csvname+'.csv')
    
        # Check for errors

        #errorMgr = vsp.ErrorMgrSingleton_getInstance()
        #num_err = errorMgr.GetNumTotalErrors()
        #for i in range(0, num_err):
        #    err = errorMgr.PopLastError()
        #    print("error = ", err.m_ErrorString)
            
        print 'FINISHED VSPAERO SIMULATION'
        
        data = []
        with open(csvname+'.csv') as f:
            for line in f:
                data.append([word for word in line.split(",") if word])
                
        wb = Workbook()
        sheet = wb.active
        for row_index in range(len(data)):
            for col_index, letter in zip(range(len(data[row_index])), string.ascii_uppercase):
                sheet[letter+str(row_index+1)]= data[row_index][col_index]

        wb.save(csvname+'.xlsx')
    
    return 
