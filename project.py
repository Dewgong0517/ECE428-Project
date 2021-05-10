import os
import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import I2C_LCD_driver
from time import *
DHT_SENSOR=Adafruit_DHT.DHT22
DHT_PIN=22

L1 = 5
L2 = 6
L3 = 13
L4 = 19

C1 = 12
C2 = 16
C3 = 20
C4 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)
GPIO.setup(L3, GPIO.OUT)
GPIO.setup(L4, GPIO.OUT)

GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

mylcd = I2C_LCD_driver.lcd()

typed2=0
humid=0
unhumid=0
def readLine(line, characters,desired):
	noton=1
	typed=0
	while (noton == 1):

		GPIO.output(line, GPIO.HIGH)
		if(GPIO.input(C1) == 1 ):
			if typed == 0:
				desired+=characters[0]
				typed = 1

		elif(GPIO.input(C2) == 1):
			if typed == 0:
				desired+=characters[1]
				typed = 1
		elif(GPIO.input(C3) == 1):
			if typed ==0:
				desired+=characters[2]
				typed=1
		elif(GPIO.input(C4) == 1):
			if typed == 0:
				desired+=characters[3]
				typed=1
		else:
			noton=0

		GPIO.output(line, GPIO.LOW)

	return desired

def turnOnDesired(line, characters, desired):
	nothing=""
	GPIO.output(line, GPIO.HIGH)
	if(GPIO.input(C1) == 1):
		desired=""
		typed2=1
		mylcd.lcd_display_string("Desired=               ",2)
		while(typed2==1 or GPIO.input(C1) ==0):

			GPIO.output(line, GPIO.LOW)
			desired= readLine(L1, ["1","2","3","A"],desired)
			desired= readLine(L2, ["4","5","6","B"],desired)
			desired= readLine(L3, ["7","8","9","C"],desired)
			desired= readLine(L4, [nothing , "0", nothing, nothing],desired)
			mylcd.lcd_display_string("Desired= "+desired, 2)
			GPIO.output(line, GPIO.HIGH)
			if(GPIO.input(C1)==0):
				typed2=0
	while(GPIO.input(C1)==1):
		if(desired==""):
			desired="0"
	return desired

#os.system("python3 transmit.py -p 187 -t 1 4216115 or 4126124")

desired="50"
while True:
	humidity, temperature=Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
	
	if humidity is not None and temperature is not None:
		#mylcd.lcd_display_string("Temp={0:0.1f}*C".format(temperature), 1)
		mylcd.lcd_display_string("Humidity={0:0.1f}%".format(humidity), 1)
		mylcd.lcd_display_string("Desired= "+desired+"%               ", 2)
		desired=turnOnDesired(L4, ["*","0","#","D"],desired)
		if int(desired)>100:
			desired="100"
		if(humidity>int(desired) and humid==0):
			os.system("python3 transmit.py -p 187 -t 1 4216115")
			os.system("python3 transmit.py -p 187 -t 1 4216268")
			humid=1
			dehumid=0
		if(humidity<int(desired) and dehumid==0):
			os.system("python3 transmit.py -p 187 -t 1 4216259")
			os.system("python3 transmit.py -p 187 -t 1 4216124")
			dehumid=1
			humid=0

	else:
		print("Failed to retrieve data from sensor")
