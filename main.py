#!/usr/bin/python3
from threading import Thread
from time import sleep
from khertylib import Connector, Filterbuffer, Decoder, rest_server,Decode_new,Filterbuffer_new
from datetime import datetime, timedelta

global now
global result
global file_name

now = datetime.now()
result = now + timedelta(minutes=2)
file_name = now.strftime("%d-%m-%Y_%H-%M-%S") + '.txt'

def save_packet(packet):
    now = datetime.now()
    if now > result:
        file_name = now.strftime("%d-%m-%Y_%H-%M-%S") + '.txt'
        result = now + timedelta(minutes=2)
    with open('./packet/' + file_name, "ab") as file:
        file.write(packet)

def update(serv):
    try:
        conn = Connector() # init connect serial port
        serial = conn.Serial
        # filter_buff = Filterbuffer()
        # dec = Decoder()
        
        filter_buff = Filterbuffer_new()
        dec = Decode_new()
        
        while True:
            try:
                while serial.in_waiting:
                    bytes = serial.read(1)
                    save_packet(bytes)
                    hex_buff = filter_buff.recv(bytes)
                    if hex_buff is not None:
                        type, msg_recv = dec.decode(hex_buff)
                        if type != None and type !=0: 
                            serv.send_message(msg_recv,msg_recv['pump_id'])
                    sleep(0.00017)
            except Exception as e:
                serial.close()
                sleep(0.00015)
                conn = Connector()
                serial = conn.serial
            sleep(0.00015)
    except Exception as e:
        print('something wrong...')
        print(e)
        
def main():
    serv = rest_server()
    thr_ = Thread(target=update, args=(serv,))
    thr_.daemon = True
    thr_.start()
    serv.start()
            
if __name__ == "__main__":
    main()

# from time import sleep
# import serial
# ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0.001)
# while True:
#     while ser.in_waiting:  # Or: while ser.inWaiting():
#         print(ser.read(1))
#     sleep(0.01)
