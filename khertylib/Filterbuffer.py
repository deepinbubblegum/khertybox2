from collections import deque
import threading
from time import sleep


class Filterbuffer:
    def __init__(self):
        self.buffer = deque(maxlen=4096)
        self.hex_buff = None
        self.buff_filter = []
        thr = threading.Thread(target=self.filter_hex, args=())
        thr.daemon = True
        thr.start()

    def recv(self, byte_recv):
        try:
            int_recv = int.from_bytes(byte_recv, "big")
            hex_data = hex(int_recv)
            # print(hex_data)
            if len(hex_data) == 4:
                self.buffer.append(hex(int_recv))
        except:
            print('something wrong drop data...')

        if self.hex_buff is None:
            return None
        else:
            ret = self.hex_buff
            self.hex_buff = None
            return ret

    def getData(self):
        if self.isNot_empty():
            return self.buffer.popleft()

    def isNot_empty(self):
        return len(self.buffer) > 0

    def rest_hex_data(self):
        self.hex_buff = self.buff_filter
        self.buff_filter = []

    def filter_hex(self):
        self.buff_filter = []
        while True:
            if self.isNot_empty():
                hex_recv = self.getData()
                if hex_recv[:3] == '0x0':
                    self.buff_filter.append(hex_recv)
                    self.rest_hex_data()

                elif hex_recv[:3] == '0x6':
                    self.buff_filter.append(hex_recv)
                    self.rest_hex_data()

                elif hex_recv[:3] == '0x7':
                    self.buff_filter.append(hex_recv)
                    self.rest_hex_data()

                elif hex_recv[:3] == '0x9':
                    buff_size = 6  # 7
                    count = 0
                    self.buff_filter.append(hex_recv)
                    while True:
                        if self.isNot_empty():
                            hex_recv = self.getData()
                            if hex_recv[2] != 'e':  # fix for tow way communication
                                continue
                            self.buff_filter.append(hex_recv)
                            count += 1
                            if count == buff_size:
                                self.rest_hex_data()
                                break
                        else:
                            sleep(0.01)

                elif hex_recv == '0xff':
                    buff_size = 33
                    counting = 0
                    self.buff_filter.append(hex_recv)
                    while True:
                        if self.isNot_empty():
                            hex_recv = self.getData()
                            self.buff_filter.append(hex_recv)
                            if len(hex_recv) > buff_size:
                                break
                            if hex_recv == '0xf0':
                                self.rest_hex_data()
                                break
                        else:
                            sleep(0.01)

                elif hex_recv == '0xba':
                    buff_size = 44
                    self.buff_filter.append(hex_recv)
                    while True:
                        if self.isNot_empty():
                            hex_recv = self.getData()
                            self.buff_filter.append(hex_recv)
                            if len(hex_recv) > buff_size:
                                break
                            if hex_recv == '0x8a':
                                self.rest_hex_data()
                                break
                        else:
                            sleep(0.01)
                hex_recv = None
            else:
                sleep(0.02)
