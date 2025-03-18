from pynq.overlays.base import BaseOverlay
import pynq.lib.rgbled as rgbled 
from pynq.lib.arduino import Arduino_Analog
import time 
import socket
import multiprocessing

# Load the PYNQ base overlay
base = BaseOverlay('base.bit')

# Initialize joysticks ADCs
joystick_x1 = Arduino_Analog(base.ARDUINO, [0])  # X-axis (A0)
joystick_y1 = Arduino_Analog(base.ARDUINO, [1])  # Y-axis (A1)
joystick_x2 = Arduino_Analog(base.ARDUINO, [4])  # X-axis (A4)
joystick_y2 = Arduino_Analog(base.ARDUINO, [5])  # Y-axis (A5)

#joystick_click1 = Arduino_IO(base.ARDUINO, 3, "in")
#joystick_click2 = 

# Initialize Button 0 (BTN0)
button = base.buttons[3]
fire_button = base.buttons[0]
enter_button = base.buttons[2]
run_button = base.buttons[1]


x_value1 = None
y_value1 = None
x_value2 = None
y_value2 = None
l_click = 0
r_click = 0

# Initialize the base LEDs
leds = [base.leds[i] for i in range(4)]  # list of leds LD0-LD3
led4 = rgbled.RGBLED(4)

def joystick1():
    global x_value1, y_value1, l_click
    # Read joystick values explicitly with 'raw' format
    x_value1 = joystick_x1.read('raw')  # X-axis (A0)
    y_value1 = joystick_y1.read('raw')  # Y-axis (A1)
    #r_click  = # digital read from pin y
    

    # Define thresholds for direction
    if y_value1 < 25000:  # threshold for "Up"
        leds[0].on()  # Turn on LD0 (Up)
        leds[1].off()
        leds[2].off()
        leds[3].off()
        print(f"Y value is: {y_value1}")
        print("joystick 1: up\n")
        #time.sleep(0.1)
    elif y_value1 > 39000:  # threshold for "Down"
        leds[0].off()
        leds[1].on()  # Turn on LD1 (Down)
        leds[2].off()
        leds[3].off()
        print(f"Y value is: {y_value1}")
        print("joystick 1: down\n")
        #time.sleep(0.1)
    elif x_value1 > 39000:  # threshold for "right"
        leds[0].off()
        leds[1].off()
        leds[2].on()  # Turn on LD2 (right)
        leds[3].off()
        print(f"X value is: {x_value1}")
        print("joystick 1: right\n")
        #time.sleep(0.1)
    elif x_value1 < 25000:  # threshold for "left"
        leds[0].off()
        leds[1].off()
        leds[2].off()
        leds[3].on()  # Turn on LD3 (left)
        print(f"X value is: {x_value1}")
        print("joystick 1: left\n")
        #time.sleep(0.1)
    else:  # Neutral/Center position
        for led in leds:
            led.off()  # Turn off all LEDs
        print(f"X: {x_value1}, Y: {y_value1}")
        #time.sleep(0.1)

def joystick2():
    # Read joystick values explicitly with 'raw' format
    global x_value2, y_value2
    x_value2 = joystick_x2.read('raw')  # X-axis (A2)
    y_value2 = joystick_y2.read('raw')  # Y-axis (A3)

    # Define thresholds for direction
    if y_value2 < 25000:  # threshold for "Up"
        led4.write(0x1)
        print(f"Y value is: {y_value2}")
        print("joystick 2: up\n")
        #time.sleep(0.1)
    elif y_value2 > 39000:  # threshold for "Down"
        led4.write(0x2)
        print(f"Y value is: {y_value2}")
        print("joystick 2: down\n")
        #time.sleep(0.1)
    elif x_value2 > 39000:  # threshold for "right"
        led4.write(0x3)
        print(f"X value is: {x_value2}")
        print("joystick 2: right\n")
        #time.sleep(0.1)
    elif x_value2 < 25000:  # threshold for "left"
        led4.write(0x4)
        print(f"X value is: {x_value2}")
        print("joystick 2: left\n")
        #time.sleep(0.1)
    else:  # Neutral/Center position
        led4.write(0x0)  # Turn off LED
        print(f"X: {x_value2}, Y: {y_value2}")
        #time.sleep(0.1)
		
	def game_controls():
    global cframe_cache
    # define bitmasks
    L_STICK_UP = 1 << 10 #bit 11
    L_STICK_DOWN = 1 << 9 #bit 10
    L_STICK_LEFT = 1 << 8 #bit 9
    L_STICK_RIGHT = 1 << 7 #bit 8
    #L_STICK_USE = 1 << 6 #bit 7

    R_STICK_STRAFE_L = 1 << 5 #bit 6
    R_STICK_STRAFE_R = 1 << 4 #bit 5
    R_STICK_ESCAPE = 1 << 3 #bit4

    BUTTON_FIRE = 1 << 2 #bit3
    BUTTON_RUN = 1 << 1 #bit2
    BUTTON_ENTER = 1 #bit1

    # define threshold values, reversed for joystick orientation
    UP_BOUND  = 25000
    LOW_BOUND = 39000

    # define control frame
    cframe = 0
    
    # apply masks
    #joystick 1 (left hand)
    if(y_value1 > LOW_BOUND):
      cframe |= L_STICK_LEFT 
      print("J1 left")
    if(y_value1 < UP_BOUND):
      cframe |= L_STICK_RIGHT
      print("J1 right")
    if(x_value1 > LOW_BOUND):
      cframe |=  L_STICK_DOWN
      print("J1 down")
    if(x_value1 < UP_BOUND):
      cframe |= L_STICK_UP
      print("J1 up")
    #if(l_click == 1 ):
      #cframe |= L_STICK_USE
      #print(f"Joystick 1 clicked and is: {l_click}")
    
    #joystick 2 (Right hand)
    if(y_value2 > LOW_BOUND):
      cframe |= R_STICK_STRAFE_L
      print("J2 left")
    if(y_value2 < UP_BOUND):
      cframe |= R_STICK_STRAFE_R
      print("J2 right")
    if(x_value2 < UP_BOUND):
      cframe |= R_STICK_ESCAPE
      print("J2 escape")
        
    #buttons
    if (fire_button.read()==1):
      cframe |= BUTTON_FIRE
      print("Fire button pressed")
    if (run_button.read()==1):
      cframe |= BUTTON_RUN
      print("Run button pressed")
    if (enter_button.read()==1):
      cframe |= BUTTON_ENTER
      print("Enter button pressed")
    
    
    cframe_bytes = cframe.to_bytes(2, byteorder='big')
    
    # update cache
    cframe_cache = cframe_bytes
    clientSocket.send(cframe_cache)
    #time.sleep(0.1)
    # clientSocket.send(htons(cframe_cache)  # might need this 
	
	#Loop to test joysticks
cframe_cache = b'\x00\x00'
serverName = '192.168.0.101'
serverPort = 65432
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName,serverPort)) 

try:
    while True:
        # Check if Button 0 is pressed
        if button.read() == 1:  # Button is pressed
            print("Button 0 pressed. Exiting program...")
            break

        joystick1();
        joystick2();
        game_controls();
        print(f"C_frame bytes: {cframe_cache}\n")
        

finally:
    # Ensure all LEDs are turned off when the program ends
    led4.write(0x0)
    for led in leds:
        led.off()
