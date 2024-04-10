import boto3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import multiprocessing
from multiprocessing import Process
from multiprocessing import Barrier
from multiprocessing import Manager , Pool

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
            global messages
            messages = json.loads(json_object["Message"])
            for i in range(3):
                shared_list.append(messages[i])
            self._set_headers()
        # self.send_response(200)

def advert_func(barrier,id):
    # Get the service resource
    msg={"ADid":id,"Bids":id+4}
    bid=id+4
    new_bid=bid
    #print(msg)
    if id==0:
        print("#Round1")
    barrier.wait()
    print("Ad ID: ",id ," Bid: ",bid)
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='Bidsqueue')
    queue.send_message(MessageBody= json.dumps(msg))

    barrier.wait()
    for x in range(9):
        while True:
            if len(shared_list)==3:
                break

        #print(len(shared_list))
        #print(shared_list)
        if id==0:
            print("#Round",x+2)
        
        barrier.wait()
        for i in range(3):
            if id==int(shared_list[i]["Ad ID"]["S"]):
                #print(shared_list[i]["Ad ID"]["S"])
                #print(shared_list[i]["Clicks"]["N"])
                #print(shared_list[i]["Sales"]["N"])
                if int(shared_list[i]["Clicks"]["N"])- int(shared_list[i]["Sales"]["N"]) > 3 :
                    bid=new_bid
                    new_bid=new_bid-1
                    if new_bid==0:
                        new_bid=1
                    
                    msg={"ADid":id,"Bids":new_bid} 
                    print("Ad ID: ",id ," Revenues: ",int(shared_list[i]["Sales"]["N"])*10," Cost: ",int(shared_list[i]["Clicks"]["N"])*bid," Profit: ",int(shared_list[i]["Sales"]["N"])*10-int(shared_list[i]["Clicks"]["N"])*bid," Increase: ",new_bid-bid," From: ",bid," To: ",new_bid)
                elif int(shared_list[i]["Clicks"]["N"])- int(shared_list[i]["Sales"]["N"])<2:
                    bid=new_bid
                    new_bid=new_bid+1
                    msg={"ADid":id,"Bids":new_bid}
                    print("Ad ID: ",id ," Revenues: ",int(shared_list[i]["Sales"]["N"])*10," Cost: ",int(shared_list[i]["Clicks"]["N"])*bid," Profit: ",int(shared_list[i]["Sales"]["N"])*10-int(shared_list[i]["Clicks"]["N"])*bid," Increase: ",new_bid-bid," From: ",bid," To: ",new_bid)
                else :
                    bid=new_bid
                    msg={"ADid":id,"Bids":new_bid}
                    print("Ad ID: ",id ," Revenues: ",int(shared_list[i]["Sales"]["N"])*10," Cost: ",int(shared_list[i]["Clicks"]["N"])*bid," Profit: ",int(shared_list[i]["Sales"]["N"])*10-int(shared_list[i]["Clicks"]["N"])*bid," Increase: ",new_bid-bid," From: ",bid," To: ",new_bid)

                


        barrier.wait()
        if id==0:
            print("del")
            print(shared_list)
            shared_list[:] = []
           
        barrier.wait()
        queue.send_message(MessageBody= json.dumps(msg))


barrier = Barrier(3)

proc0 = Process(target=advert_func, args=(barrier,0))
proc1 = Process(target=advert_func, args=(barrier,1))
proc2 = Process(target=advert_func, args=(barrier,2))
proc0.start()
proc1.start()
proc2.start()

httpd = HTTPServer(("", 8080), MyHandler)#socketserver.TCPServer(("", 8080), MyHandler)
httpd.serve_forever()