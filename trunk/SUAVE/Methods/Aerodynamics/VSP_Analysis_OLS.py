## @ingroup Analyses-Aerodynamics
# SU2_inviscid.py
#
# Created:  Sep 2016, E. Botero
# Modified: Jan 2017, T. MacDonald

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# SUAVE imports
import SUAVE
from SUAVE.Core import Data, Units

# Local imports
from SUAVE.Analyses.Aerodynamics import Aerodynamics
from SUAVE.Input_Output.SU2.call_SU2_CFD import call_SU2_CFD
from SUAVE.Input_Output.SU2.write_SU2_cfg import write_SU2_cfg
from SUAVE.Input_Output.OpenVSP import vsp_write_x57
from SUAVE.Input_Output.OpenVSP import vspaero

# Package imports
import numpy as np
import time
import pylab as plt
import sklearn
from sklearn import gaussian_process
from sklearn import neighbors
from sklearn import svm
import statsmodels.formula.api as smf
import pandas
import math
import os

# ----------------------------------------------------------------------
#  Class
# ----------------------------------------------------------------------
## @ingroup Analyses-Aerodynamics
class VSP_Analysis_OLS(Aerodynamics):
    """This builds a surrogate and computes lift and drag using SU2

    Assumptions:
    Inviscid, subsonic

    Source:
    None
    """   
    def __defaults__(self):
        """This sets the default values and methods for the analysis.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        N/A
        """ 
        self.tag = 'SU2_inviscid'

        self.geometry = Data()
        self.settings = Data()
        #self.settings.half_mesh_flag     = True
        #self.settings.parallel           = False
        #self.settings.processors         = 1
        #self.settings.maximum_iterations = 1500

        # Conditions table, used for surrogate model training
        self.training = Data()        
        self.training.AoA  = np.array([7.0, 0.4, 5.0, 15.0, 40.0,
                                        6.0, 9.0, 5.0, 0.0, 21.0]) * Units.deg
    
        self.training.mach  = np.array([0.44079532457429516, 0.3, 0.5, 0.21, 0.1, 
                                        0.81195286433823222, 0.511229581250084, 0.50823848545971062, 0.50240914350715393, 0.49956803451753434])
    
        self.training.rpm_forward  = np.array([78.0, 0.001, 7570.218883021749, 20.0, 10.0, 
                                               450.0, 350.0, -2000.0, 300.0, 70.0]) * Units['rpm']
                                     
        self.training.rpm_lift  = np.array([46.0, 3784.575248141249, 4000.0, 30.0, -100.0, 
                                            1500.0, 350.0, 750.0, 1200.0, 65.0]) * Units['rpm']
                                     
        self.training.Cp_lift  = np.array([10.0, -1000.00000, 0.0, 200.0, 10.0, 
                                           -10.0, 44.45010057682831, 1000.0, 350.0, -39.573102476674528])
                                     
        self.training.Cp_forward  = np.array([60.4271376019077016, -146.57880339094905, 248.15478376178456, 20.13225978032551, -41.159087723621411,
                                              600.0, 55.065564919157, 122.44107478164513, 1000.0, -495.62502937595718])
                                     
        self.training.Ct_lift  = np.array([0.001, 100.0, -1000.0, 44.0, 20.0,
                                           80.0, 150.0, 900.0, 90.0, 550.0])
                                     
        self.training.Ct_forward  = np.array([10.0, 0.001, 200.0, 15.0, 750.0,
                                             500.0, 1000.0, 650.0, 90.0, 800.0])
        
        self.training.lift_coefficient = None
        self.training.drag_coefficient = None
        self.training_file             = None
        
        # Surrogate model
        self.surrogates = Data()
 
        
    def initialize(self):
        """Drives functions to get training samples and build a surrogate.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        None
        """                     
        # Sample training data
        self.sample_training()
                    
        # Build surrogate
        self.build_surrogate()


    def evaluate(self,state,settings,geometry):
        """Evaluates lift and drag using available surrogates.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        state.conditions.
          mach_number      [-]
          angle_of_attack  [radians]

        Outputs:
        inviscid_lift      [-] CL
        inviscid_drag      [-] CD

        Properties Used:
        self.surrogates.
          lift_coefficient [-] CL
          drag_coefficient [-] CD
        """  
        # Unpack
        surrogates = self.surrogates        
        conditions = state.conditions
        
        mach = conditions.freestream.mach_number
        AoA  = conditions.aerodynamics.angle_of_attack
        engines_number_tot = geometry.propulsors.propulsor.number_of_engines_forward + geometry.propulsors.propulsor.number_of_engines_lift
        rpm_forward = conditions.propulsion.rpm_forward      
        rpm_lift =  conditions.propulsion.rpm_lift        
        rho=conditions.freestream.density
        vel_sound=conditions.freestream.speed_of_sound        
        Cp_lift=conditions.propulsion.propeller_power_coefficient_lift
        Cp_forward=conditions.propulsion.propeller_power_coefficient     
        Ct_lift=conditions.propulsion.propeller_thrust_coefficient_lift
        Ct_forward = conditions.propulsion.propeller_thrust_coefficient_forward
        
        for ii,_ in enumerate(AoA):
            if math.isnan(AoA[ii])==True:
                AoA[ii]=0.0
            if math.isnan(mach[ii])==True:
                mach[ii]=0.0
            if math.isnan(rpm_forward[ii])==True:
                rpm_forward[ii]=0.001
            if math.isnan(rpm_lift[ii])==True:
                rpm_lift[ii]=0.001
            if math.isnan(Cp_forward[ii])==True:
                Cp_forward[ii]=0.0
            if math.isnan(Cp_lift[ii])==True:
                Cp_lift[ii]=0.0
            if math.isnan(Ct_forward[ii])==True:
                Ct_forward[ii]=0.001
            if math.isnan(Ct_lift[ii])==True:
                Ct_lift[ii]=0.001
        
        lift_model = surrogates.lift_coefficient
        drag_model = surrogates.drag_coefficient
        
        # Inviscid lift
        data_len = len(AoA)
        inviscid_lift = np.zeros([data_len,1])
        for ii,_ in enumerate(AoA):
            df=pandas.DataFrame({'AoA': AoA[ii], 'mach': mach[ii], 'rpm_forward': rpm_forward[ii], 'rpm_lift': rpm_lift[ii], 'Cp_lift': Cp_lift[ii], 'Cp_forward': Cp_forward[ii], 'Ct_lift': Ct_lift[ii], 'Ct_forward': Ct_forward[ii]}, index=[0])
            inviscid_lift[ii] = lift_model.predict(df)
            #print "Inviscid_Lift= %f" % inviscid_lift[ii]
            
        conditions.aerodynamics.lift_breakdown.inviscid_wings_lift       = Data()
        conditions.aerodynamics.lift_breakdown.inviscid_wings_lift.total = inviscid_lift
        state.conditions.aerodynamics.lift_coefficient                   = inviscid_lift
        state.conditions.aerodynamics.lift_breakdown.compressible_wings  = inviscid_lift
        
        # Inviscid drag, zeros are a placeholder for possible future implementation
        inviscid_drag                                              = np.zeros([data_len,1])       
        state.conditions.aerodynamics.inviscid_drag_coefficient    = inviscid_drag
        
        return inviscid_lift, inviscid_drag


    def sample_training(self):
        """Call methods to run SU2 for sample point evaluation.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        see properties used

        Outputs:
        self.training.
          coefficients     [-] CL and CD
          grid_points      [radians,-] angles of attack and mach numbers 

        Properties Used:
        self.geometry.tag  <string>
        self.training.     
          angle_of_attack  [radians]
          Mach             [-]
        self.training_file (optional - file containing previous AVL data)
        """               
        # Unpack
        geometry = self.geometry
        settings = self.settings
        training = self.training
        
        vel_sound=340
        rho=1.2250
        iters=3
        
        AoA  = training.AoA
        mach = training.mach
        rpm_forward = training.rpm_forward
        rpm_lift = training.rpm_lift
        Cp_lift = training.Cp_lift
        Cp_forward = training.Cp_forward
        Ct_lift = training.Ct_lift
        Ct_forward = training.Ct_forward
        engines_number_tot = geometry.propulsors.propulsor.number_of_engines_forward + geometry.propulsors.propulsor.number_of_engines_lift
        
        # Build OpenVSP geometry file
        tag  = geometry.tag
        vsp_write_x57(geometry, tag)
        
        i=0
        data_len = len(AoA)
        CL = np.zeros([data_len,1])
        CD = np.zeros([data_len,1])

        # Condition input, local, do not keep (k is used to avoid confusion)
        konditions              = Data()
        konditions.aerodynamics = Data()

        if self.training_file is None:
            # Calculate aerodynamics for table
            #table_size = len(AoA)*len(mach)
            #xy = np.zeros([table_size,2])
            #count = 0
            time0 = time.time()
            while i < len(AoA):
    
                CL[i], CD[i] = vspaero(vel_sound,tag + ".vsp3", rho, AoA[i], mach[i], iters, rpm_forward[i], rpm_lift[i], engines_number_tot, Cp_lift[i], Cp_forward[i], Ct_lift[i], Ct_forward[i])
                print "CL= %f" % CL[i]
                print "CD= %f" % CD[i]
                i=i+1
            
            time1 = time.time()
            
            print 'The total elapsed time to run VSPAERO: '+ str(time1-time0) + '  Seconds'
        else:
            data_array = np.loadtxt(self.training_file)
            #xy         = data_array[:,0:2]
            CL         = data_array[:,2]
            CD         = data_array[:,3]
            
        CL2=np.zeros(data_len)
        i=0
        while i < len(AoA):
            CL2[i]=CL[i]
            i=i+1
            
        CD2=np.zeros(data_len)
        i=0
        while i < len(AoA):
            CD2[i]=CD[i]
            i=i+1

        # Save the data
        np.savetxt(geometry.tag+'_data.txt',np.column_stack((np.transpose(AoA), np.transpose(mach), np.transpose(CL2), np.transpose(CD2),  np.transpose(rpm_forward), np.transpose(rpm_lift), np.transpose(Cp_lift), np.transpose(Cp_forward), np.transpose(Ct_lift), np.transpose(Ct_forward))),fmt='%10.8f',header='AoA Mach CL CD RPM_for RPM_lift Cp_lift Cp_for Ct_lift Ct_for')
        
        # Store training data
        training.coefficients = np.hstack([CL,CD])
        #training.grid_points  = xy
        
        cwd = os.getcwd()
            
        myfile=cwd+'/'+tag + ".vsp3"

        ## If file exists, delete it ##
        if os.path.isfile(myfile):
            os.remove(myfile)
        else:    ## Show an error ##
            print("Error: %s file not found" % myfile)
        

        return

    def build_surrogate(self):
        """Builds a surrogate based on sample evalations using a OLS process.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        self.training.
          coefficients     [-] CL and CD
          grid_points      [radians,-] angles of attack and mach numbers 

        Outputs:
        self.surrogates.
          lift_coefficient <Guassian process surrogate>
          drag_coefficient <Guassian process surrogate>

        Properties Used:
        No others
        """  
        # Unpack data
        training  = self.training
        AoA  = training.AoA
        mach = training.mach
        rpm_forward = training.rpm_forward
        rpm_lift = training.rpm_lift
        Cp_lift = training.Cp_lift
        Cp_forward = training.Cp_forward
        Ct_lift = training.Ct_lift
        Ct_forward = training.Ct_forward
        CL   = training.coefficients[:,0]
        CD   = training.coefficients[:,1]
        
        # OLS Process
        df_cl=pandas.DataFrame({'AoA': AoA, 'mach': mach, 'rpm_forward': rpm_forward, 'rpm_lift': rpm_lift, 'Cp_lift': Cp_lift, 'Cp_forward': Cp_forward, 'Ct_lift': Ct_lift, 'Ct_forward': Ct_forward, 'CL': CL})  
        mod_cl = smf.ols(formula='CL~mach+np.power(AoA,2)+np.power(rpm_forward,2)+np.power(rpm_lift,2)+AoA*mach+rpm_forward*Cp_forward+rpm_forward*Ct_forward+rpm_lift*Cp_lift+AoA*rpm_forward+AoA*rpm_lift', data=df_cl)    
        cl_surrogate = mod_cl.fit()
        df_cd=pandas.DataFrame({'AoA': AoA, 'mach': mach, 'rpm_forward': rpm_forward, 'rpm_lift': rpm_lift, 'Cp_lift': Cp_lift, 'Cp_forward': Cp_forward, 'Ct_lift': Ct_lift, 'Ct_forward': Ct_forward, 'CD': CD})  
        mod_cd = smf.ols(formula='CD~mach+np.power(AoA,2)+np.power(rpm_forward,2)+np.power(rpm_lift,2)+AoA*mach+rpm_forward*Cp_forward+rpm_forward*Ct_forward+rpm_lift*Cp_lift+AoA*rpm_forward+AoA*rpm_lift', data=df_cd)    
        cd_surrogate = mod_cd.fit()
        
        
        self.surrogates.lift_coefficient = cl_surrogate
        self.surrogates.drag_coefficient = cd_surrogate

        return