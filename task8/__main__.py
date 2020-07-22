from multiprocessing import Process, Queue
from pynats import NATSClient
import PySimpleGUI as sg


sg.theme('DarkAmber')


layout = [[sg.Text('Your Name'), sg.InputText(key='name')],
            [sg.Text('Room'), sg.InputText(key='room')],
            [sg.OK(), sg.Cancel()]]

# Create the Window
window = sg.Window('Login', layout)
# Event Loop to process "events"
close_me = False
room = None
name = None
while True:
    event, values = window.read()
    room = values.get('room')
    name = values.get('name')
    if len(room) > 0 and len(name) > 0:
        break
    if event in (sg.WIN_CLOSED, 'Cancel'):
        close_me = True
        break

window.close()
if close_me:
    exit(0)

in_queue = Queue()


def sub(que):
    def push_in_queue(msg):
        que.put(msg.payload.decode())

    with NATSClient(name=name+"sub") as client:
        client.subscribe(str(room), callback=push_in_queue)
        client.wait()


ps = Process(target=sub, args=(in_queue, ))
ps.start()

layout = [[sg.Output((100, 20),key='out')],
            [sg.Text('mesg'), sg.InputText(key='msg')],
            [sg.Ok()]]
window = sg.Window('room'+str(room)+':'+str(name), layout)

while True:
    event, values = window.read(100)
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    if event == 'Ok':
        txt = values.get('msg', None)
        if txt is not None and len(txt) > 0:
            with NATSClient(name=name + "pub") as client:
                client.publish(str(room), payload=str(name+": "+txt).encode())
    try:
        t = in_queue.get(block=False)
        print(t)
    except Exception:
        pass

window.close()
ps.kill()
ps.join()
