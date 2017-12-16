import DSClient


animation = ["[255,0,0]","[0,255,0]","[0,0,255]","[255,255,0]","[255,0,255]","[255,255,255]","[0,0,0]"]
DSClient.sendGateUpdate("192.168.1.110",13246,animation)
