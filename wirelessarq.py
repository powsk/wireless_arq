#CS 597 Wireless and Mobile Systems
#Alex Kopowski and Aaron Hoffman
#03/10/10

import threading
import datetime
import random

packets = {'sending':[],'acknowledging':[],'fail':[],'complete':[]}
timeout = 5000
curID = 0

class packet():
    data = {}
    def __setitem__(self,key,item):self.data[key] = item
    def __getitem__(self, key): return self.data[key]

    def __init__(self,id=None):
        global curID
        if id is None:
            curID += 1
            self["id"] = curID
        else:
            self["id"] = id
        self["fail"] = bool(0)
        c = datetime.datetime.now()
        self["birth_time"] = c.minute * 60000 + c.second * 1000 + c.microsecond / 1000
        global timeout
        tempRand = random.randrange(timeout*0.75,timeout*1.1)
        self["data_length"] = tempRand/2
        tempRand = random.randrange(timeout*0.75,timeout*1.1)
        self["ack_length"] = tempRand/2

    def CheckFail(self):
        if self['fail']:
            return bool(1)
        
        tempNow = datetime.datetime.now()
        tempMS = tempNow.minute * 60000 + tempNow.second * 1000 + tempNow.microsecond / 1000
        packetBirth = self['birth_time']
        global timeout
        if tempMS - packetBirth >= timeout:
            self['fail'] = bool(1)
            return bool(1)
        else:
            return bool(0)

    def CheckSend(self):
        tempNow = datetime.datetime.now()
        tempMS = tempNow.minute * 60000 + tempNow.second * 1000 + tempNow.microsecond / 1000
        dataLength = self["data_length"]
        packetBirth = self['birth_time']
        if dataLength <= tempMS - packetBirth:
            return bool(1)
        else:
            return bool(0)

    def CheckAck(self):
        tempNow = datetime.datetime.now()
        tempMS = tempNow.minute * 60000 + tempNow.second * 1000 + tempNow.microsecond / 1000
        dataLength = self["data_length"]
        packetBirth = self['birth_time']
        ackLength = self["ack_length"]
        if ackLength + dataLength <= tempMS - packetBirth:
            return bool(1)
        else:
            return bool(0)

class packet_thread(threading.Thread):
    def __init__ ( self ):
        threading.Thread.__init__ ( self )

    def run (self):
        """go go go"""
        global packets
        var = 1
        while var == 1 :  # This constructs an infinite loop
            tempList = packets['sending']
            if len(tempList) <= 0:
                tempList = packets['acknowledging']
                if len(tempList) <= 0:
                    tempList = packets['fail']
                    if len(tempList) <= 0:
                        tempPacket = packet()
                        tempList = packets['sending']
                        tempList.append(tempPacket)
                        print 'Create and send packet:' + str(tempPacket['id'])
            tempList = packets['sending']
            if len(tempList) > 0:
                for i in range(0,len(tempList)):
                    tempPacket = tempList[i]
                    if tempPacket.CheckFail():
                        #move to fail list
                        tempList.remove(tempPacket)
                        tempList = packets['fail']
                        tempList.append(tempPacket)
                        print 'Failed packet:' + str(tempPacket['id'])
                    else:
                        if tempPacket.CheckSend():
                            #move to ack list
                            tempList.remove(tempPacket)
                            tempList = packets['acknowledging']
                            tempList.append(tempPacket)
                            print 'Ack sent for packet:' + str(tempPacket['id'])

            tempList = packets['acknowledging']
            if len(tempList) > 0:
                #move to complete list
                for i in range(0,len(tempList)):
                    tempPacket = tempList[i]
                    if tempPacket.CheckFail():
                        #move to fail list
                        tempList.remove(tempPacket)
                        tempList = packets['fail']
                        tempList.append(tempPacket)
                        print 'Failed packet:' + str(tempPacket['id'])
                    else:
                        if tempPacket.CheckAck():
                            #move to ack list
                            tempList.remove(tempPacket)
                            tempList = packets['complete']
                            tempList.append(tempPacket)
                            print 'Ack received packet:' + str(tempPacket['id'])

            tempList = packets['fail']
            if len(tempList) > 0:
                for i in range(0,len(tempList)):
                    tempPacket = tempList[i]
                    tempID = tempPacket['id']
                    newPacket = packet(tempID)
                    tempList.remove(tempPacket)
                    tempList = packets['sending']
                    tempList.append(newPacket)
                    print 'Resending failed packet:' + str(tempPacket['id'])

## Main program code ##
if __name__ == "__main__":
    packet_thread().start()
    
