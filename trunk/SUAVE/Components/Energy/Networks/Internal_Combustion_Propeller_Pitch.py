## @ingroup Components-Energy-Networks
# Internal_Combustion_Propeller_Pitch.py
# 
# Created:  Sep 2016, E. Botero
# Modified: 

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# suave imports
import SUAVE

# package imports
import numpy as np
from SUAVE.Components.Propulsors.Propulsor import Propulsor

from SUAVE.Core import Data, Units

# ----------------------------------------------------------------------
#  Network
# ----------------------------------------------------------------------
class Internal_Combustion_Propeller_Pitch(Propulsor):
    def __defaults__(self): 
        self.engine            = None
        self.propeller         = None
        self.engine_length     = None
        self.number_of_engines = None
        self.thrust_angle      = 0.0
        self.rated_speed       = 0.0
        self.tag               = 'network'
        self.nacelle_diameter = None
        
        #areas needed for drag; not in there yet
        self.areas             = Data()
        self.areas.wetted      = 0.0
        self.areas.maximum     = 0.0
        self.areas.exit        = 0.0
        self.areas.inflow      = 0.0
    
    # manage process with a driver function
    def evaluate_thrust(self,state):
    
        # unpack
        conditions  = state.conditions
        numerics    = state.numerics
        engine      = self.engine
        propeller   = self.propeller
        rated_speed = self.rated_speed
        
        # Throttle the engine
        eta = conditions.propulsion.throttle[:,0,None]
        engine.speed = conditions.propulsion.rpm
        #conditions.propulsion.combustion_engine_throttle = eta # keep this 'throttle' on
        conditions.propulsion.pitch_command = eta
        
        # Run the engine
        engine.power(conditions)
        power_output = engine.outputs.power
        sfc          = engine.outputs.power_specific_fuel_consumption
        mdot         = engine.outputs.fuel_flow_rate
        torque       = engine.outputs.torque     
        
        # link
        propeller.inputs.omega =  engine.speed
        propeller.thrust_angle = self.thrust_angle
        # step 4
        F, Q, P, Cp = propeller.spin_variable_pitch(conditions)
        
        #print 'Delta Torque'
        #print Q - torque
    
        # Pack the conditions for outputs
        #rpm        = engine.speed / Units.rpm
          
        conditions.propulsion.rpm              = engine.speed
        conditions.propulsion.propeller_torque = Q
        conditions.propulsion.power            = P
        
        # Create the outputs
        F    = self.number_of_engines * F * [np.cos(self.thrust_angle),0,-np.sin(self.thrust_angle)]      
        
        results = Data()
        results.thrust_force_vector = F
        results.vehicle_mass_rate   = mdot
        
        return results
    
    
    def unpack_unknowns(self,segment,state):
        """"""        
        
        # Here we are going to unpack the unknowns (Cp) provided for this network
        state.conditions.propulsion.propeller_power_coefficient = state.unknowns.propeller_power_coefficient
        
        return
    
    def residuals(self,segment,state):
        """"""        
        
        # Here we are going to pack the residuals (torque,voltage) from the network
        
        # Unpack
        q_motor   = state.conditions.propulsion.motor_torque
        q_prop    = state.conditions.propulsion.propeller_torque
        
        # Return the residuals
        state.residuals.network[:,0] = q_motor[:,0] - q_prop[:,0]    
        
        return    
            
    __call__ = evaluate_thrust