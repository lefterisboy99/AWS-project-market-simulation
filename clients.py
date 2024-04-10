import boto3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import multiprocessing
from multiprocessing import Process
from multiprocessing import Barrier
from multiprocessing import Manager , Pool
from random import seed
from random import randint


input_list = []

manager = Manager()
shared_list = manager.list()
messages = []

class MyHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        if self.path == '/msg':
            # Insert your code here
            print("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
            self._set_headers()
        # self.send_response(200)

    def do_POST(self):
        if self.path == '/msg':
            # Insert your code here
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length) # <--- Gets the data itself
            #print("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
            #    str(self.path), str(self.headers), post_data.decode('utf-8'))
            json_object = json.loads(post_data)
            #print(json_object["Message"])
            global messages
            #print(len(messages))
            messages = json.loads(json_object["Message"])
            for i in range(3):
                shared_list.append(messages[i])
            #print(len(messages))
            print("received msg")
            print(messages)
            #shared_list.append(messages)
            self._set_headers()
        # self.send_response(200)

def advert_func(barrier,id):
    # Get the service resource
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='Actionsqueue')
    for x in range(10):
        while True:
            if len(shared_list)==3:
                break
            
        #print(len(shared_list))
        #print(shared_list)
        
        i = randint(0,10)
        value = randint(0,1)
        msg={}
        if id==0:
            print("#Round",x+1)

        barrier.wait()
        if i>0 and i<6 :
            #print(shared_list[0]["Ad ID"],id,value)
            print()
            msg={"ADid":shared_list[0]["Ad ID"]["S"],"Bids":int(shared_list[0]["Bid"]["N"]),"Clicks":1,"Sales":value}
            print("ClientID: ",id," Ad ID: ",shared_list[0]["Ad ID"]["S"]," Purchase: ",value)
        elif i<9 :
            #print(shared_list[1]["Ad ID"],id,value)
            msg={"ADid":shared_list[1]["Ad ID"]["S"],"Bids":int(shared_list[1]["Bid"]["N"]),"Clicks":1,"Sales":value}
            print("ClientID: ",id," Ad ID: ",shared_list[1]["Ad ID"]["S"]," Purchase: ",value)
        else:
            #print(shared_list[2]["Ad ID"],id,value)
            msg={"ADid":shared_list[2]["Ad ID"]["S"],"Bids":int(shared_list[2]["Bid"]["N"]),"Clicks":1,"Sales":value}
            print("ClientID: ",id," Ad ID: ",shared_list[2]["Ad ID"]["S"]," Purchase: ",value)

        
        barrier.wait()
        if id==0:
            print("del")
            print(shared_list)
            print(len(shared_list))
            shared_list[:] = []
            print(len(shared_list))
           
        barrier.wait()
        
        queue.send_message(MessageBody= json.dumps(msg))
    



seed(1)

barrier = Barrier(10)

client0 = Process(target=advert_func, args=(barrier,0))
client1 = Process(target=advert_func, args=(barrier,1))
client2 = Process(target=advert_func, args=(barrier,2))
client3 = Process(target=advert_func, args=(barrier,3))
client4 = Process(target=advert_func, args=(barrier,4))
client5 = Process(target=advert_func, args=(barrier,5))
client6 = Process(target=advert_func, args=(barrier,6))
client7 = Process(target=advert_func, args=(barrier,7))
client8 = Process(target=advert_func, args=(barrier,8))
client9 = Process(target=advert_func, args=(barrier,9))


client0.start()
client1.start()
client2.start()
client3.start()
client4.start()
client5.start()
client6.start()
client7.start()
client8.start()
client9.start()

httpd = HTTPServer(("", 8080), MyHandler)#socketserver.TCPServer(("", 8080), MyHandler)
httpd.serve_forever()