from datetime import datetime, timedelta

def save_packet(packet, now, result, file_name):
    now = datetime.now()
    if now > result:
        file_name = now.strftime("%d-%m-%Y_%H-%M-%S") + '.txt'
        result = now + timedelta(minutes=2)
    with open('./packet/' + file_name, "a") as file:
        file.write(packet)

now = datetime.now()
result = now + timedelta(minutes=2)
file_name = now.strftime("%d-%m-%Y_%H-%M-%S") + '.txt'
save_packet('test', now, result, file_name)