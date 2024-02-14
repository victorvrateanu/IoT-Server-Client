import socket
import numpy
import encodings
import Adafruit_DHT
import time
import board
from _thread import*
import os
import time
import RPi.GPIO as GPIO
import RPi_I2C_driver
import datetime
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

#definim HOSTUL si portul
HOST = '192.168.100.10'
PORT = 65405
inchidere = 0
ThreadCounter = 0

#LCD Display
lcd = RPi_I2C_driver.lcd()
lcd.lcd_display_string("EVERYTHING WORKS",1)
lcd.lcd_display_string("ASTEPT CLIENT",2)


#senzor distanta
GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 22
GPIO_ECHO = 24
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

#senzor temperatura si distanta
dht22_senzor = Adafruit_DHT.DHT22
# Delay in-between sensor readings, in seconds.
DHT_READ_TIMEOUT = 5
DHT_DATA_PIN = 23


#functie de test pentru transmiterea datelor
def test_trimitere():
	x1 = numpy.random.randint(0,55, None)
	y1 = numpy.random.randint(56,99, None)
	senzor = "{},{}".format(x1,y1) # returneaza datele sperate prin ,
	print(senzor)
	return senzor
	

def senzor_distanta():

	GPIO.output(GPIO_TRIGGER, True)
	time.sleep(0.0001)
	GPIO.output(GPIO_TRIGGER, False)
	
	
	StartTime = time.time()
	StopTime = time.time()
	
	#calculare timp pana sunetul ajunge la obiect
	while GPIO.input(GPIO_ECHO) == 0:
		StartTime= time.time()
		
	while GPIO.input(GPIO_ECHO) == 1:
		StopTime = time.time()
	
	# diferenta intre start si arrival
	TimeElapsed = StopTime - StartTime
	distance = (TimeElapsed * 34300) /2
	
	
	return distance

def citire_senzori():
	
	temperatura = None
	umiditate = None
	#citire distanta
	try:
		distanta = senzor_distanta()
	except:
		print("eroare citire senzor distanta")
	
	#citire temp si umiditate
	try:
		umiditate,temperatura = Adafruit_DHT.read_retry(dht22_senzor, 
		DHT_DATA_PIN)
	except RuntimeError as error:
		print(error.args[0])
	except Exception as error:
		print(error.args[0])
		raise error
	except eroare:
		print("aia e")
	
	if umiditate is not None and temperatura is not None:
		print('Temp={0:0.1f}C Umiditate={1:0.1f}% Distanta={2:0.1f} cm'
		.format(temperatura,umiditate,distanta))
		
		date = '{},{},{}'.format(temperatura,umiditate,distanta)
		return date
	




def server_mt(conexiune):
			
		#generarea keyilor
		cheie_privata = RSA.generate(1024)	
		cheie_publica = cheie_privata.publickey()
		
		#exportare cheie publica in format PEM
		pem_cheie_publica = cheie_publica.export_key()
		
		#pregatire cifru RSA
		cifru_rsa = PKCS1_OAEP.new(cheie_privata)
		
		conexiune.sendall(pem_cheie_publica)   # trimitere cheie publica
		
		pem_client_cheie_publica = conexiune.recv()
		client_public_key = RSA.import_key(pem_client_cheie_publica)
		cifru_rsa_date = PKCS1_OAEP(client_public_key)
		
			
		while True:
			
			date = conexiune.recv(1024)  # asteapta comanda de la client
			print(date)
			date = cifru_rsa.decrypt(date)
			date = date.decode('utf-8')
			print("===========" +date)
			if str(date.strip().lower()) == "date":
				print(" Trimit datele ")
				tr_date = citire_senzori()
				encoded_data = tr_date.encode('utf-8')
				encoded_data = cifru_rsa_date.encrypt(encoded_data)
				conexiune.sendall(encoded_data)   #trimite datele spre client
							
					
			elif str(date.strip().lower()) == "quit":
				print("bye")
				global ThreadCounter 
				ThreadCounter -=1
				lcd.lcd_clear()
				lcd.lcd_display_string("Clienti",1)
				lcd.lcd_display_string("conectati: {}"
				.format(ThreadCounter),2)
				break

			elif str(date.strip().lower()) == "qserver":
				print("Serverul a fost inchis")
				inchidere = 1
				break
			else:
				pass
				
			if not date:
				print("bye")
				ThreadCounter -=1
				lcd.lcd_clear()
				lcd.lcd_display_string("Clienti",1)
				lcd.lcd_display_string("conectati: {}"
				.format(ThreadCounter),2)
				break



	
	
def stab_conexiune():
	
	#AF_INET = familia de adrese a internetului
	#SOCK_STREAM = protocolul TCP folosit la transmiterea mesajelor
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:    
		

		print("Servarul asteapta conexiunea")
		
		try:
			server.bind((HOST, PORT))   # adauga portul si adresa
		except socket.error as e:
			print(str(e))
		
		
		server.listen(5)      	   # asteapta conexiunea | max 5 conex.
		
		while True:
			
			
			conexiune, adresa = server.accept() #se accepta noul client
			global ThreadCounter
			ThreadCounter += 1     #incrementam cu 1 nr de clienti
			
			print("Clienti actuali: {}".format(ThreadCounter))
			lcd.lcd_display_string("Clienti"
			.format(ThreadCounter),1)
			lcd.lcd_display_string("conectati: {}"
			.format(ThreadCounter),2)

			
			start_new_thread(server_mt,(conexiune,)) 
		server.close()
	

		
					
if __name__ == '__main__':
	
	while 1:
		stab_conexiune()
		citire_senzori()
		time.sleep(1)
