import serial
import requests
import json
import time
from datetime import datetime, timedelta

# Gets JSON raw data from the API
# ==============
def fetchDataFromApi(url):
    response = requests.get(url)
    pageJson = json.dumps(response.json(), sort_keys=True, indent=4)
    return pageJson

# Exports the JSON raw data to a .json file
# ==============
def createJsonFile(data, filePath):
    with open(filePath, "w") as outFile:
        outFile.write(data)
    
# Converts the JSON raw data to a Python dictionary
# ==============
def readJsonFile(filePath):
    with open(filePath, 'r') as jsonFile:
        jsonData = json.load(jsonFile)
    return jsonData

# Adapts the time to correct timezone
# ==============
def formatTime(hourMinute):
    timeObj = datetime.strptime(hourMinute, "%H:%M")
    timeObj += timedelta(hours=1)
    formattedTime = timeObj.strftime("%H:%M")
    return formattedTime

# Formats the data and creates two arrays, one for destinations and one for departure times
# ==============
def createTableau(jsonData):
    tableauSens = []
    tableauHeure = []

    for i in range(jsonData['nhits']):
        sensLigne = jsonData["records"][i]["fields"]["sensligne"]
        heureDepart = jsonData["records"][i]["fields"]["heureestimeedepart"][11:16]
        heureFormattee = formatTime(heureDepart)
        tableauSens.append("<" + sensLigne + ">")
        tableauHeure.append("<" + heureFormattee + ">")
    
    return tableauSens, tableauHeure

# Exports the formatted data to a .txt file
# ==============
def exportDataToText(dataSens, dataHeure, filePath, header):
    with open(filePath,'w') as file:
        file.write(header)
        for i in range(len(dataSens)):
            if (dataSens[i] != dataSens[i-1]):
                file.write('\n')
                file.write(dataSens[i])
            file.write(dataHeure[i])

# Sends a string to Arduino board via Serial 
# ==============
def sendToArduino(ser, sendStr):
    ser.write(sendStr.encode('utf-8'))


# Receives a string from Arduino via Serial
# ==============
def getFromArduino(ser, startMarker, endMarker):
    ck = ""
    x = "Z" # any value that is not an end- or startMarker
    byteCount = -1
    
    while  ord(x) != startMarker: 
        x = ser.read()
    
    while ord(x) != endMarker:
        if ord(x) != startMarker:
            ck = ck + x.decode()
            byteCount += 1
        x = ser.read()
    
    return ck

#  Allows time for Arduino reset, also ensures that any bytes left over from a previous message are discarded
# ==============
def waitForArduino(ser, startMarker, endMarker):
    msg = ""
    while msg.find("Arduino is ready") == -1:
        while ser.inWaiting() == 0:
            pass
        msg = getFromArduino(ser, startMarker, endMarker)
        print(msg)
        print()

# Tests communication with Arduino
# ==============
def runTest(ser, data, startMarker, endMarker):
    numLoops = len(data)
    waitingForReply = False

    n = 0
    while n < numLoops:
        teststr = data[n]

        if waitingForReply == False:
            sendToArduino(ser, teststr)
            print ("Sent from PC -- LOOP NUM " + str(n) + " TEST STR " + teststr)
            waitingForReply = True

        if waitingForReply == True:

            while ser.inWaiting() == 0:
                pass
            
            dataRecvd = getFromArduino(ser, startMarker, endMarker)
            print ("Reply Received  " + dataRecvd)
            n += 1
            waitingForReply = False

            print ("===========")

        time.sleep(0.1)

# MAIN
# ==============
def main():
    # v This can be adapted to any station and for bus / metro easily
    nomStation = "EUROTELEPORT"
    ligne = "TRAM"
    url = "https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=ilevia-prochainspassages&q=&rows=50&facet=identifiantstation&facet=nomstation&facet=codeligne&facet=sensligne&refine.codeligne="+ligne+"&refine.nomstation="+nomStation
    jsonFilePath = "./python/data/timetable.json"
    textFilePath = "./python/data/timetable.txt"
    
    pageJson = fetchDataFromApi(url)
    createJsonFile(pageJson, jsonFilePath)
    
    jsonData = readJsonFile(jsonFilePath)
    tableauSens, tableauHeure = createTableau(jsonData)
    
    header = "Direction, Prochain, Prochain+1, Prochain+2"
    exportDataToText(tableauSens, tableauHeure, textFilePath, header)

    print(tableauSens)
    print(tableauHeure)
    
    serPort = "COM5"
    baudRate = 9600
    startMarker = 60    # '<'
    endMarker = 62      # '>'
    endSignal = []
    endSignal.append("<END>")
    
    ser = serial.Serial(serPort, baudRate)
    print("Serial port " + serPort + " opened  Baudrate " + str(baudRate))
    
    waitForArduino(ser, startMarker, endMarker)
    
    runTest(ser, tableauSens, startMarker, endMarker)
    runTest(ser, tableauHeure, startMarker, endMarker)
    runTest(ser, endSignal, startMarker, endMarker)
    
    ser.close()
    

if __name__ == "__main__":
    main()