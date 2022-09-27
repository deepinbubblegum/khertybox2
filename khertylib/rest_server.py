from flask import Flask
from flask_restful import Api, Resource
from flask_cors import CORS

data = [{}]*16


class rest_server:
    class mes(Resource):
        def get(self, id):
            return data[id]

    def __init__(self):
        global app
        global api
        app = Flask(__name__)
        CORS(app)

        api = Api(app)

        api.add_resource(self.mes, "/<int:id>")

    def send_message(self, msg, id):
        global data
        if len(data[id])!=0:
            if(data[id]['type']==5 and msg['type']==1):
                if('delay' in data[id]):
                    data[id]=msg
                else:
                    data[id]['delay']="delay"  #if not have any delay it will replace by type 1 before client request it
            else:
                data[id]=msg
        else:
            data[id]=msg

    def start(self):
        app.run()
