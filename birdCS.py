#from _future_ import print_function
from subprocess import call
import Queue
import Pyro4
import time
import thread

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")

class MainBird(object):
    
    #Cordinates of the pigs
    cordinates = dict([])
    return_cordinate = dict([])
    cordinateSpace = ['34','43','24','33','42','14','23','32','41','04','13','22','31','40','03','12','21','30','02','11','20','01','10','00']

    #Function to get new cordinate location for pigs in bird landing location
    def workergetCordinates(self,pigID):
        print self.cordinates
        for k,v in self.cordinates.iteritems():
            if (k == pigID):
                #check if new cordinate is already occupied and also if it is a value in possible cordinate space
                if ((~(str(int(v)-1) in self.cordinates.values()))and (str(int(v)-1) in self.cordinateSpace)):
                    self.return_cordinate[k] = str(int(v)-1)
                    self.cordinates[k] = str(int(v)-1)
                    return
                elif((~(str(int(v)+1) in self.cordinates.values())) and (str(int(v)+1) in self.cordinateSpace)):
                    self.return_cordinate[k] = str(int(v)+1)
                    self.cordinates[k] = str(int(v)+1)
                    return
                elif((~(str(int(v)+10) in self.cordinates.values())) and (str(int(v)+10) in self.cordinateSpace)):
                    self.return_cordinate[k] = str(int(v)+10)
                    self.cordinates[k] = str(int(v)+10)
                    return
                elif((~(str(int(v)-10) in self.cordinates.values())) and (str(int(v)-10) in self.cordinateSpace)):
                    self.return_cordinate[k] = str(int(v)-10)
                    self.cordinates[k] = str(int(v)-10)
                else:    
                    self.return_cordinate[k] = 'No'
                    return
    #GetCordinates
    def getCordinate(self,pigID):
        value = thread.start_new_thread(self.workergetCordinates,(pigID,))
        time.sleep(2)
        if (len(self.return_cordinate[pigID]) == 1):
             self.return_cordinate[pigID]= '0'+self.return_cordinate[pigID]
             return self.return_cordinate[pigID]
        else:
            return  self.return_cordinate[pigID]

    #Function to receive cordinates from Main
    def getCord(self,pigCordinates):
        self.cordinates = pigCordinates
        print self.cordinates

    #Function to check if there is a pig in landing cordinate
    def checkCord(self,landingCord):
        if landingCord in self.cordinates.values():
            for k,v in self.cordinates.iteritems():
                if(landingCord == v):
                    return k
        #write code to check for stone
        else:
            return '0'                              #Return 0 if no pig is in landing cordinate

    #Function to revert cordinate updation in case pig was hit before it saved itself.
    def revertCordinate(self,oldC,newC):
        if (newC in self.cordinates.values()):
            for k,v in self.cordinates.iteritems():
                if (v == newC):
                    v =oldC
                    return v
        else:
            print "Error : Cannot revert cordinates"

    #Function to get physical neighbours (checks :is pig present to the right of attacked pig?)
    def getCordinateNeighbours(self,cord):
        #self.cordinates['2'] = '12'
        cordNum = str(int(cord)+1)                   
        if cordNum in self.cordinates.values():
            for k,v in self.cordinates.iteritems():
                if(v== cordNum):
                    return k
        else:
            return '0'                              #Return 0 if no neighbour

#Program starts

# Start MainBird Server
Pyro4.Daemon.serveSimple(
    {
        MainBird: "birdMain.database"
    },
    ns=True,)
