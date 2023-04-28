import serial 
import time

# Open the serial port at the specified baudrate
ser = serial.Serial('/dev/cu.usbmodem14101', 9600)

# Write the data to the serial port 
while True:
	data = 'G'
	ser.write(data.encode())
	time.sleep(0.2) 
	data = 'P' 
	ser.write(data.encode())
# Close the serial port
ser.close()
