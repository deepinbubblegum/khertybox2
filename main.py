#!/usr/bin/python3
from threading import Thread
from time import sleep
from khertylib import Connector, Filterbuffer, Decoder, rest_server,Decode_new,Filterbuffer_new

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
                    hex_buff = filter_buff.recv(bytes)
                    if hex_buff is not None:
                        type, msg_recv = dec.decode(hex_buff)
                        if type != None and type !=0: 
                            serv.send_message(msg_recv,msg_recv['pump_id'])
                    sleep(0.00005)
            except Exception as e:
                serial.close()
                conn = Connector()
                serial = conn.serial
                sleep(0.000014)
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
