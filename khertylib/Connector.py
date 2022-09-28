from time import sleep
import serial
from khertylib import Config
class Connector:
    def __init__(self):
        conf = Config()
        serial_conf = conf.serial_conf # Get config connector
        PARITY, BYTESIZE, STOPBITS = self.static_config_value()
        port=serial_conf['port'],
        baudrate=serial_conf['baudrate'],
        bytesize=BYTESIZE[serial_conf['bytesize']],
        parity=PARITY[serial_conf['parity']],
        stopbits=STOPBITS[serial_conf['stopbits']],
        print(f'port:{port}\nbaudrate:{baudrate}\nbytesize:{bytesize}\nparity:{parity}\nstopbits:{stopbits}')
        try:
            self.Serial = serial.Serial(
                port=serial_conf['port'],
                baudrate=serial_conf['baudrate'],
                bytesize=BYTESIZE[serial_conf['bytesize']],
                parity=PARITY[serial_conf['parity']],
                stopbits=STOPBITS[serial_conf['stopbits']],
                timeout=0.001,
            )
        except Exception as e:
            print("try connect serial port...")
            print(e)
            sleep(0.01)
            self.__init__()

    def static_config_value(self):
        PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'
        FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = (5, 6, 7, 8)
        STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = (1, 1.5, 2)
        PARITY = {
            "PARITY_NONE": PARITY_NONE,
            "PARITY_EVEN": PARITY_EVEN,
            "PARITY_ODD": PARITY_ODD,
            "PARITY_MARK": PARITY_MARK,
            "PARITY_SPACE": PARITY_SPACE
        }
        BYTESIZE = {
            "FIVEBITS": FIVEBITS, 
            "SIXBITS" : SIXBITS, 
            "SEVENBITS" : SEVENBITS, 
            "EIGHTBITS" : EIGHTBITS
        }
        STOPBITS = {
            "STOPBITS_ONE" : STOPBITS_ONE, 
            "STOPBITS_ONE_POINT_FIVE": STOPBITS_ONE_POINT_FIVE, 
            "STOPBITS_TWO" : STOPBITS_TWO
        }
        return PARITY, BYTESIZE, STOPBITS