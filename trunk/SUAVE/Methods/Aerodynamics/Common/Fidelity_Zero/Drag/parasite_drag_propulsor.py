## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Drag
# parasite_drag_propulsor.py
# 
# Created:  Dec 2013, SUAVE Team
# Modified: Jan 2016, E. Botero          

#Sources: Stanford AA241 Course Notes
#         Raymer: Aircraft Design: A Conceptual Approach

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# suave imports
from SUAVE.Core import Data
from SUAVE.Methods.Aerodynamics.Common.Fidelity_Zero.Helper_Functions import compressible_turbulent_flat_plate

# package imports
import numpy as np

# ----------------------------------------------------------------------
#   Parasite Drag Propulsor
# ----------------------------------------------------------------------

## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Drag
def parasite_drag_propulsor(state,settings,geometry):
    """Computes the parasite drag due to the propulsor

    Assumptions:
    Basic fit

    Source:
    adg.stanford.edu (Stanford AA241 A/B Course Notes)

    Inputs:
    state.conditions.freestream.
      mach_number                                [Unitless]
      temperature                                [K]
      reynolds_number                            [Unitless]
    geometry.      
      nacelle_diameter                           [m^2]
      areas.wetted                               [m^2]
      engine_length                              [m]

    Outputs:
    propulsor_parasite_drag                      [Unitless]

    Properties Used:
    N/A
    """

    # unpack inputs
    conditions    = state.conditions
    configuration = settings
    
    propulsor = geometry
    
    # conditions
    freestream = conditions.freestream
    Mc  = freestream.mach_number
    Tc  = freestream.temperature    
    re  = freestream.reynolds_number
    
    try: 
        propulsor.nacelle_diameter
    except AttributeError:   
        Sref_forward      = propulsor.nacelle_diameter_forward**2. / 4. * np.pi
        Swet_forward      = propulsor.areas_forward.wetted
        l_prop_forward = propulsor.engine_length_forward
        d_prop_forward = propulsor.nacelle_diameter_forward
        
        Sref_lift      = propulsor.nacelle_diameter_lift**2. / 4. * np.pi
        Swet_lift      = propulsor.areas_lift.wetted
        l_prop_lift = propulsor.engine_length_lift
        d_prop_lift = propulsor.nacelle_diameter_lift
        
        # reynolds number
        Re_prop_forward = re*l_prop_forward
        Re_prop_lift = re*l_prop_lift
        
        # skin friction coefficient
        cf_prop_forward, k_comp_forward, k_reyn_forward = compressible_turbulent_flat_plate(Re_prop_forward,Mc,Tc)
        cf_prop_lift, k_comp_lift, k_reyn_lift = compressible_turbulent_flat_plate(Re_prop_lift,Mc,Tc)
        
        ## form factor according to Raymer equation (pg 283 of Aircraft Design: A Conceptual Approach)
        k_prop_forward = 1 + 0.35 / (float(l_prop_forward)/float(d_prop_forward))
        k_prop_lift = 1 + 0.35 / (float(l_prop_lift)/float(d_prop_lift))
        
        # find the final result    
        propulsor_parasite_drag_forward = k_prop_forward * cf_prop_forward * Swet_forward / Sref_forward
        propulsor_parasite_drag_lift = k_prop_lift * cf_prop_lift * Swet_lift / Sref_lift
        
        propulsor_parasite_drag=propulsor_parasite_drag_forward+propulsor_parasite_drag_lift
        
        
    else:
        Sref      = propulsor.nacelle_diameter**2. / 4. * np.pi
        Swet      = propulsor.areas.wetted
        l_prop = propulsor.engine_length
        d_prop = propulsor.nacelle_diameter
        # reynolds number
        Re_prop = re*l_prop
    
        # skin friction coefficient
        cf_prop, k_comp, k_reyn = compressible_turbulent_flat_plate(Re_prop,Mc,Tc)
    
        ## form factor according to Raymer equation (pg 283 of Aircraft Design: A Conceptual Approach)
        k_prop = 1 + 0.35 / (float(l_prop)/float(d_prop))  

        # find the final result    
        propulsor_parasite_drag = k_prop * cf_prop * Swet / Sref
    
    
    # dump data to conditions
    try:
        propulsor.nacelle_diameter
    except AttributeError:
        propulsor_result = Data(
                                    wetted_area               = Swet_forward+Swet_lift   , 
                                    reference_area            = Sref_forward+Sref_lift   , 
                                    parasite_drag_coefficient = propulsor_parasite_drag ,
                                    skin_friction_coefficient = cf_prop_forward+cf_prop_lift ,
                                    compressibility_factor    = k_comp_forward+k_comp_lift  ,
                                    reynolds_factor           = k_reyn_forward+k_reyn_lift  , 
                                    form_factor               = k_prop_forward+k_prop_lift  ,
                                )
            
    else:
        propulsor_result = Data(
                                wetted_area               = Swet    , 
                                reference_area            = Sref    , 
                                parasite_drag_coefficient = propulsor_parasite_drag ,
                                skin_friction_coefficient = cf_prop ,
                                compressibility_factor    = k_comp  ,
                                reynolds_factor           = k_reyn  , 
                                form_factor               = k_prop  ,                
                                )
    
    conditions.aerodynamics.drag_breakdown.parasite[propulsor.tag] = propulsor_result    
    
    return propulsor_parasite_drag