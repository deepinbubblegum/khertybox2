import requests

class TCPTrigger:
    def tringger(self, address, pump):
        if address != False:
            try:
                Trigger = {"Trigger": "p"}
                r = requests.post(address, json=Trigger, verify=False, timeout=0.001)
            except Exception as e:
                print(e)
                
    def endtransaction(self, address, pump):
        if address != False:
            try:
                Trigger = {"Trigger": "c"}
                r = requests.post(address, json=Trigger, verify=False, timeout=0.001)
            except Exception as e:
                print(e)