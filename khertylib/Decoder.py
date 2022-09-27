from khertylib import Config
class Decoder:
    def __init__(self):
        self.conf = Config()
        self.pump_conf = self.conf.pump_type
        self.PricePerUnit = self.conf.price_per_uinit
        self.decimal_off_unit = self.conf.decimal_off_unit
        self.grade_select_pump = {}
        
    def decode(self, hex_pkg):
        decoded_type = None
        decoded_msg = None
        header_hex = hex_pkg[0]
        if header_hex[:3] == '0x0':  # pump number is it state data error
            pump_id = int(header_hex[3], 16)
            decoded_type = 0
            decoded_msg = {
                "type": 0,
                "pump_id" : pump_id,
                "status": "Unknown format"
            }

        elif header_hex[:3] == '0x6':  # pump number is it state off
            pump_id = int(header_hex[3], 16)
            decoded_type = 1
            decoded_msg = {
                "type": 1,
                "pump_id" : pump_id,
                "status": "off",
                "PriceUnitPeer": self.PricePerUnit,
                "decimal_preview_price": self.pump_conf[f'pump{pump_id}']['decimal_preview_price'],
                "decimal_preview_unit": self.pump_conf[f'pump{pump_id}']['decimal_preview_unit'],
                "speed_profile": self.pump_conf[f'pump{pump_id}']['speed_profile'],
            }

        elif header_hex[:3] == '0x7':  # pump number is it state call
            pump_id = int(header_hex[3], 16)
            decoded_type = 2
            decoded_msg = {
                "type": 2,
                "pump_id" : pump_id,
                "status": "call",
                "PriceUnitPeer": self.PricePerUnit,
                "decimal_preview_price": self.pump_conf[f'pump{pump_id}']['decimal_preview_price'],
                "decimal_preview_unit": self.pump_conf[f'pump{pump_id}']['decimal_preview_unit'],
                "speed_profile": self.pump_conf[f'pump{pump_id}']['speed_profile'],
            }

        elif header_hex[:3] == '0x9':  # pump number is it state busy and realtime price
            pump_id = int(header_hex[3], 16)
            msg_box_pkg = hex_pkg[1:]
            decoded_type = 3
            try:
                decoded_msg = self.realtime_price(pump_id, msg_box_pkg)
            except:
                pass

        elif header_hex == '0xba': # 4.9.2.1 Data Block Format
            # find pump id 0xb{number} or 0xc{number}
            pkg_pump_id = hex_pkg[3]
            if pkg_pump_id[:3] == '0xb':
                pump_id = int(pkg_pump_id[3], 16)
                if pump_id == 0:
                    pump_id = 16
            elif pkg_pump_id[:3] == '0xc':
                pump_id = int(pkg_pump_id[3], 16) + 9
            else:
                pump_id = None
            # find special funtion command code SF3, SF2, SF1 = index 6, 5, 4 
            sf1, sf2, sf3 = hex_pkg[4], hex_pkg[5], hex_pkg[6]
            sf_code = f'{sf3[3]}{sf2[3]}{sf1[3]}'
            if sf_code == '010':
                msg_box_pkg = hex_pkg[9:-4] # extract msg from data blox format
                msg_status = self.extended_pump_status(pump_id, msg_box_pkg) # call fun Extended Pump Status
                decoded_type = 4
                decoded_msg = msg_status
            
        elif header_hex == '0xff':
            rest_type = hex_pkg[1]
            if int(rest_type[3]) >= 1 and int(rest_type[3]) <= 3: # fx 1,2 or 3
                decoded_type = 5
                decoded_msg = self.transaction_decode(hex_pkg)
            elif rest_type == '0xf6':
                pass
                # decoded_type = 6
                # decoded_msg = self.pump_totals(hex_pkg)
        
        return decoded_type, decoded_msg
    
    def pump_totals(self, hex_pkg):
        msg_status = {}
        grade_number = int(hex_pkg[2][3], 16)
        print(grade_number)
        
    def pump_totals(self, hex_pkg):
        grade_hex = hex_pkg[2]
        grade = int(grade_hex[3], 16) + 1
        point_position = 6
        pump_vol_next = hex_pkg[3]
        if pump_vol_next == '0xf9':
            pump_vol_arr = hex_pkg[4:12]
            pump_vol_arr.reverse()
            pump_vol = ''
            for pump_vol_digit in pump_vol_arr:
                pump_vol += pump_vol_digit[3]
            pump_vol = float(f'{pump_vol[:point_position]}.{pump_vol[point_position:]}')
        pump_money_data_next = hex_pkg[12]
        if pump_money_data_next == '0xfa':
            point_position = 0
            pump_money_arr = hex_pkg[13:21]
            pump_money_arr.reverse()
            pump_money_total = ''
            for pump_money in pump_money_arr:
                pump_money_total += pump_money[3]
            # pump_money_total = float(f'{pump_money_total[:point_position]}.{pump_money_total[point_position:]}')
        msg_status = {
            "type": 6,
            'pump_vol_total': pump_vol,
            'pump_money_total': pump_money_total
        }
        return msg_status
    
    def transaction_decode(self, hex_pkg):
        pump_identifier_next = hex_pkg[2]
        if pump_identifier_next == '0xf8': # decode referent doc topic 4.5
            pump_identifier_data = hex_pkg[3]
            if pump_identifier_data == '0xeb':
                pump_number_hex = hex_pkg[4]
                pump_number = int(pump_number_hex[3], 16) + 1 #pump number start 0
            grade_data_next = hex_pkg[8]
            if grade_data_next == '0xf6':
                grade_number_hex = hex_pkg[9] # Grade position
                grade_number = int(grade_number_hex[3], 16) + 1
            transaction_type_next = hex_pkg[10]
            if transaction_type_next == '0xf4':
                transaction_type_level = 1
            elif transaction_type_next == '0xf5':
                transaction_type_level = 2
            else:
                transaction_type_level = None
            ppu_data_next = hex_pkg[11]
            if ppu_data_next == '0xf7':
                ppu_point_position = 2
                ppu_data_arr = hex_pkg[12:16]
                ppu_data_arr.reverse()
                price_per_unit = ''
                for ppu_data in ppu_data_arr:
                    price_per_unit += ppu_data[3]
                price_per_unit = float(f'{price_per_unit[:ppu_point_position]}.{price_per_unit[ppu_point_position:]}')
            transaction_vol_next = hex_pkg[16]
            if transaction_vol_next == '0xf9':
                point_position = 3 #3 when config position manual
                transaction_vol_arr = hex_pkg[17:23]
                # print(transaction_vol_arr)
                transaction_vol_arr.reverse()
                transaction_vol = ''
                for vol in transaction_vol_arr:
                    transaction_vol += vol[3]
                transaction_vol = float(f'{transaction_vol[:point_position]}.{transaction_vol[point_position:]}')
            transaction_money_next = hex_pkg[23]
            if transaction_money_next == '0xfa':
                point_position = self.decimal_off_unit
                transaction_money_arr = hex_pkg[24:30]
                transaction_money_arr.reverse()
                transaction_money = ''
                for money_data in transaction_money_arr:
                    transaction_money += money_data[3]
                transaction_money = float(f'{transaction_money[:point_position]}.{transaction_money[point_position:]}')
            msg_status = {
                "type": 5,
                "pump_id" : pump_number,
                "grade_number": grade_number,
                "transaction_type_level": transaction_type_level,
                "price_per_unit" : price_per_unit,
                "transaction_vol" : transaction_vol,
                "transaction_money" : transaction_money,
                "grade_type" : self.pump_conf_type(pump_number, grade_number),
                "decimal_preview_price": self.pump_conf[f'pump{pump_number}']['decimal_preview_price'],
                "decimal_preview_unit": self.pump_conf[f'pump{pump_number}']['decimal_preview_unit'],
                "speed_profile": self.pump_conf[f'pump{pump_number}']['speed_profile'],
            }
            if self.PricePerUnit[msg_status['grade_type']] != msg_status['price_per_unit']:
                self.conf.set_state(msg_status['grade_type'], msg_status['price_per_unit']) #update config
                self.PricePerUnit[msg_status['grade_type']] = msg_status['price_per_unit']
            try:
                address = self.pump_conf[f'pump{pump_number}']['address']
                # ip, port = address.split(":")
                # print(ip, port, "Close Preview")
                self.tringger.endtransaction(address=address, pump=pump_number)
            except:
                pass
            return msg_status
    
    # realtime price decode and format
    def realtime_price(self, pump_id, msg_box_pkg):
        msg_status = {}
        msg_box_pkg.reverse()
        price_decode = ''
        price_point_index = self.decimal_off_unit #5
        for msg in msg_box_pkg:
            price_decode += msg[3]
        try:
            price_realtime = float(f'{price_decode[:price_point_index]}.{price_decode[price_point_index:]}')
        except:
            print(msg_box_pkg)
        msg_status['type'] = 3
        msg_status['pump_id'] = pump_id
        try:
            msg_status['price'] = price_realtime
        except:
            print(msg_box_pkg)
        msg_status['PriceUnitPeer'] = self.PricePerUnit
        msg_status['decimal_preview_price'] = self.pump_conf[f'pump{pump_id}']['decimal_preview_price']
        msg_status['decimal_preview_unit'] = self.pump_conf[f'pump{pump_id}']['decimal_preview_unit']
        msg_status['speed_profile'] = self.pump_conf[f'pump{pump_id}']['speed_profile']
        try:
            msg_status['grade_type'] = self.grade_select_pump[str(pump_id)]['grade_type']
        except:
            pass
        return msg_status
    
    def pump_conf_type(self, pump_id, grade):
        str_pump_id = f'pump{str(pump_id)}'
        str_grade_id = f'grade{str(grade)}'
        pump_data = self.pump_conf[str_pump_id]
        grade_type = pump_data[str_grade_id]
        return grade_type
    
    # 4.9.4.4 Extended Pump Status (010)
    def extended_pump_status(self, pump_id, msg_box_pkg):
        grade_mesage = {}
        msg_status = {}
        msg_status['type'] = 4
        msg_status['pump_id'] = pump_id
        # msg_status['cmd_code_msd'] = msg_box_pkg[0]
        msg_status['price_lv_selection'] = int(msg_box_pkg[1][3])
        msg_status['grade_selection'] = int(msg_box_pkg[2][3])
        msg_status['pump_handle'] = int(msg_box_pkg[3][3])
        msg_status['push_to_start'] = int(msg_box_pkg[4][3])
        msg_status['selected_grade'] = int(msg_box_pkg[5][3]) # if 0 = Unknown grade
        msg_status['grade_type'] = self.pump_conf_type(pump_id, int(msg_box_pkg[5][3]))
        msg_status['PriceUnitPeer'] = self.PricePerUnit
        msg_status['decimal_preview_price'] = self.pump_conf[f'pump{pump_id}']['decimal_preview_price']
        msg_status['decimal_preview_unit'] = self.pump_conf[f'pump{pump_id}']['decimal_preview_unit']
        msg_status['speed_profile'] = self.pump_conf[f'pump{pump_id}']['speed_profile']
        
        # self.grade_select_pump['pump_id'] = pump_id
        grade_mesage['grade_selection'] = int(msg_box_pkg[2][3])
        grade_mesage['grade_type'] = self.pump_conf_type(pump_id, int(msg_box_pkg[5][3]))
        self.grade_select_pump[str(pump_id)] = grade_mesage
        # print(self.grade_select_pump)
        try:
            address = self.pump_conf[f'pump{pump_id}']['address']
            # ip, port = address.split(":")
            # print(ip, port, "Preview")
            self.tringger.tringger(address=address, pump=pump_id)
        except:
            pass
        return msg_status
