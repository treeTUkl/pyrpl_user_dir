#NOCH IN BEARBEITUNG

# these imports are the standard imports for required for derived lockboxes
from pyrpl.software_modules.lockbox import *
from pyrpl.software_modules.loop import *

# Any InputSignal must define a class that contains the function "expected_signal(variable)" that returns the expected
# signal value as a function of the variable value. This function ensures that the correct setpoint and a reasonable
# gain is chosen (from the derivative of expected_signal) when this signal is used for feedback.
class AG_InputClassONE(InputSignal):
    """ A custom input signal for our customized lockbox. Please refer to the documentation on the default API of
    InputSignals"""
    """ it is assumed that the output has the linear relationship between
        setpoint change in output_unit per volt from the redpitaya, which
        is configured in the output parameter 'dc_gain'. We only need to
        convert units to get the output voltage bringing about a given
        setpoint difference. """
        # An example:
        # The configured output gain is 'output.dc_gain' nm/V.
        # setpoint_unit is cavity 'linewidth', the latter given by
        # 'lockbox._setpopint_unit_in_unit('nm')' (in nm).
        # Therefore, the output voltage corresponding to a change of
        # one linewidth is given (in V) by:
        # lockbox._setpopint_unit_in_unit('nm')/output.dc_gain
    def expected_signal(self, Myvoltage):
        """Returns the value of the expected signal in V, depending on the
              setpoint value "variable".
              """
        Myvoltage*= self.lockbox._setpoint_unit_in_unit('V')
        # For example, assume that our analog signal is proportional to the square of the variable
        return  Myvoltage

    # If possible, you should explicitely define the derivative of expected_signal(variable). Otherwise, the derivative
    # is estimated numerically which might lead to inaccuracies and excess delay.
    # haben die andern auch nicht
    #def expected_slope(self, variable):
    #   return 2.0 * self.custom_gain_attribute * self.lockbox.custom_attribute * variable

    # Signals can have their specific attributes, including gui support.
    # Please refer to the Lockbox example for more explanations on this.
   #_gui_attributes = _gui_attributes
   # _setup_attributes = ["setup-attribute_Voltage"]
    
    #haben die andern auch nicht
    custom_gain_attribute = FloatProperty(default=1.0,
                                          min=-1e10,
                                          max=1e10,
                                         increment=0.01,
                                          doc="custom factor for each input signal... so V?")

    # A customized calibration method can be used to implement custom calibrations. The calibration method of the
    # InputSignal class retrieves min, max, mean, rms of the input signal during a sweep and saves them as class
    # attributes, such that they can be used by expected_signal().
    ##duno what to do here so keep it

class AG_InputClassTWO(AG_InputClassONE):
    """ A custom input signal for our customized lockbox. Please refer to the documentation on the default API of
    InputSignals"""


class MyPiezoOutput(OutputSignal):
    unit = SelectProperty(default='V/V',
                          options=lambda inst:
                          [u + "/V" for u in inst.lockbox._output_units],
                          call_setup=True,
                          ignore_errors=True)
    #dc_gain: how much the model's variable is expected to change for 1 V
    #on the output (in *unit*)
    dc_gain = FloatProperty(default=8.7300e+02, min=-1e10, max=1e10, call_setup=True,doc="how much the model's variable is expected to change for 1 V on the output (in *unit*). Mostly 53 Peaks per 0.1V so via 633nm araound 2.3887e-9m/V  or in V/V 8.7300e+02")
    # sweep properties
    sweep_amplitude = FloatProperty(default=0.1, min=-1, max=1, call_setup=True)
    sweep_offset = FloatProperty(default=0.0, min=-1, max=1, call_setup=True)
    sweep_frequency = FrequencyProperty(default=0.5, call_setup=True)
    sweep_waveform = SelectProperty(options=Asg1.waveforms, default='ramp', call_setup=True)
    max_voltage = FloatProperty(default=0.8, min=-1.0, max=1.0,
                                call_setup=True,
                                doc="positive saturation voltage")
    min_voltage = FloatProperty(default=-0.8,
                                min=-1.0, max=1.0,
                                call_setup=True,
                                doc="negative saturation voltage")
    # gain properties
    ##assisted_design = BoolProperty(default=True, call_setup=True)
    desired_unity_gain_frequency = FrequencyProperty(default=0.0048838461373129465, min=0, max=1e10, call_setup=True)
    analog_filter_cutoff = FrequencyProperty(default=16.108, min=0, max=1e10, increment=0.1, call_setup=True)
    p = FloatProperty(min=-1e10, max=1e10, call_setup=True)
    i = FloatProperty(min=-1e10, max=1e10, call_setup=True)


# "" Crashed bei ausführung""""""
class AG_Lockbox(Lockbox):
    """ A custom lockbox class that can be used to implement customized feedback controllers"""


    # this syntax for the definition of inputs and outputs allows to conveniently access inputs in the API
    inputs = LockboxModuleDictProperty(port1=AG_InputClassONE,
                                       port2=AG_InputClassTWO)

    outputs = LockboxModuleDictProperty(piezo=MyPiezoOutput)#analog wie aus interferometer.py

    # the name of the variable to be stabilized to a setpoint. inputs.expected_signal(variable) returns the expected
    # signal as a function of this variable
   # variable = 'displacement'
    #copiert aus interferometer.py und auf "V" geändert
    # management of intput/output units
    setpoint_variable = 'Myvoltage'
    setpoint_unit = SelectProperty(options=['V'],
                                   default='V')



    # attributes are defined by descriptors
    # not sure what it does so leave it
    # custom_attribute_Voltage= FloatProperty(default=1.0, increment=0.01, min=1e-5, max=1e5)
    # attributes that are displayed in the gui. _gui_attributes from base classes are also added.
    wavelength = FloatProperty(max=1., min=0., default=633e-9, increment=1e-9)
    _gui_attributes = ['wavelength']
    _setup_attributes = _gui_attributes
    # list of attributes that are mandatory to define lockbox state. setup_attributes of all base classes and of all
    # submodules are automatically added to the list by the metaclass of Module
    #

    # if nonstandard units are to be used to specify the gain of the outputs, their conversion to Volts must be defined
    # by a property called _unitname_per_V
    _mV_per_V = 1000.0
    _units = ['V', 'mV']
    _output_units = ['V','mV']
    # overwrite any lockbox functions here or add new ones
    # def custom_function(self):
    #     self.calibrate_all()
    #     self.unlock()
    #     self.lock()

