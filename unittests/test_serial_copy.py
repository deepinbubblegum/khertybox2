import datetime
from time import sleep
import serial
import random

PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'
STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = (1, 1.5, 2)
FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = (5, 6, 7, 8)

Serial = serial.Serial(
    port="COM4",
    baudrate=9600,
    bytesize=EIGHTBITS,  # FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS
    parity=PARITY_NONE, # PARITY_NONE, PARITY_EVEN, PARITY_ODD PARITY_MARK, PARITY_SPACE
    stopbits=STOPBITS_ONE, # STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO
    timeout=None,
)

def sleeping():
    ran = random.uniform(0.02, 0.03)
    # print(f'sleeping {ran}')
    sleep(ran)

with open("unittests\\resource\\esso_logs_clean.txt") as log_file:
    lines = log_file.readlines()
while True:
    for line in lines:
        data_array = line.split()
        for data in data_array:
            data = data.upper()
            hex_data = int("0x"+ data, 16)
            # print(hex(hex_data))
            bytes_val = hex_data.to_bytes(1, 'big')
            if bytes_val != b'0x00':
                Serial.write(bytes_val)
                print(hex(hex_data))
            sleeping()
    print("running")
    