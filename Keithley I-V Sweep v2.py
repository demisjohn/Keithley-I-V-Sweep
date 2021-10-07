# -*- coding: utf-8 -*-
"""
Keithley I-V Sweep
Demis D. John, October 2014, Univ. of California Santa Barbara

Program to sweep voltage & measure current on Keithley SMU
Known bugs: With PythonXY, the plot window opens *behind* the current window.
Also, file is saved *usually* in same directory as this script - but at one point it kept saving into the PythonXY directory, which was confusing.  Probably need to set the Python working directory to be sure.

Edit/Run this file via Python(x,y) (click the 1st button to open the Spyder IDE)
Installed PyVISA for GPIB communication.

Spyder Editor. 
Based off Steve Nichols' Script from ~2010, Univ. of California Santa Barbara
"""

SaveFiles = True   # Save the plot & data?  Only display if False.

DevName = 'I-V Curve 01' # will be inserted into filename of saved plot
Keithley_GPIB_Addr = 22

CurrentCompliance = 1.0e-3    # compliance (max) current
start = -5.0     # starting value of Voltage sweep
stop = +5.0      # ending value 
numpoints = 100  # number of points in sweep



import visa          # PyVISA module, for GPIB comms
import numpy as N    # enable NumPy numerical analysis
import time          # to allow pause between measurements
import os            # Filesystem manipulation - mkdir, paths etc.

import matplotlib.pyplot as plt # for python-style plottting, like 'ax1.plot(x,y)'


# Open Visa connections to instruments
#keithley = visa.GpibInstrument(22)     # GPIB addr 22
rm = visa.ResourceManager()
keithley = rm.get_instrument(  'GPIB::' + str(Keithley_GPIB_Addr)  )


# Setup Keithley for  current loop
#keithley.write("*RST")
#keithley.write("SOUR:FUNC:MODE CURR")  # current source
#keithley.write("SOUR:CURR 0")          # set current to 0
#keithley.write('SENS:FUNC "VOLT"')   
#keithley.write('FORM:ELEM VOLT')
#keithley.write('SENS:VOLT:RANGE 3')
#keithley.write("SENS:VOLT:PROT:LEV " + str(CompVolt))  # set voltage compliance
#keithley.write(":OUTP ON")                             # turn on output
#print "gain keithley initialized ..."

# Setup electrodes as voltage source
keithley.write("*RST")
#print("reset the instrument")
time.sleep(0.5)    # add second between
keithley.write(":SOUR:FUNC:MODE VOLT")
keithley.write(":SENS:CURR:PROT:LEV " + str(CurrentCompliance))
keithley.write(":SENS:CURR:RANGE:AUTO 1")   # set current reading range to auto (boolean)
keithley.write(":OUTP ON")                    # Output on    


# Loop to sweep voltage
Voltage=[]
Current = []
for V in N.linspace(start, stop, num=numpoints, endpoint=True):
    #Voltage.append(V)
    print("Voltage set to: " + str(V) + " V" )
    keithley.write(":SOUR:VOLT " + str(V))
    time.sleep(0.1)    # add second between
    data = keithley.ask(":READ?")   #returns string with many values (V, I, ...)
    answer = data.split(',')    # remove delimiters, return values into list elements
    I = eval( answer.pop(1) ) * 1e3     # convert to number
    Current.append( I )
    
    vread = eval( answer.pop(0) )
    Voltage.append(vread)
    #Current.append(  I  )          # read the current
    
    print("--> Current = " + str(Current[-1]) + ' mA')   # print last read value
#end for(V)
keithley.write(":OUTP OFF")     # turn off

#set to current source, voltage meas
keithley.write(":SOUR:FUNC:MODE curr")
keithley.write(":SOUR:CURR " + str(CurrentCompliance))
keithley.write(":SENS:volt:PROT:LEV " + str(max(Voltage))  )
keithley.write(":SENS:volt:RANGE:AUTO 1")

keithley.write("SYSTEM:KEY 23") # go to local control
keithley.close()
    
    




###### Plot #####
    
fig1, ax1 = plt.subplots(nrows=1, ncols=1)         # new figure & axis

line1 = ax1.plot(Voltage, Current, 'b+-')

ax1.set_xlabel('Voltage (V)')
ax1.set_ylabel('Current (mA)')

ax1.set_title('I-V Curve - ' + DevName)


fig1.show()  # draw & show the plot - unfortunately it often opens underneath other windows
fig1.canvas.window().raise_()

if SaveFiles:
    # create subfolder if needed:
    if not os.path.isdir(DevName): os.mkdir(DevName)
    curtime = time.strftime('%Y-%M-%d_%H%M.%S')
    SavePath = os.path.join(DevName, 'I-V Curve - ' + DevName + ' - [' + curtime +']' )
    fig1.savefig(  SavePath + '.png'  )
    
    data = np.array(  zip(Current, Voltage)  )
    np.savetxt( SavePath + '.txt', data, fmt="%e", delimiter="\t", header="Current (A)\tVoltage (V)" )
    #np.array(Voltage).tofile(  os.path.join(DevName, 'I-V Voltage - ' + DevName + ' - [' + curtime +'].txt' )  )
    #np.array(Current).tofile(  os.path.join(DevName, 'I-V Current - ' + DevName + ' - [' + curtime +'].txt' )  )
#end if(SaveFiles)
