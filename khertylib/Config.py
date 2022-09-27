import yaml

class Config:
    def __init__(self):
        conf = self.config_file()
        self.serial_conf = conf['serialport']
        self.pump_type = conf['pump_grade']
        self.price_per_uinit = conf['PricePerUnit']
        self.decimal_off_unit = conf['decimal_off_unit']
        
    def config_file(self):
        with open('config.yaml') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        return config
    
    def set_state(self, type, ppu):
        conf = self.config_file()
        conf['PricePerUnit'][type] = ppu
        with open('config.yaml', 'w') as f:
            yaml.dump(conf, f, sort_keys=False)