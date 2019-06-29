#!/usr/bin/env python3
import math
from enum import Enum
import RPi.GPIO as GPIO
import time
import atexit
from datetime import datetime
#import matplotlib.pyplot as plt
#STATUS_LED         = 10

#BTN_RUN_STOP       = 11
#BTN_DIRECTION      = 12
#BTN_SPEED_INCREASE = 13
#BTN_SPEED_DECREASE = 15

#MotorPin_A         = 16
#MotorPin_B         = 18

#g_sta =  1
#g_dir =  1
#speed = 50

#pwm_B = 0


class Button:
        
    def __init__(self, pin, pull_up_down=GPIO.PUD_DOWN, name='', debug=False):
        self.pin = pin
        self.pull_up_down = pull_up_down
        self.debug = debug
        self.previous_value = None
        self.current_value = None
        self.name = name if name else "Button on pin {}".format(self.pin)    
    
        self._subscibers = []
        
    def setup(self):
        if self.debug:
            print('Setting up button on pin {}'.format(self.pin))
            
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=self.pull_up_down)
        
    def scan(self):

        #if self.debug:
            #print(GPIO.input(self.pin))
        
        self.previous_value = self.current_value
        self.current_value = GPIO.input(self.pin)
        
        if self.current_value == GPIO.HIGH and self.previous_value == GPIO.LOW:
            if self.debug:
                print('{} pressed'.format(self.name))
            self.pressed()
        if self.current_value == GPIO.LOW and self.previous_value == GPIO.HIGH:
            if self.debug:
                print('{} released'.format(self.name))            
            
    def cleanup(self):
        pass
        
    def pressed(self):
        for s in self._subscibers:
            s(self)
        
    def subscribe(self, func):
        self._subscibers.append(func)
    

class LED_Light:
    
    def __init__(self, pin, name=''):
        
        self.state = 0
        self.pin = pin
        self.name = name if name else "LED on pin {}".format(self.pin)    
        
    def setup(self):
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.HIGH)

    def turn_on(self):   
        print('light on')     
        GPIO.output(self.pin, GPIO.LOW)
        self.state = 1
        
    def turn_off(self):
        print('light off')
        GPIO.output(self.pin, GPIO.HIGH)
        self.state = 0
        
    def switch(self, *args):
        
        if self.state == 0:
            GPIO.output(self.pin, GPIO.LOW)
            self.state = 1
        else:
            GPIO.output(self.pin, GPIO.HIGH)
            self.state = 0
        
    def cleanup():
        GPIO.output(self.pin, GPIO.HIGH)
        
        
#def motorStop():
#    GPIO.output(MotorPin_A, GPIO.HIGH)
#    GPIO.output(MotorPin_B, GPIO.LOW)

#def setup():
#    GPIO.setwarnings(False)
#    GPIO.setmode(GPIO.BOARD)
#    GPIO.setup(STATUS_LED, GPIO.OUT)   # pin mode --- output
#    GPIO.setup(BTN_RUN_STOP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # set pin mode as input, and pull it to high level.
#    GPIO.setup(BTN_DIRECTION, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#    GPIO.setup(BTN_SPEED_INCREASE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#    GPIO.setup(BTN_SPEED_DECREASE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#    GPIO.setup(MotorPin_A, GPIO.OUT)
#    GPIO.setup(MotorPin_B, GPIO.OUT)
#    motorStop()
#    global pwm_B
#    pwm_B = GPIO.PWM(MotorPin_B, 2000) # create pwm and set frequece to 2KHz

class MotorState(Enum):
    OFF = 0
    ON = 1
    
  
class ControlMode(Enum):
    SPEED = 1
    STROKE = 2

class Motor:
    
    min_speed = 1
    max_speed = 10
    speed_increment = 1
    motor_pins = (31, 33, 35, 37)
    max_stroke = 64
    min_stroke = 14
    
    def __init__(self):
        
        self.state = MotorState.OFF
        self.speed = 1
        
        
        
        
        
        3333330
        self.direction = 1
        self.indicator_light = LED_Light(29, name='Motor Status')
        self.position = 0
        self.stroke = 24
        
        self.control_mode  = ControlMode.SPEED
        
        self.history = []

    def set_step(self, *args):  
        for pin, w in zip(self.motor_pins, args):
            GPIO.output(pin,w)  
        
        
    def print_state(self):
        print("{}: speed={}  stroke={} control mode={} pos={}".format(
            self.state.name, 
            self.speed, 
            self.stroke,
            self.control_mode.name,
            self.position))
        
    def turn_off(self):
        self.state = MotorState.OFF
        self.indicator_light.turn_off()
        self.set_step(0,0,0,0)        
        
    def turn_on(self):
        self.state = MotorState.ON        
        self.indicator_light.turn_on()

    def get_dt(self):
        #print('getting dt')
        base_dt = 0.01/ self.speed
        #return base_dt
        #d = abs(self.stroke - self.position)
        d = abs(self.position / self.stroke)
        dt = base_dt + d**4 * base_dt*4
        #print(dt)
        return base_dt
        #dt = (d + 1) / (self.stroke + 1) * base_dt
        #return dt
        #return (6 - 5*math.cos(self.position / self.stroke * math.pi/2)) * base_dt
        
    def run(self, dt):
        
        if self.state == MotorState.OFF:
            return
        
        if self.direction == 1:
            for j in range(4):
                args = [0,0,0,0]
                args[j] = 1
                self.set_step(*args)
                time.sleep(self.get_dt())    
            self.position += 1
                
        elif self.direction == -1:
            for j in range(4):
                args = [0,0,0,0]
                args[-j] = 1
                self.set_step(*args)
                time.sleep(self.get_dt())
            self.position -= 1
        
        if abs(self.position) == self.stroke:
            self.direction *= -1    
            
        self.history.append([datetime.now(), self.position, self.speed, self.stroke, self.get_dt()])
                
    def switch_on_off(self, *args):
        
        if self.state == MotorState.OFF:
            self.turn_on()
        else:
            self.turn_off()
            # self.speed = 1
            self.dump_history()
        
        self.print_state()
            
    def faster(self, *args):
        
        if self.state == MotorState.OFF:
            return
        speed = self.speed
        speed += self.speed_increment
        speed = min(self.max_speed, speed)
        self.speed = speed
        self.print_state()

    def slower(self, *args):
        
        if self.state == MotorState.OFF:
            return
        speed = self.speed
        speed -= self.speed_increment
        speed = max(self.min_speed, speed)
        self.speed = speed
        self.print_state()
        
    def increase_stroke(self, *args):
        
        self.stroke = min(64, self.stroke + 10)
        self.print_state()
        
    def decrease_stroke(self, *args):
        
        self.stroke = max(14, self.stroke - 10)
        self.print_state()
        
    def control_up(self, *args):
        
        if self.control_mode == ControlMode.SPEED:
            self.faster(*args)
        else:
            self.increase_stroke(*args)
    
    def control_down(self, *args):
        
        if self.control_mode == ControlMode.SPEED:
            self.slower(*args)
        else:
            self.decrease_stroke(*args)        

    def change_direction(self, *args):
        
        if self.state == MotorState.ON:
            print('You must turn off the motor before switching direction')
        else:
            self.direction *= -1

        self.print_state()
        
    def change_control_mode(self, *args):
        
        if self.control_mode == ControlMode.SPEED:
            self.control_mode = ControlMode.STROKE
        elif self.control_mode == ControlMode.STROKE:
            self.control_mode = ControlMode.SPEED
              
    def setup(self):
        self.indicator_light.setup()        
        
        for pin in self.motor_pins:
            GPIO.setup(pin, GPIO.OUT)      # Set pin's mode is outuput        
        
    def cleanup():
        self.turn_off()
        
        
    def dump_history(self):
        
        import json
        history = list(zip(*self.history))
        t = list(history[0])
        t0 = t[0] 
        for i in range(len(t)):
            t[i] = (t[i] - t0).total_seconds()
            
        history[0] = t
        with open('motor_history_{}.txt'.format(t0), 'w') as fout:
            json.dump(history, fout)
        history = []

class Program:
    
    def __init__(self, dt=0.002, debug=False):
        self.controls = []
        self.controls.append(Button(11, name='On/Off Button', debug=debug))
        self.controls.append(Button(12, name='Faser Button', debug=debug))
        self.controls.append(Button(13, name = 'Slower Button', debug=debug))   
        self.controls.append(Button(15, name='Direction Button', debug=debug))
        self.motor = Motor()
        self.controls[0].subscribe(self.motor.switch_on_off)
        self.controls[1].subscribe(self.motor.control_up)
        self.controls[2].subscribe(self.motor.control_down)
        self.controls[3].subscribe(self.motor.change_control_mode)
        self.dt = dt
        self.debug = debug
        
    def setup(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        for c in self.controls:
            c.setup()
        self.motor.setup()
            
    def loop(self):
        while True:
            for c in self.controls:
                c.scan()
            self.motor.run(self.dt)            
            self.dt = self.motor.get_dt()  # 0.01 / self.motor.speed
            time.sleep(self.dt)
            #~ plt.hold(False)
            #~ plt.plot(list(range(len(self.motor.history))), self.motor.history)

    def destroy(self, *args):
        #motorStop()
        print('Running cleanup')
        self.motor.turn_off()
        self.motor.cleanup()
        time.sleep(0.5)
        GPIO.cleanup()             # Release resource
        time.sleep(0.5)
        
    def run(self):
        
        #~ plt.figure(figsize=(12,8))
        #~ plt.show(block=False)
        if self.debug:
            print('starting program')
        self.setup()
        try:
            self.loop()
        except KeyboardInterrupt:
            self.destroy() 
            
        
        
        
            
if __name__ == '__main__':     # Program start from here
    print('setting up program')
    prog = Program(debug=False)
    atexit.register(prog.destroy)
    prog.run()
    
    from plot_motor_position import plot_last_history
    plot_last_history()
    
