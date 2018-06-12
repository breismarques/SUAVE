## @defgroup Components-Energy-Networks Networks
# Components used in energy networks.
# These scripts are the blue prints the connect the component of your energy system. The mission will call these
# at each iteration to calculate thrust and a mass flow rate.
# @ingroup Components-Energy

from Solar import Solar
from Ducted_Fan import Ducted_Fan
from Battery_Ducted_Fan import Battery_Ducted_Fan 
from Turbofan import Turbofan
from Turbojet_Super import Turbojet_Super
from Solar_Low_Fidelity import Solar_Low_Fidelity
from Dual_Battery_Ducted_Fan import Dual_Battery_Ducted_Fan
from Turbofan_3 import Turbofan_3
from Turbojet_Super_AB import Turbojet_Super_AB

from Turbofan_TASOPT import Turbofan_TASOPT
#from Turbofan_TASOPTc_wrap import Turbofan_TASOPTc_wrap
from Turbofan_Deck_I import Turbofan_Deck_I
from Turbofan_JDM import Turbofan_JDM
from Turbofan_TASOPT_Net import Turbofan_TASOPT_Net
from Series_Ducted_Fan_Hybrid import Series_Ducted_Fan_Hybrid
from Series_Battery_Propeller_Hybrid import Series_Battery_Propeller_Hybrid
from Series_Battery_Propeller_Hybrid_Interp import Series_Battery_Propeller_Hybrid_Interp
from Battery_Propeller import Battery_Propeller
from Internal_Combustion_Propeller import Internal_Combustion_Propeller
from Lift_Forward_Propulsor_Low_Fidelity import Lift_Forward_Low_Fidelity
from Battery_Propeller_Low_Fidelity import Battery_Propeller_Low_Fidelity
from Propulsor_Surrogate import Propulsor_Surrogate
from Series_Battery_Propeller_Hybrid_Low_Fid import Series_Battery_Propeller_Hybrid_Low_Fid
from Lift_Forward_Propulsor import Lift_Forward