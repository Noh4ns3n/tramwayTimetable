import serial
import time
import requests
import json
from datetime import datetime, timedelta

# récupère les datas de l'API à l'URL demandée
url = 'https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=ilevia-prochainspassages&q=&rows=50&facet=identifiantstation&facet=nomstation&facet=codeligne&facet=sensligne&refine.nomstation=BOTANIQUE'
page = requests.get(url)
page_json = json.dumps(page.json(), sort_keys=True, indent=4)

# crée un fichier json à partir des infos 
with open("c:/users/20100/Dev/Python/horairesTramway/horairesBotanique.json", "w") as outfile:
    outfile.write(page_json)

# lis les données à partir du fichier json
with open('c:/users/20100/Dev/Python/horairesTramway/horairesBotanique.json', 'r') as json_file:
	json_load = json.load(json_file)

# stocke le nombre de hits dans une variable
numberHits = json_load['nhits']

# pour chaque hit, stocke les keys d'intérêt (sensLigne et heureDepart) dans une case d'un tableau (un par key)
# formatte l'heure pour ajuster au bon fuseau horaire (+2h)
tableauSens=[]
tableauHeure=[]
for i in range(numberHits):
    sensLigne = json_load["records"][i]["fields"]["sensligne"]
    heureDepart = json_load["records"][i]["fields"]["heureestimeedepart"][11:16]    # récupère uniquement l'heure
    heureDepartFormattee = datetime.strptime(heureDepart, "%H:%M")                  # convertis l'heure en string en objet datetime
    heureDepartFormattee += timedelta(hours=2)                                      # ajoute 2h 
    heureDepartFormattee = heureDepartFormattee.strftime("%H:%M")                   # reconvertis l'objet datetime en string
    tableauSens.append("<"+sensLigne+">")
    tableauHeure.append("<"+heureDepartFormattee+">")
tableauSens.append("<g>")

# exporte les valeurs inscrites dans les tableaux dans un fichier texte avec en_tete
# écris la direction en début de ligne
# puis les horaires des prochains passages vers cette direction à la suite sur la même ligne
en_tete="Direction, Prochain, Prochain+1, Prochain+2"
with open('c:/users/20100/Dev/Python/horairesTramway/horairesBotanique.txt', 'w') as file:
   file.write(en_tete)
   file.write('\n')
   for i in range(numberHits):
        if(i != 0) and (tableauSens[i] != tableauSens[i-1]):
            file.write('\n')
        if(i == 0) or (tableauSens[i] != tableauSens[i-1]):
            file.write(tableauSens[i])
        file.write(tableauHeure[i])
           

def sendToArduino(sendStr):
    ser.write(sendStr.encode('utf-8'))

def recvFromArduino():
    global startMarker, endMarker
    
    ck = ""
    x = "z" # any value that is not an end- or startMarker
    byteCount = -1 # to allow for the fact that the last increment will be one too many
    
    # wait for the start character
    while  ord(x) != startMarker: 
        x = ser.read()
    
    # save data until the end marker is found
    while ord(x) != endMarker:
        if ord(x) != startMarker:
            ck = ck + x.decode("utf-8") # change for Python3
            byteCount += 1
        x = ser.read()
    
    return(ck)

def waitForArduino():

    # wait until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
    # it also ensures that any bytes left over from a previous message are discarded
    
    global startMarker, endMarker
    
    msg = ""
    while msg.find("Arduino is ready") == -1:

        while ser.inWaiting() == 0:
            pass
        
        msg = recvFromArduino()

        print (msg) 
        print ()

def runTest(td):
    numLoops = len(td)
    waitingForReply = False

    n = 0
    while n < numLoops:
        teststr = td[n]

        if waitingForReply == False:
            sendToArduino(teststr)
            print ("Sent from PC -- LOOP NUM " + str(n) + " TEST STR " + teststr)
            waitingForReply = True

        if waitingForReply == True:

            while ser.inWaiting() == 0:
                pass
            
            dataRecvd = recvFromArduino()
            print ("Reply Received  " + dataRecvd)
            n += 1
            waitingForReply = False

            print ("===========")

        time.sleep(1)

# =============================================

print ()
print ()

# NOTE the user must ensure that the serial port and baudrate are correct

serPort = "COM5"
baudRate = 9600
ser = serial.Serial(serPort, baudRate)
print ("Serial port " + serPort + " opened  Baudrate " + str(baudRate))


startMarker = 60
endMarker = 62


waitForArduino()
runTest(tableauSens)

ser.close