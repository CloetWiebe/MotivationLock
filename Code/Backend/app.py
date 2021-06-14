from flask.wrappers import Request
from repositories.Database import Database
import time
from RPi import GPIO
from repositories.DataRepository import DataRepository
import serial
from subprocess import check_output
from flask_cors import CORS
from flask_socketio import SocketIO, emit, send
import threading
from flask import Flask, jsonify, request
import os

ips = (check_output(['hostname', '-I']).decode(encoding='utf-8').split(" "))
ip = ips[1]
print(ip)

ser = None
ser2 = None
db0 = 4
db1 = 17
db2 = 27
db3 = 22
db4 = 5
db5 = 6
db6 = 13
db7 = 19
rs = 24
e = 23

gewenstecal = 0
geslacht = ""
leeftijd = 0
gewicht = 0

tot_cal = 0
cal_ver = 0
thread_running = False
prog_running = False

button = 16

databits = [db0, db1, db2, db3, db4, db5, db6, db7]

initclear = 0

servo = 12
frequencyHertz = 50
limit_open = 21
limit_gesloten = 20
status_open = "leeg"
status_sluiten = "leeg"
command = ""


def button_pressed(param):
    print("======================================Shutdown now============================")
    os.system("sudo shutdown now")


def is_open(parameter):
    global status_open
    # print("status_open: stop")
    status_open = "stop"


def is_gesloten(parameter):
    global status_sluiten
    # print("status_sluiten: stop")
    status_sluiten = "stop"

print("setup")
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
ser2 = serial.Serial('/dev/ttyUSB0', 9600, timeout=2)

GPIO.setmode(GPIO.BCM)
GPIO.setup(databits, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(rs, GPIO.OUT)
GPIO.setup(e, GPIO.OUT)
GPIO.output(e, GPIO.HIGH)

GPIO.setup(servo, GPIO.OUT)
GPIO.setup(limit_open, GPIO.IN)
pwm = GPIO.PWM(servo, frequencyHertz)
GPIO.add_event_detect(limit_open, GPIO.FALLING,
                      callback=is_open, bouncetime=200)
GPIO.setup(limit_gesloten, GPIO.IN)
GPIO.add_event_detect(limit_gesloten, GPIO.FALLING,
                      callback=is_gesloten, bouncetime=200)
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(button, GPIO.FALLING,
                      callback=button_pressed, bouncetime=200)


# code voor flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'geheim!'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False,
                    engineio_logger=False, ping_timeout=1)

CORS(app)


# berekenen verbrande calorieen
def verbrande_calorieen(bpm):
    global geslacht
    global leeftijd
    global gewicht
    if geslacht == "m":
        calpermin = ((-55.0969 + (0.6309 * bpm) +
                     (0.1988 * gewicht) + (0.2017 * leeftijd))/4.184)
        return calpermin
    elif geslacht == "v":
        calpermin = ((-20.4022 + (0.4472 * bpm) +
                     (0.1263 * gewicht) + (0.074 * leeftijd))/4.184)
        return calpermin

# ------------------------------------------------------LEDSTRIP


def led_groen():
    global ser2
    print("Groen")
    ser2.write(str.encode("groen"))

def led_oranje():
    global ser2
    print("Oranje")
    ser2.write(str.encode("oranje"))

def led_rood():
    global ser2
    print("Rood")
    ser2.write(str.encode("rood"))

def led_uit():
    global ser2
    print("Uit")
    ser2.write(str.encode("uit"))

def update_led_strip():
    global prefstate
    global gewenstecal
    global tot_cal
    print("Ledstrip started")

    percentcal = int((tot_cal/gewenstecal)*100)
    data = DataRepository.get_recent_color()
    prefstate = data['Waarde']
    print("prefstate: ", prefstate)

    if percentcal < 50 and prefstate != 1:
        led_rood()
        DataRepository.insert_color(1)

    elif 50 =< percentcal < 80 and prefstate != 2:
        led_oranje()
        DataRepository.insert_color(2)

    elif 80 =< percentcal and prefstate != 3 and percentcal < 100:
        led_groen()
        DataRepository.insert_color(3)

    elif 100 <= percentcal:
        print("Doel bereikt")
        reset()


# ---------------------------------------------------------------LCD
def send_instruction(value):
    # print("Intruction")
    GPIO.output(rs, GPIO.LOW)
    GPIO.output(e, GPIO.HIGH)
    set_data_bits(value)
    GPIO.output(e, GPIO.LOW)
    time.sleep(0.005)
    GPIO.output(e, GPIO.HIGH)

def send_character(value):
    # print("Character")
    GPIO.output(rs, GPIO.HIGH)
    GPIO.output(e, GPIO.HIGH)
    set_data_bits(value)
    GPIO.output(e, GPIO.LOW)
    time.sleep(0.005)
    GPIO.output(e, GPIO.HIGH)

def init_LCD():
    global initclear
    # print("LCD")
    send_instruction(0x38)
    time.sleep(0.005)
    send_instruction(0x0C)
    time.sleep(0.005)
    if initclear == 0:
        send_instruction(0x01)
        initclear = 1

def set_data_bits(value):
    mask = 0x01
    for i in range(0, 8):
        pin = databits[i]
        if value & mask:
            GPIO.output(pin, GPIO.HIGH)
        else:
            GPIO.output(pin, GPIO.LOW)
        mask = mask << 1


def write_message(message):
    list_message = list(message)
    first_list = list_message[:16]
    second_list = list_message[16:]
    for char in first_list:
        send_character(ord(f"{char}"))
    go_to_new_line()
    for char in second_list:
        send_character(ord(f"{char}"))


def go_to_new_line():
    value = 0x80 | 0x40
    send_instruction(value)


def go_to_first_line():
    value = 0x80
    send_instruction(value)

# -----------------------------------------------------------------thread lcd


def lcd_display_ip():
    print("LCD display go")
    while True:
        init_LCD()
        go_to_first_line()
        write_message("IP:")
        go_to_new_line
        write_message(ip)

#----------------------------------------------------------------Sensors
def get_moved():
    global ser
    ser.write(str.encode("mpu6050"))

def get_bpm():
    global ser
    # print("get BPM")
    ser.write(str.encode("hartslag"))
    
def get_temp():
    global ser
    # print("get temp")
    ser.write(str.encode("temp"))
   
def read_serialport():
    global ser
    # ser.write(b'hello')     # write a string
    recv_mesg = (ser.readline().decode(encoding='utf-8'))

    if (recv_mesg != ""):
        recv_mesg = float(recv_mesg)
        return(recv_mesg)
        # for i in recv_mesg:
        #   print(ord(i))
    # if (recv_mesg == "sensor1\r\n"):
    #    print("joepie")
    # if (recv_mesg == "sensor1"):
    #    print("en zonder extra's")


def value_bmp():
    get_bpm()
    value = read_serialport()
    # print ("---printing value---\n\tBPM")
    # print(value)
    if value == None:
        # print("Auto bpm 90")
        DataRepository.insert_hearrate(90)
    else:
        DataRepository.insert_hearrate(value)


def value_temp():
    get_temp()
    value = read_serialport()
    # print ("---printing value---")
    # print(value)
    DataRepository.insert_temp(value)

def value_moved():
    get_moved()
    value = read_serialport()
    # print ("---printing value---\n\tMoved")
    # print(value)
    DataRepository.insert_moved(value)

# ---------------------------------------------------------------Data


def data_cal_en_hart():
    global gewenstecal
    global tot_cal
    global cal_var

    # heartrate
    # print("Gewenste cal", gewenstecal)
    databmp = DataRepository.read_avg_hearrate()
    # print("Databmp: ", databmp)
    bmp = databmp['Gemiddelde']
    # print("bmp: ", bmp)
    socketio.emit('B2F_bpm', {'bpm': bmp}, broadcast=True)

    # Calorieen
    aantal_verbrande_cal_min = verbrande_calorieen(bmp)
    # print("Verbrande cal per min", aantal_verbrande_cal_min)
    DataRepository.insert_cal(aantal_verbrande_cal_min)
    cal_ver = aantal_verbrande_cal_min
    tot_cal = tot_cal + cal_ver
    # print(f"Aantal Verbrande Calorieen: {aantal_verbrande_cal_min}")
    socketio.emit('B2F_cal', {'verbrandecal': aantal_verbrande_cal_min,
                  'goalcal': gewenstecal, 'totverbrand': tot_cal}, broadcast=True)


def data_temp():
    datatemp = DataRepository.read_avg_temp()
    temp = datatemp['Gemiddelde']
    socketio.emit('B2F_temp', {'temp': temp}, braodcast=True)


def data_move():
    datamoved = DataRepository.read_moved()
    # print(datamoved)
    moved = datamoved['Waarde']
    # print(moved)
    socketio.emit('B2F_moved', {'moved': moved}, broadcast=True)


def data_tot_cal_per_day():
    listdata = DataRepository.get_total_cal_by_day()
    socketio.emit('B2F_totcalday', {'meetingen': listdata}, broadcast=True)


# ---------------------------------------------------------thread sensors
def get_value_sensors():
    print("Get value sensors go")
    while True:
        if thread_running == True:
            try:
                value_bmp()
                value_temp()
                value_moved()
            except BaseException as e:
                print(f"Restarting thread {e}")


def send_data_B2F():
    print("Send data go")
    while True:
        if thread_running == True:
            try:
                time.sleep(60)
                print("Collecting data")
                data_cal_en_hart()
                data_temp()
                data_move()
                data_tot_cal_per_day()
                update_led_strip()
            except BaseException as e:
                print(f"Restarting thread {e}")

# -----------------------------------------------------------thread servo


def servo_functie():
    print("Servo active")
    while True:
        # print("-----------------------------Statussen begin loop----------------------")
        # print("status_open", status_open)
        # print("status_gesloten", status_sluiten)
        # print("Command", command)
        # print("------------------------------------------------------------------------")
        pwm.start(0)
        if command == "openen" and status_open != "stop":
            while status_open != "stop":
                A = 8.5
                pwm.start(A)
            if status_open == "stop":
                pwm.start(0)
                DataRepository.insert_unlock()
        if command == "sluiten" and status_sluiten != "stop":
            while status_sluiten != "stop":
                A = 6.5
                pwm.start(A)
            if status_sluiten == "stop":
                pwm.start(0)
                DataRepository.insert_unlock()

        # print("A=", A)
        # command = input("Sluiten of openen: ")
        # status_sluiten = "leeg"
        # status_open = "leeg"


# reset
def reset():
    global gewenstecal
    global geslacht
    global leeftijd
    global gewicht
    global tot_cal
    global cal_ver
    global prefstate
    global thread_running
    global command
    global status_sluiten
    global status_open

    print("----------------------------Reset----------------------------")

    status_sluiten = ""
    status_open = ""
    command = "openen"
    print("Command: ", command)
    print("status open", status_open)
    print("status gesloten", status_sluiten)
    led_uit()
    DataRepository.insert_color(0)

    gewenstecal = 0
    geslacht = ""
    leeftijd = 0
    gewicht = 0

    tot_cal = 0
    cal_ver = 0
    thread_running = False
    print("Thread running = false")


thread_sensors = threading.Thread(target=get_value_sensors)
thread_data = threading.Thread(target=send_data_B2F)
thread_lcd = threading.Thread(target=lcd_display_ip)
thread_servo = threading.Thread(target=servo_functie)


@socketio.on('F2B_start')
def start(data):
    global gewenstecal
    global geslacht
    global leeftijd
    global gewicht
    global thread_running
    global command
    global status_open
    global status_sluiten
    global prog_running

    print("-----------------------------Start----------------------------")

    gewenstecal = float(data['gewenstecal'])
    # print(gewenstecal)

    geslacht = data['geslacht']
    # print(geslacht)

    gewicht = float(data['gewicht'])
    # print(gewicht)

    leeftijd = float(data['leeftijd'])
    # print(leeftijd)
    thread_running = True
    print("thread running = True")

    status_sluiten = ""
    status_open = ""
    command = "sluiten"
    print("status open", status_open)
    print("status gesloten", status_sluiten)
    led_uit()
    DataRepository.insert_color(0)
    if thread_running == True and prog_running != True:
        print("Tis wao")
        thread_servo.start()
        thread_sensors.start()
        thread_data.start()
        prog_running = True


thread_lcd.start()


@socketio.on('F2B_reset')
def reset_knop(data):
    reset()


if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
