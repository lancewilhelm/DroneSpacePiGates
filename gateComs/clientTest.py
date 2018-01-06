import DSClient
import time
t = .2
while(True):
    DSClient.sendSpecificGateUpdate('192.168.1.124',58789,"red")
    time.sleep(t)
    DSClient.sendSpecificGateUpdate('192.168.1.124',58789,"blue")
    time.sleep(t)
    DSClient.sendSpecificGateUpdate('192.168.1.124',58789,"green")
    time.sleep(t)
    DSClient.sendSpecificGateUpdate('192.168.1.124',58789,"yellow")
    time.sleep(t)
