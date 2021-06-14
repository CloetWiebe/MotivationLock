import serial
import time
from RPi import GPIO
from repositories.DataRepository import DataRepository
import threading


ser = None


print("setup")
# ser = serial.Serial('/dev/serial0',9600,timeout=2) #timeout moet er staan
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)  # werkt ttyS0 => software of ttyAMA0 hardware
GPIO.setmode(GPIO.BCM)



def get_bpm():
    global ser
    print("get BPM")
    ser.write(str.encode("hartslag"))

       
def get_temp():
    global ser
    print("get temp")
    ser.write(str.encode("temp"))
   

def read_serialport():
    global ser
    # ser.write(b'hello')     # write a string
    recv_mesg = (ser.readline().decode(encoding='utf-8'))


    
    if (recv_mesg != ""):
        recv_mesg = float(recv_mesg)
        return(recv_mesg)
        #for i in recv_mesg:
        #   print(ord(i))
    #if (recv_mesg == "sensor1\r\n"):
    #    print("joepie")
    #if (recv_mesg == "sensor1"):
    #    print("en zonder extra's")
        
def value_bmp():
    get_bpm()
    time.sleep(0.5)
    value = read_serialport()
    print ("---printing value---")
    print(value)
    time.sleep(0.5)
    DataRepository.insert_hearrate(value)
    

def value_temp():
    get_temp()
    time.sleep(0.5)
    value = read_serialport()
    print ("---printing value---")
    print(value)
    DataRepository.insert_temp(value)
    time.sleep(0.5)





def get_value_sensors():
    while True:
        value_bmp()
        time.sleep(0.5)
        value_temp()

thread_sensors = threading.Thread(target=get_value_sensors)
thread_sensors.start()


