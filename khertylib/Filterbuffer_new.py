from collections import deque


class Filterbuffer_new:
    def __init__(self):
        self.buffer = deque(maxlen=4096)
        self.hex_buff = None
        self.buff_filter = []
        self.mode = 0
        self.count = 0

    def recv(self, byte_recv):
        try:
            hex_data = byte_recv.hex()
            self.buffer.append(hex_data)
            hex_recv = self.getData()
            match [self.mode, hex_recv[0], hex_recv[1]]:
                # when mode 0 && 0 is unknow 6 is off 7 is call && _ mean pump id can be everything
                case [0, '0' | '6' | '7', _]:
                    self.buff_filter.append(hex_recv)
                case [0, '9', _]:
                    self.SetHeaderType_and_waitmore(hex_recv, 1, 6)
                    self.count = 0
                case [0, 'f', 'f']:
                    self.SetHeaderType_and_waitmore(hex_recv, 2, 33)
                case [0, 'b', 'a']:
                    self.SetHeaderType_and_waitmore(hex_recv, 3, 44)
                case [1, _, _]:  # mode after 9{x}
                    # recive only e{x} to make e2 e0 e1 e0 e0 e0 =0001.02 in Decoder
                    if hex_recv[0] == 'e':
                        self.buff_filter.append(hex_recv)
                        self.count += 1
                        if self.count == self.buff_size:
                            self.mode = 0
                case [2, _, _]:  # mode after FF
                    self.buff_filter.append(hex_recv)
                    if len(hex_recv) > self.buff_size:
                        self.mode = 0
                    if hex_recv == 'f0':
                        self.mode = 0
                    pass
                case [3, _, _]:  # mode after BA
                    self.buff_filter.append(hex_recv)
                    if len(hex_recv) > self.buff_size:
                        self.mode = 0
                    if hex_recv == '8a':
                        self.mode = 0

        except Exception as e:
            print('something wrong drop data...')
            print(e)

        if self.mode == 0 and self.buff_filter != []:
            temp = self.buff_filter
            self.buff_filter = []
            return temp
        else:
            return None

    def getData(self):
        if self.isNot_empty():
            return self.buffer.popleft()

    def isNot_empty(self):
        return len(self.buffer) > 0

    def SetHeaderType_and_waitmore(self, head, mode, wait):
        self.buff_filter.append(head)
        self.buff_size = wait
        self.mode = mode
