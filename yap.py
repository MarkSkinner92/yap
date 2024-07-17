# Created by Mark Skinner, July 12, 2024

import socket
import threading
import json
import base64
import signal, sys
import copy

class YapPacket:

    def encode(topic, data):
        obj = {
            "topic":topic,
            "data":data
        }
        stringData = json.dumps(obj)
        return(stringData.encode()+b'\n')

    # Will return an array of messages, and a string of partial data
    def decode(raw):
        messages = []
        leftover = b''
        
        if b'\n' in raw:
            parts = raw.split(b'\n')

            for part in parts:
                if(len(part) > 0):
                    try:
                        messages.append(json.loads(part.decode('utf-8')))
                    except:
                        leftover = part
            
        else:
            messages = []
            leftover = raw
        
        return messages, leftover
    
class Yapper:

    def __init__(self,host='127.0.0.1', port=12345):
        self.port = port
        print("yap connection requested")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.messages = {}
        self.client_socket.bind(("", self.port))        
        self.listeningThread = threading.Thread(target=self.receive_messages, daemon=False)
        self.listeningThread.start()

    # Function to handle receiving messages from the server
    def receive_messages(self):
        leftover = b''
        while True:
            try:
                raw = self.client_socket.recvfrom(1024) # Tuple with (data,senderinfo)
                messages, leftover = YapPacket.decode(leftover+raw[0])

                for message in messages:
                    if message:
                        if self.messages.get(message['topic'], False):
                            queue = self.messages[message['topic']]
                            if(len(queue) >= 10):
                                queue.pop(0)
                            queue.append(message['data'])
                            # print("queue",message['topic'],len(queue))
                        else:
                            self.messages[message['topic']] = [message['data']]
                    else:
                        break

            except Exception as e:
                    print(type(e))
                    raise

    def send(self, topic, data):
        packet = YapPacket.encode(topic,data)
        self.client_socket.sendto(packet, ('<broadcast>', self.port))
    
    def getMessages(self, topic):
        returns = []

        if(self.messages.get(topic,False)):
            returns = copy.deepcopy(self.messages[topic])
            self.messages[topic].clear()
            return returns
        
        return []

    def waitForMessages(self, topic):
        returns = []

        while (not self.messages.get(topic, False)):
              pass

        if(self.messages.get(topic,False)):
            returns = copy.deepcopy(self.messages[topic])
            self.messages[topic].clear()
            return returns
        
        return []

    def shutup(self):
        self.client_socket.close()
        pass