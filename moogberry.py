##Moogberry  with analog input from MCP3008
import time
import OSC
import os
import subprocess
import RPi.GPIO as GPIO
##Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

#Start puredata
##os.system('sudo pd-extended  -nogui -alsamidi -alsa /home/pi/Documents/Moogberry_background.pd')
##time.sleep(5)

##Setup OSC client
c = OSC.OSCClient()
c.connect(('localhost', 9001))

##GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
##setup inputs
GPIO.setup(25, GPIO.IN) 
GPIO.setup(21, GPIO.IN)

##setup outputs
mux1s0 = 20
mux1s1 = 16
mux1s2 = 12

mux2s0 = 26
mux2s1 = 19
mux2s2 = 13

mux3s0 = 6
mux3s1 = 5
mux3s2 = 22

filterLed = 27
filterSel = 17

statusLED = 2
resetLED = 24
resetBtn = 23

##mux1 (filter/envelope)
GPIO.setup(mux1s0, GPIO.OUT)
GPIO.setup(mux1s1, GPIO.OUT)
GPIO.setup(mux1s2, GPIO.OUT)
##mux2 (osc1 leds)
GPIO.setup(mux2s0, GPIO.OUT)
GPIO.setup(mux2s1, GPIO.OUT)
GPIO.setup(mux2s2, GPIO.OUT)
##mux3 (osc2 leds)
GPIO.setup(mux3s0, GPIO.OUT)
GPIO.setup(mux3s1, GPIO.OUT)
GPIO.setup(mux3s2, GPIO.OUT)
##filter selected 
GPIO.setup(filterLed, GPIO.OUT)
GPIO.setup(filterSel, GPIO.IN)
##setup variables
currentOscillator1 = 0  ##0=sin,1=tri,2=squ,3=saw
currentOscillator2 = 0  ##0=sin,1=tri,2=squ,3=saw
currentFilter = 0       ##0=hpf, 1=lpf

GPIO.setup(statusLED, GPIO.OUT)
GPIO.setup(resetLED, GPIO.OUT)
GPIO.setup(resetBtn, GPIO.IN)

##Software SPI configuration:
CLK  = 11
MISO = 9
MOSI = 10
CS1   = 8
CS2 = 7
mcp1 = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS1, miso=MISO, mosi=MOSI)
mcp2 = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS2, miso=MISO, mosi=MOSI)

def startupSeq():
    GPIO.output(statusLED,1)
    time.sleep(0.2)
    GPIO.output(statusLED,0)
    time.sleep(0.2)
    GPIO.output(statusLED,1)
    time.sleep(0.2)
    GPIO.output(statusLED,0)
    time.sleep(0.2)
    GPIO.output(statusLED,1)

def shutdown():
    if(GPIO.input(resetBtn)==1):
        GPIO.output(resetLED,1)
        time.sleep(0.5)
        GPIO.output(resetLED,0)
	time.sleep(0.5)
        GPIO.output(resetLED,1)
        time.sleep(0.5)
        GPIO.output(resetLED,0)
        time.sleep(0.5)   
        GPIO.output(resetLED,1)
        time.sleep(0.5)
        GPIO.output(resetLED,0)
        time.sleep(0.5)
        GPIO.output(resetLED,1)
        time.sleep(0.5)
        GPIO.output(resetLED,0)
	GPIO.output(statusLED,0)
        time.sleep(0.5)
	print('Shutting down')
	os.system('sudo shutdown now')
    elif(GPIO.input(resetBtn)==0):
	return

##
## sets the ADSR of the envelope
##    
def envelope():
    ##set mux channel
    GPIO.output(mux1s0, 0)
    GPIO.output(mux1s1, 0)
    GPIO.output(mux1s2, 0)
    ##read adc channel    
    attack = int(mcp1.read_adc(0))
    ##send OSC message    

    attackOSC = OSC.OSCMessage("/env/a")
    attackOSC.append(attack/991.9)
    c.send(attackOSC)

    GPIO.output(mux1s0, 0)
    GPIO.output(mux1s1, 1)
    GPIO.output(mux1s2, 1)
    decay = int(mcp1.read_adc(0))
    decayOSC = OSC.OSCMessage("/env/d")
    decayOSC.append(decay/991.9)
    c.send(decayOSC)

    GPIO.output(mux1s0, 1)
    GPIO.output(mux1s1, 1)
    GPIO.output(mux1s2, 0)
    sustain = int(mcp1.read_adc(0))
    sustainOSC = OSC.OSCMessage("/env/s")
    sustainOSC.append(sustain/991.9)
    c.send(sustainOSC)

    GPIO.output(mux1s0, 1)
    GPIO.output(mux1s1, 1)
    GPIO.output(mux1s2, 1)
    release = int(mcp1.read_adc(0))
    releaseOSC = OSC.OSCMessage("/env/r")
    releaseOSC.append(release/991.9)
    c.send(releaseOSC)
    
##
## sets the filter cutoff frequency, and resonance amount
##    
def filter():
    GPIO.output(mux1s0, 0)
    GPIO.output(mux1s1, 0)
    GPIO.output(mux1s2, 1)
    filterVal = int(mcp1.read_adc(0))
    filtFreqOSC = OSC.OSCMessage('/filter/freq')
    filtFreqOSC.append(filterVal/7.9)
    c.send(filtFreqOSC)

    GPIO.output(mux1s0, 1)
    GPIO.output(mux1s1, 0)
    GPIO.output(mux1s2, 0)
    resVal= int(mcp1.read_adc(0))   
    filtResOSC = OSC.OSCMessage('/filter/res')
    filtResOSC.append(resVal/103.2)
    c.send(filtResOSC)

def filterSelect():
    global currentFilter
    filtSelBtn = GPIO.input(filterSel)
    if(filtSelBtn==1):
        if(currentFilter==0):
            filtTypeOSC=OSC.OSCMessage('/filter/type')
            GPIO.output(filterLed,1)
            filtTypeOSC.append(1)
            c.send(filtTypeOSC) 
            currentFilter = 1

        elif(currentFilter==1):
            filtTypeOSC=OSC.OSCMessage('/filter/type')    
            GPIO.output(filterLed,0)
            filtTypeOSC.append(0)
            c.send(filtTypeOSC) 
            currentFilter=0
        time.sleep(0.2) 


##
## sets the pitch parameters and PWM of oscillator 1
##        
def oscillator1():
    #reading from adc
    osc1Semi = int(mcp1.read_adc(1))
    osc1Octave = int(mcp1.read_adc(4))
    osc1Cents = int(mcp1.read_adc(7))
    osc1PWM = int(mcp2.read_adc(4))
    osc1Vol = mcp2.read_adc(7)
##    print('Osc1--', 'Semi: ', osc1Semi, 'Oct: ', osc1Octave,'Cents:', osc1Cents,'PWM: ', osc1PWM, 'Vol: ', osc1Vol)

    #send OSC to puredata
    semi1OSC = OSC.OSCMessage('/osc1/semi')
    semi1OSC.append(int(osc1Semi/41.33))
    c.send(semi1OSC)
    
    oct1OSC = OSC.OSCMessage('/osc1/octave')
    oct1OSC.append(int(osc1Octave/198.4)-2)
    c.send(oct1OSC)
    
    cent1OSC = OSC.OSCMessage('/osc1/cents')
    cent1OSC.append(int(osc1Cents/4.99))
    c.send(cent1OSC)
    
    pwm1OSC = OSC.OSCMessage('/osc1/pwm')
    pwm1OSC.append((osc1PWM/991.9))
    c.send(pwm1OSC)
    
    vol1OSC = OSC.OSCMessage('/mix/osc1')
    vol1OSC.append((osc1Vol/991.9))
    c.send(vol1OSC)

##
## sets the pitch parameters and PWM of oscillator 2
##    
def oscillator2():
    #reading from adc
    osc2Semi = int(mcp1.read_adc(3))
    osc2Octave = int(mcp1.read_adc(6))
    osc2Cents = int(mcp2.read_adc(0))
    osc2PWM = (mcp2.read_adc(2))
    osc2Vol = (mcp2.read_adc(5))
##    print('Osc2--', 'Semi: ', osc2Semi, 'Oct: ', osc2Octave,'Cents:', osc2Cents,'PWM: ', osc2PWM, 'Vol: ', osc2Vol)

    #send OSC to puredata
    semi2Osc = OSC.OSCMessage('/osc2/semi')
    semi2Osc.append(int(osc2Semi/41.33))
    c.send(semi2Osc)
    
    oct2Osc = OSC.OSCMessage('/osc2/octave')
    oct2Osc.append(int(osc2Octave/198.4)-2)
    c.send(oct2Osc)
    
    cent2Osc = OSC.OSCMessage('/osc2/cents')
    cent2Osc.append(int(osc2Cents/4.99))
    c.send(cent2Osc)
    
    pwm2Osc = OSC.OSCMessage('/osc2/pwm')
    pwm2Osc.append((osc2PWM/991.9))
    c.send(pwm2Osc)
    
    vol2Osc = OSC.OSCMessage('/mix/osc2')
    vol2Osc.append((osc2Vol/991.9))
    c.send(vol2Osc)

## ## toggles between the waveforms for oscillator 1
## sends OSC messages and sets display led   
##    
def wave1Select():
    global currentOscillator1
    waveform1ToggleBtn = GPIO.input(25)
    if(waveform1ToggleBtn==1):
##        print('pressed')        
        if(currentOscillator1==0):##select sine            
##            print('sine')
            ##send OSC
            osc1TypeOSC = OSC.OSCMessage('/osc1/type')
            osc1TypeOSC.append(1)
            c.send(osc1TypeOSC)
            currentOscillator1=1
            ##set LED            
            GPIO.output(mux2s0, 0)
            GPIO.output(mux2s1, 0)
            GPIO.output(mux2s2, 0)
            
        elif(currentOscillator1==1):##select triangle                     
##            print('triangle')
            osc1TypeOSC = OSC.OSCMessage('/osc1/type')
            osc1TypeOSC.append(2)
            c.send(osc1TypeOSC)
            currentOscillator1=2
            GPIO.output(mux2s0, 1)
            GPIO.output(mux2s1, 0)
            GPIO.output(mux2s2, 0)
            
        elif(currentOscillator1==2):##select square            
##            print('square')
            osc1TypeOSC = OSC.OSCMessage('/osc1/type')
            osc1TypeOSC.append(3)
            c.send(osc1TypeOSC)            
            currentOscillator1=3
            GPIO.output(mux2s0, 0)
            GPIO.output(mux2s1, 1)
            GPIO.output(mux2s2, 0)
            
        elif(currentOscillator1==3):##select saw
##            print('saw')
            osc1TypeOSC = OSC.OSCMessage('/osc1/type')
            osc1TypeOSC.append(0)
            c.send(osc1TypeOSC)            
            currentOscillator1=0
            GPIO.output(mux2s0, 1)
            GPIO.output(mux2s1, 1)
            GPIO.output(mux2s2, 0)
            
        time.sleep(0.2)
        
##
## toggles between the waveforms for oscillator 2
## sends OSC messages and sets display led   
##   
def wave2Select():
    global currentOscillator2
    waveform2ToggleBtn = GPIO.input(21)
    if(waveform2ToggleBtn==1):
##        print('pressed')
        if(currentOscillator2==0):##select sine            
            ##send OSC
            osc2TypeOSC = OSC.OSCMessage('/osc2/type')
            osc2TypeOSC.append(1)
            c.send(osc2TypeOSC)
            currentOscillator2=1
            GPIO.output(mux3s0, 0)
            GPIO.output(mux3s1, 0)
            GPIO.output(mux3s2, 0)     
            
        elif(currentOscillator2==1):##select triangle                     
            osc2TypeOSC = OSC.OSCMessage('/osc2/type')
            osc2TypeOSC.append(2)
            c.send(osc2TypeOSC)
            currentOscillator2=2
            GPIO.output(mux3s0, 0)
            GPIO.output(mux3s1, 0)
            GPIO.output(mux3s2, 1)
            
        elif(currentOscillator2==2):##select square            
            osc2TypeOSC = OSC.OSCMessage('/osc2/type')
            osc2TypeOSC.append(3)
            c.send(osc2TypeOSC)            
            currentOscillator2=3
            GPIO.output(mux3s0, 0)
            GPIO.output(mux3s1, 1)
            GPIO.output(mux3s2, 0)
            
        elif(currentOscillator2==3):##select saw
            osc2TypeOSC = OSC.OSCMessage('/osc2/type')
            osc2TypeOSC.append(0)
            c.send(osc2TypeOSC)            
            currentOscillator2=0
            GPIO.output(mux3s0, 0)
            GPIO.output(mux3s1, 1)
            GPIO.output(mux3s2, 1)
            
        time.sleep(0.2)
        
##
## sets volume of sub oscillator
## sets glide time       
## sets master volume
##        
def master():
    ##read from adc    
    subVol = int(mcp1.read_adc(2))
    glide = (mcp1.read_adc(5))
    bend = (mcp2.read_adc(1))
    
    ##set sub oscillator values    
    subVolOSC = OSC.OSCMessage('/mix/osc3')
    subVolOSC.append((subVol/991.9))
    c.send(subVolOSC) 
    
    subOctOSC = OSC.OSCMessage('/osc3/octave')
    subOctOSC.append(-1)
    c.send(subOctOSC)

    subSemiOSC = OSC.OSCMessage('/osc3/semi')
    subSemiOSC.append(0)
    c.send(subSemiOSC)

    subTypeOSC = OSC.OSCMessage('/osc3/type')
    subTypeOSC.append(0)
    c.send(subTypeOSC)

    glideOSC = OSC.OSCMessage('/master/glide')
    glideOSC.append((glide/2.046))
    c.send(glideOSC)

    bendOSC = OSC.OSCMessage('/master/bend')
    bendOSC.append((bend/0.06))
    c.send(bendOSC)
    
    masterVolOSC = OSC.OSCMessage('/master/mastervol')
    masterVolOSC.append(0.8)
    c.send(masterVolOSC)
  

#Main loop:
try:
    startupSeq()
    while True:
        wave1Select()
        wave2Select()
        envelope()
        oscillator1()
        oscillator2()
        master()
        filter()
        filterSelect()
	shutdown()
except KeyboardInterrupt:
    GPIO.output(statusLED, 0)
    time.sleep(1)
#    GPIO.cleanup()
