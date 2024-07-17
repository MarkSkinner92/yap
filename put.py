import yap
import time
import random

yapper = yap.Yapper()
i=0
while True:
    try:
        print("sending a random value")
        yapper.send("randomNumber",["some super long",i,i,i,i,i,i,i,i])
        yapper.send("otherstuff",{"other":2})
        i += 1

        time.sleep(0)

    except KeyboardInterrupt:
        break

print("stopping")
yapper.shutup()