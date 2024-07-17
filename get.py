import yap
import time
import random

yapper = yap.Yapper()

while True:
    try:
        messages = yapper.getMessages("randomNumber")
        for message in messages:
            print("random",message)
        
    except KeyboardInterrupt:
        break

print("stopping")
yapper.shutup()