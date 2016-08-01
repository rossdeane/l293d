#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
from threading import Thread

verbose = True # Prints stuff to the terminal
test_mode = False # Disables GPIO calls when true
pins_in_use = [] # Lists pins in use (all motors)

from info import version
print('L293D driver version ' + version.num_string)

try:
    import RPi.GPIO as GPIO
except Exception as e:
    print("Can't import RPi.GPIO. Please (re)install.")
    test_mode = True
    print('Test mode has been enabled. Please view README for more info.')

if not test_mode:
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        if verbose: print('GPIO mode set (GPIO.BOARD)')
    except Exception as e:
        print("Can't set GPIO mode (GPIO.BOARD)")

class motor(object):
    """
    A motor wired to the L293D chip where
    motor_pins[0] is pinA is L293D pin1 or pin9  : On or off
    motor_pins[1] is pinB is L293D pin2 or pin10 : Anticlockwise positive
    motor_pins[2] is pinC is L293D pin7 or pin15 : Clockwise positive
    """
    
    motor_pins = [0 for x in range(3)]
    
    def __init__(self, pinA=0, pinB=0, pinC=0):
        self.motor_pins[0] = pinA
        self.motor_pins[1] = pinB
        self.motor_pins[2] = pinC
        
        self.pins_are_valid(self.motor_pins)
        pins_in_use.append(self.motor_pins)
        self.gpio_setup(self.motor_pins)
    
    
    def pins_are_valid(self, pins):
        for pin in pins:
            pin_int = int(pin)
            if (pin_int < 1) or (pin_int > 40):
                raise ValueError('GPIO pin number needs to be between 1 and 40 inclusively.')
            for pin_in_use in pins_in_use:
                if pin_int in pin_in_use:
                    raise ValueError('GPIO pin {} already in use.'.format(pin_int))
        self.motor_pins = pins
        return True
    
    
    def gpio_setup(self, pins):
        for pin in pins:
            if not test_mode: GPIO.setup(pin, GPIO.OUT)
    
        
    def drive_motor(self, direction=1, duration=None, wait=True):
        if not test_mode:
            if (direction == 0):
                GPIO.output(self.motor_pins[0], GPIO.LOW)
            else:
                GPIO.output(self.motor_pins[direction], GPIO.HIGH)
                GPIO.output(self.motor_pins[direction*-1], GPIO.LOW)
                GPIO.output(self.motor_pins[0], GPIO.HIGH)
        if (duration is not None) and (direction != 0):
            stop_thread = Thread(target=self.stop, args = (duration, ))
            stop_thread.start()
            if wait:
                stop_thread.join()


    def pins_string_list(self):
        return '[{}, {} and {}]'.format(tuple(self.motor_pins))
    
    
    def spin_clockwise(self, duration=None, wait=True):
        if verbose: print('spinning motor at pins {} clockwise.'.format(str(self)))
        self.drive_motor(direction=1, duration=duration, wait=wait)
    
    
    def spin_anticlockwise(self, duration=None, wait=True):
        if verbose: print('spinning motor at pins {} anticlockwise.'.format(str(self)))
        self.drive_motor(direction=-1, duration=duration, wait=wait)
    
    
    def stop(self, after=0):
        if after > 0: sleep(after)
        if verbose: print('stopping motor at pins {}.'.format(str(self)))
        if not test_mode: self.drive_motor(direction=0, duration=after, wait=True)


def cleanup():
    if not test_mode: GPIO.cleanup()

