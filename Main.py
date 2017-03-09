#from _future_ import print_function
from subprocess import call
import Queue
import Pyro4
import time
import thread
import random
import sys

########################### Variable Definitions ###################################################

pigList = ['pigOne','pigTwo','pigThr','pigFou',
           'pigFiv','pigSix','pigSev','pigEig','pigNin']            #List of possible pigs

########################### Function Definitions ###################################################

#CreatePigs
def createPigs(x):
    if x== "B":
        call ("python birdCS.py")       #Start mainBird ServerClient
    else:   
        call ("python pig"+x+"CS.py")   #Start pig ServerClient
    
#Worker function to create threads to create pigs
def workerCreatePigs(x):
    return_value = thread.start_new_thread(createPigs,(x,))


#Function to send peer and selfcordinate data to pigs
def sendUpdateToPigs(temp,pigCS):
    for i in range(9):
        if (temp[0:6] == pigList[i]):
            pigCS[str(i+1)].pigUpdate(pigCordinates[str(i+1)],temp[6:len(temp)])
            return


#Function to send bird's landing data to nearest neighbour
def sendBirdData(nearestNeighbour,trajectory,hopcount):
    for i in range(9):
        for k,v in pigDict.iteritems():
            if(nearestNeighbour == k):
                cB = v.closestBird(trajectory,hopcount)
                return cB

########################### Game Initialization #####################################################
print "Game initializing..."

#Start main server and pigs
print "Starting peers..."
for x in 'B123':
    workerCreatePigs(x)

time.sleep(5)

#Place pigs at random cordinates
#Bird always launches from (4,4)

print "Placing pigs in random cordinate locations..."

cordinateSpace = ['34','43','24','33','42','14','23','32','41','04','13','22','31','40','03','12','21','30','02','11','20','01','10','00']
numSamples = 1

pigCordinates = dict([])

for i in "123456":                                                  #For loop to select a random cordinate
    tempCordinate = random.sample(cordinateSpace,numSamples)
    #Making sure 2 pigs are not allocated the same cordinates
    while (tempCordinate[0] in pigCordinates.values()):
        tempCordinate = random.sample(cordinateSpace,numSamples)
    pigCordinates[i] = (tempCordinate.pop())

print "The cordinate location of the pigs. "
print pigCordinates

#Send pig cordinates to MainServerClient
birdCS = Pyro4.Proxy('PYRONAME:birdMain.database')
birdCS.getCord(pigCordinates)

#Reading the peer information from the config file
   
with open('configFile.txt') as f:                                   #Read from config file
    newline = f.readlines()

newline =   [x.strip('\n') for x in newline]
numConnections = len(newline)

#Send self cordinates and peer information to pigs
print "Sending peer data to pigs..."

pOneCS= Pyro4.Proxy("PYRONAME:pigOne.database")
pTwoCS= Pyro4.Proxy("PYRONAME:pigTwo.database")
pThrCS= Pyro4.Proxy("PYRONAME:pigThr.database")
pFouCS= Pyro4.Proxy("PYRONAME:pigFou.database")
pFivCS= Pyro4.Proxy("PYRONAME:pigFiv.database")
pSixCS= Pyro4.Proxy("PYRONAME:pigSix.database")
pSevCS= Pyro4.Proxy("PYRONAME:pigSev.database")
pEigCS= Pyro4.Proxy("PYRONAME:pigEig.database")
pNinCS= Pyro4.Proxy("PYRONAME:pigNin.database")

pigDict = dict([('1',pOneCS),('2',pTwoCS),('3',pThrCS),
                ('4',pFouCS),('5',pFivCS),('6',pSixCS),
                ('7',pSevCS),('8',pEigCS),('9',pNinCS)])
 
for i in range(len(newline)):
    temp = newline[i]
    sendUpdateToPigs(temp,pigDict)                          #Call function to update pigs

print "End of initialization"

############################ End Initilalization #################################################

#User enters time delay
timeDelayin = raw_input('Enter the time delay for pig communication T in seconds (>3) : ')
if (int(timeDelayin) <= 3):
    timeDelay = raw_input('Time delay should be greater than 3. Please re-enter :')

#User enters speed
speedin = raw_input('Enter the speed of the bird in hopcounts/T : ')

#User enters trajectory
trajectory = raw_input('Enter the trajectory as 0<horizontal>1<vertical> : ')
trajectoryOK = False
n = 0
while((trajectoryOK == False)):
    if ((trajectory[0] != '0') or (trajectory[2] != '1')):
        trajectory = raw_input('Enter trajectory in format : ')
        n = n+1
        if (n==4):
            print "Please read instructions for entering trajectory in format"
            time.sleep(5)
            sys.exit()
    else:
        trajectoryOK = True

#User enters hopcount
hopcountin = raw_input('Enter the hopcount : ')

timeDelay = float(timeDelayin)
speed = float(speedin)
hopcount = int(hopcountin)

#Calculate landing position
col = str(4 -int(trajectory[1]))
row = str(4 - int(trajectory[3]))
landingCord = row+col

print "Landing Cordinates are : " , landingCord

#Calculate Time
TimeForOneHop = float(timeDelay/speed)
totalHops = float(trajectory[1])+float(trajectory[3])
landingTime = float(TimeForOneHop*totalHops)

print "Estimated time to land is : ", landingTime

#Find closest neighbour
nearestNeighbour = ""
found = False

for i in cordinateSpace:
    for j,val in pigCordinates.iteritems():
        if (pigCordinates[j] == i):
            nearestNeighbour = j
            found = True
            break
    if (found):  
        break
    
print "Nearest Neighbour has been found to be Pig",nearestNeighbour

#Check if pig is at landing cordinate

pigInLoc = False

if (landingCord in pigCordinates.values()):
    pigInLoc = True

#Write code to check for stone
##############################
    
# To Remove
nearestNeighbour = "1"

#Send Speed and Trajectory to neearest Neighbour
cB2 = sendBirdData(nearestNeighbour,trajectory,hopcount)

#Waiting for Bird to land on landing cordinate
time.sleep(landingTime)
print "Woke up from sleep"

#Check if pig is still in landing cordinate
if (pigInLoc):

    hitPigID = birdCS.checkCord(landingCord)
    if (hitPigID != '0'):
        hitPigID = '1'                  #to be removed                  
        pigName = pigDict[hitPigID]
        pigAffected = pigName.pigHit()
        print "Pig was hit by the Bird : " ,pigAffected
        
    else:
        print "No one was hit"

# Ask nearest neighbour to query pigs with statusAll
startStatusAll = pigDict[nearestNeighbour].callStatusAll()

    
#update score
