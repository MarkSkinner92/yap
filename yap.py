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
        print("yap connection requested")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

        while not self.connected:
            try:
                self.client_socket.connect((host, port))
                self.connected = True
            except:
                print("Waiting for the yap server to start...")

        self.messages = {}
        self.clearMessageRequest = False
        
        self.listeningThread = threading.Thread(target=self.receive_messages, daemon=False)
        self.listeningThread.start()

    # Function to handle receiving messages from the server
    def receive_messages(self):
        leftover = b''
        while True:
            # try:
            raw = self.client_socket.recv(1024)
            messages, leftover = YapPacket.decode(leftover+raw)

            for message in messages:
                if message:
                    if self.messages.get(message['topic'], False):
                        queue = self.messages[message['topic']]
                        if(len(queue) >= 10):
                            queue.pop(0)
                        queue.append(message['data'])
                        print("queue",message['topic'],len(queue))
                    else:
                        self.messages[message['topic']] = [message['data']]
                else:
                    break
            
            # except Exception as e:
            #     if isinstance(e, json.JSONDecodeError) or isinstance(e, TypeError):
            #         print("Message dropped")
            #         pass
            #     else:
            #         print(type(e))
            #         raise

    def send(self, topic, data):
        packet = YapPacket.encode(topic,data)
        self.client_socket.sendall(packet)
    
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

# List to keep track of connected clients
clients = []

# Function to handle client connections
def handle_client(client_socket, address):
    print(f"New connection: {address}")
    clients.append(client_socket)

    while True:
        try:
            # Receive messages from the client
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"Received from {address}: {message}")
                broadcast(message, client_socket)
            else:
                break
        except Exception as e:
            print(f"Error: {e}")
            break

    # Remove the client and close the connection
    clients.remove(client_socket)
    client_socket.close()
    print(f"Connection closed: {address}")

# Function to broadcast messages to all clients
def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message: {e}")

# Main server function
def start_server(host='127.0.0.1', port=12345):
    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.settimeout(None)
    server.listen()
    print(f"Server listening on {host}:{port}")

    while True:
        try:
            client_socket, address = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, address))
            thread.start()

        except TimeoutError:
            pass

def signal_handler(sig, frame):
    print('Signal received, exiting gracefully...')
    server.close()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    start_server()
