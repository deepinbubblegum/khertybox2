from khertylib import Config, TCPTrigger


class Decode_new:
    def __init__(self):
        self.conf = Config()
        self.pump_conf = self.conf.pump_type
        self.PricePerUnit = self.conf.price_per_uinit
        self.decimal_off_unit = self.conf.decimal_off_unit
        self.grade_select_pump = {}
        self.tringger = TCPTrigger()

    def decode(self, hex_pkg):
        decoded_type = None
        decoded_msg = None
        header_hex = hex_pkg[0]
        state = header_hex[0]
        match state:
            case '0':  # state data error
                pump_id = int(header_hex[1], 16)
                decoded_type = 0
                decoded_msg = {
                    "type": 0,
                    "pump_id": pump_id,
                    "status": "Unknown format"
                }
            case '6':  # state off
                pump_id = int(header_hex[1], 16)
                decoded_type = 1
                decoded_msg = {
                    "type": 1,
                    "pump_id": pump_id,
                    "status": "off",
                }
            case '7':  # state call
                pump_id = int(header_hex[1], 16)
                pump = f'pump{pump_id}'
                decoded_type = 2
                decoded_msg = {
                    "type": 2,
                    "pump_id": pump_id,
                    "status": "call",
                    "PriceUnitPeer": self.PricePerUnit,
                    "decimal_preview_price": self.pump_conf[pump]['decimal_preview_price'],
                    "decimal_preview_unit": self.pump_conf[pump]['decimal_preview_unit'],
                    "speed_profile": self.pump_conf[pump]['speed_profile'],
                }

            case '9':  # state busy and realtime price
                pump_id = int(header_hex[1], 16)
                msg_box_pkg = hex_pkg[1:]
                decoded_type = 3
                decoded_msg = self.realtime_price(pump_id, msg_box_pkg)

            case _:
                match header_hex:
                    case 'ba':
                        # find pump id 0xb{number} or 0xc{number}
                        pkg_pump_id = hex_pkg[3]
                        if pkg_pump_id[0] == 'b':
                            pump_id = int(pkg_pump_id[1], 16)
                            if pump_id == 0:
                                pump_id = 16
                        elif pkg_pump_id[0] == 'c':
                            pump_id = int(pkg_pump_id[1], 16) + 9
                        else:
                            pump_id = None
                        # find special funtion command code SF3, SF2, SF1 = index 6, 5, 4
                        sf1, sf2, sf3 = hex_pkg[4], hex_pkg[5], hex_pkg[6]
                        sf_code = f'{sf3[1]}{sf2[1]}{sf1[1]}'

                        if sf_code == '010':
                            # extract msg from data blox format
                            msg_box_pkg = hex_pkg[9:-4]

                            decoded_type = 4
                            decoded_msg = self.extended_pump_status(
                                pump_id, msg_box_pkg)  # call fun Extended Pump Status
                    case 'ff':
                        rest_type = hex_pkg[1]
                        if int(rest_type[1]) >= 1 and int(rest_type[1]) <= 3:  # fx 1,2 or 3
                            decoded_type = 5
                            decoded_msg = self.transaction_decode(hex_pkg)
        return decoded_type, decoded_msg

    # funcion for reduce codeing
    def grade_type_name(self, pump_id, grade):
        str_pump_id = f'pump{str(pump_id)}'
        str_grade_id = f'grade{str(grade)}'
        pump_data = self.pump_conf[str_pump_id]
        grade_type = pump_data[str_grade_id]
        return grade_type

    def reverse_read_data(self, data_array):
        data_array.reverse()
        result = ''
        for data in data_array:
            result += data[1]
        return result

    def text_to_float(self, full_text, decimal_places):
        integer = full_text[:decimal_places]
        decimal = full_text[decimal_places:]
        translate = float(f'{integer}.{decimal}')
        return translate
    # =================================

    # realtime price decode and format

    def realtime_price(self, pump_id, msg_box_pkg):

        price_decode = self.reverse_read_data(msg_box_pkg)
        price_realtime = self.text_to_float(
            price_decode, self.decimal_off_unit)

        data_status = {
            "type": 3,
            "pump_id": pump_id,
            "price": price_realtime,
            "PriceUnitPeer": self.PricePerUnit,
        }
        try:
            data_status['grade_type'] = self.grade_select_pump[str(pump_id)]['grade_type']
        except:
            pass

        return data_status

    # 4.9.4.4 Extended Pump Status (010)

    def extended_pump_status(self, pump_id, msg_box_pkg):
        grade_mesage = {}

        pump = f'pump{pump_id}'
        data_status = {
            "type": 4,
            "pump_id": pump_id,
            "grade_type": self.grade_type_name(pump_id, int(msg_box_pkg[5][1])),
            "PriceUnitPeer": self.PricePerUnit,
            "decimal_preview_price": self.pump_conf[pump]['decimal_preview_price'],
            "decimal_preview_unit": self.pump_conf[pump]['decimal_preview_unit'],
            "speed_profile": self.pump_conf[pump]['speed_profile'],
        }

        grade_mesage['grade_selection'] = int(msg_box_pkg[2][1])
        grade_mesage['grade_type'] = self.grade_type_name(
            pump_id, int(msg_box_pkg[5][1]))
        self.grade_select_pump[str(pump_id)] = grade_mesage
        try:
            address = self.pump_conf[f'pump{pump_id}']['address']
            self.tringger.tringger(address=address, pump=pump_id)
        except:
            print('open tringger error')

        return data_status

    def transaction_decode(self, command_box):  # decode referent doc topic 4.5

        pump_number = int(command_box[4][1], 16) + 1  # pump number start 0

        grade_number_hex = command_box[9]  # Grade position
        grade_number = int(grade_number_hex[1], 16) + 1

        transaction_type_next = command_box[10]
        if transaction_type_next == 'f4':
            transaction_type_level = 1
        elif transaction_type_next == 'f5':
            transaction_type_level = 2
        else:
            transaction_type_level = None

        ppu_point_position = 2
        ppu_data_arr = command_box[12:16]
        price_per_unit = self.reverse_read_data(ppu_data_arr)
        price_per_unit = self.text_to_float(price_per_unit, ppu_point_position)

        point_position = 3  # 3 when config position manual
        transaction_vol_arr = command_box[17:23]
        transaction_vol = self.reverse_read_data(transaction_vol_arr)
        transaction_vol = self.text_to_float(transaction_vol, point_position)

        point_position = self.decimal_off_unit
        transaction_money_arr = command_box[24:30]
        transaction_money = self.reverse_read_data(transaction_money_arr)
        transaction_money = self.text_to_float(
            transaction_money, point_position)

        data_status = {
            "type": 5,
            "pump_id": pump_number,
            "grade_number": grade_number,
            "transaction_type_level": transaction_type_level,
            "price_per_unit": price_per_unit,
            "transaction_vol": transaction_vol,
            "transaction_money": transaction_money,
            "grade_type": self.grade_type_name(pump_number, grade_number)
        }

        if self.PricePerUnit[data_status['grade_type']] != data_status['price_per_unit']:
            self.conf.set_state(
                data_status['grade_type'], data_status['price_per_unit'])  # update config
            self.PricePerUnit[data_status['grade_type']
                              ] = data_status['price_per_unit']
        try:
            address = self.pump_conf[f'pump{pump_number}']['address']
            self.tringger.endtransaction(address=address, pump=pump_number)
        except:
            print('close tringger error')

        return data_status
