#This script is the core of the app. It performs the following tasks
#1. Find all launchable apps
#2. Collect info about each app in step1 according to date
#3. Average and accumulate data for all apps 
#4. Based on certain specific values for my phone,I can make a prediction of time left.


import android,commands,os,sys,time
from collections import defaultdict
droid = android.Android()

keyDict=[]

def mkdir():
    directory1 = commands.getstatusoutput('mkdir -p  /sdcard/daily_logs')
    #directory2 = commands.getstatusoutput('mkdir -p  /sdcard/usefulData')
    #droid.makeToast(directory1[1]+"\n daily_logs")
    #time.sleep(1)
    #droid.makeToast(directory2[1]+"\n Useful Data")
    #time.sleep(2)
   

def getLaunchableApps():
    listofApps = droid.getLaunchableApplications().result
    #print listofApps
    f = open('List.txt','w')
    f.write(str(listofApps))
    f.close()
    


def getUsageStats() :
    droid.makeToast('Generating logs ...')
    dumpsys = commands.getstatusoutput('dumpsys usagestats > usagestats.txt')
    
#Opens each day's file ,accumulates each apps data over different days and find average usage 
def fileHash():
    filepath = '/sdcard/daily_logs'
    Apps = defaultdict(dict)
    #Each app has following details :
    # total time [totalTime]
    # wifi locks [wifiLocks]
    # cpu locks [cpuLocks]
    # average usage per day [averageUsage]
    # starts
    totalTime = "totalTime"
    wifiLocks = "wifiLocks"
    cpuLocks = "cpuLocks"
    averageUsage = "averageUsage"
    starts = "starts"


    contents = commands.getstatusoutput("ls %s"%filepath)
    files = contents[1].split()
    #print files

    days = len(files)
    #print "Days are ",days
    if(days <= 0):
        droid.makeToast("No Data Available")
 	time.sleep(1)
        sys.exit()
	
    pos = 0

    for filename in files :
        #print filename
        absPath = str(os.path.join(filepath,filename))
        #print "Abs Path ",absPath
        fileReader = open(absPath,'r')
        for line in fileReader:
      	    if(len(line) > 1) :
      	        lineWords = line.strip().split(',')
      	        #print lineWords
      	    if lineWords[3] in Apps :	
	        #print "Testing this ",lineWords
		Apps[ lineWords[3] ][totalTime] = Apps[ lineWords[3] ][totalTime] + int ( lineWords[2])
		Apps[ lineWords[3] ][starts] = Apps[ lineWords[3] ][starts] + int ( lineWords[1])
		Apps[ lineWords[3] ][averageUsage] = int(Apps[ lineWords[3] ][totalTime])/days
        	#print "pass",Apps
      
      	    if lineWords[3] not in Apps :
        	Apps[ lineWords[3] ] = {}
        	Apps[ lineWords[3] ][totalTime] = 0
        	Apps[ lineWords[3] ][wifiLocks] = False
        	Apps[ lineWords[3] ][cpuLocks] = False
        	Apps[ lineWords[3] ][averageUsage] = 0
		Apps[ lineWords[3] ][ starts ] = 0
      
		#print "Testing this ",lineWords
		Apps[ lineWords[3] ][starts] = Apps[ lineWords[3] ][starts] + int ( lineWords[1])
		Apps[ lineWords[3] ][totalTime] = Apps[ lineWords[3] ][totalTime] + int ( lineWords[2])
		Apps[ lineWords[3] ][averageUsage] = int(Apps[ lineWords[3] ][totalTime])/days

        fileReader.close()
    os.system('touch /sdcard/HashtoString.txt')
    fileSaver = open('/sdcard/HashtoString.txt','w')
    fileSaver.write("Apps    Total    Avg    Starts")
    fileSaver.write(os.linesep)
    for app in Apps :
        
        fileSaver.write(app.ljust(0))
  	fileSaver.write("  ")
  	fileSaver.write(str(int(Apps[app][totalTime]/60000)).rjust(7))
	#fileSaver.write(str("min") )       
	fileSaver.write("  ")
        fileSaver.write(str(int(Apps[app][averageUsage]/60000)).rjust(4))
        #fileSaver.write(str("min") )
        fileSaver.write("  ")
        fileSaver.write(str(int(Apps[app][starts])).rjust(1))
        fileSaver.write(os.linesep)
    fileSaver.close()
    #os.system('cat HashtoString.txt')

#This parses the List.txt and gets all launchable apps
def RunnableApps(keyDict, keyfilename):
    #fixme
    keyfilename = "List.txt"

    if (os.path.exists(keyfilename)==False):
        print "Wrong key filename, please enter a complete path to your key file."
        
    keyFile = open(keyfilename, 'r')

    #parse KeyName file, create array    
    temp = ((keyFile.readline()).strip()[1:-1]).split(',')

    for i in range(0, len(temp)):
        keyDict.append(temp[i].split(':'))
        keyDict[i].remove(keyDict[i][1])
        k=keyDict[i][0].index('u')
        keyDict[i][0]=keyDict[i][0][k+2:-1]
        #keyDict[i][1]=keyDict[i][1][k+2:-1]

        keyFile.close()

    for key in keyDict:
        tempr=""
        for k in key[0]:
            tempr = tempr + k.lower()
        key.append(tempr)
        key.append("".join(key[1].split()))
        
    return keyDict

#main parser
#This function compares apps in list or launchable apps with the apps from usage stats
#Accumulates each day's usage as a new text file,which is used in HashToString.txt
def parser_main(keyDict, cDate):

    
    keyDict = RunnableApps(keyDict, "List.txt")
    
    #variables
    string0="Date:" 
    cDate=0
    flag=0
    outputfilename=""
    #fixme
    logfilename = "usagestats.txt"    
    
    if (os.path.exists(logfilename)==False):
        droid.makeToast("Wrong log filename, please enter a complete path to your log file")

    logFile = open(logfilename, 'r')

    for line in logFile:

        flag=0    
    
        if (line.find(string0, 0) >=0 and cDate<int(line.split()[1])):
            cDate= int(line.split()[1])
            outputfilename ="/sdcard/daily_logs/"+"logs" + str(cDate) +".txt"
            outputFile =open(outputfilename, 'w')
    
        if (line[0]==' ' and line[1]== ' ' and line[2]!=' '):
            line= line.strip()
            temp0=line.split()

            for key in keyDict:
                for word in key:
                    if (line.find(word,0)>=0):
                        outputFile.write(temp0[0][0:-1]+','+temp0[1]+','+temp0[3]+','+key[0]+'\n')
                        flag=1
                        break
            if(flag==0):
                outputFile.write(temp0[0][0:-1]+','+temp0[1]+','+temp0[3]+','+'System'+'\n')
            
    outputFile.close()

#Prediction based on data from my phone,not a generalized value.
#Fix me later
def Prediction():
    droid.batteryStartMonitoring()
    time.sleep(2)
    Level =  int(str(droid.batteryGetLevel().result))
    wifiOn = None
    WifiEffect = None
    wDR = wMin = wHR = None
    btEffect = None
    bDR = bMin = bHR = None
    wifiOn = droid.checkWifiState().result
    #droid.makeToast(str(wifiOn))
    btOn = None
    btOn = droid.checkBluetoothState().result
    #droid.makeToast(str(btOn))
    DepletionRate = 0.12
    if(wifiOn == True) :
        tDR = DepletionRate
        tMin = int(Level/tDR)
        tHR = int(tMin/60)
        tMin = int(tMin%tHR)
 	WifiEffect = "If you turn OFF Wifi :\n"+str(tHR)+" Hrs "+str(tMin)+" min\n"
        #droid.makeToast(WifiEffect)
        time.sleep(1)
        DepletionRate = DepletionRate + 0.07 
 	droid.makeToast("Wifi On")
        time.sleep(1) 
    else :
	tDR = DepletionRate + 0.07
        tMin = int(Level/tDR)
        tHR = int(tMin/60)
        tMin = int(tMin%tHR)
 	WifiEffect = "If you turn ON Wifi :\n"+str(tHR)+" Hrs "+str(tMin)+" min\n"
        #droid.makeToast(WifiEffect)
        #time.sleep(1) 
    
    if(btOn == True) :
        bDR = DepletionRate
        bMin = int(Level/bDR)
        bHR = int(bMin/60)
        bMin = int(bMin%bHR)
 	btEffect = "If you turn OFF Bluetooth :\n"+str(bHR)+" Hrs "+str(bMin)+" min\n"
        #droid.makeToast(btEffect)
        #time.sleep(1)
        DepletionRate = DepletionRate + 0.03
	droid.makeToast("BT On")
        time.sleep(1)
    else:
	bDR = DepletionRate + 0.03
        bMin = int(Level/bDR)
        bHR = int(bMin/60)
        bMin = int(bMin%bHR)
	btEffect = "If you turn ON Bluetooth :\n"+str(bHR)+" Hrs "+str(bMin)+" min\n"
        #droid.makeToast(btEffect)
        #time.sleep(1)

    Minutes = int(Level/DepletionRate)
    Hours = int(Minutes/60)
    Minutes = int(Minutes%60)
    droid.batteryStopMonitoring()
    final1 = str(Hours)+" Hours "+str(Minutes)+" Minutes Left\n"
    final2  = btEffect+"\n"+WifiEffect
    #droid.makeToast(final1+"\n"+str(final2))
    time.sleep(1)
    droid.dialogCreateAlert(final1,final2)
    droid.dialogSetNeutralButtonText("OK")
    #droid.dialogSetNegativeButtonText("Exit")
    droid.dialogShow()
    droid.batteryStopMonitoring()




mkdir()
getLaunchableApps()
getUsageStats()
parser_main(keyDict, 0)
fileHash()
output = commands.getstatusoutput("cat /sdcard/HashtoString.txt")
#droid.makeToast(output[1])
#time.sleep(2)
#dispData = str("App\tTotal Min\tAvg Min\n"+output[1])

#droid.dialogGetInput("Usage",output[1])
#droid.dialogSetNegativeButtonText("Exit");
#droid.dialogSetPositiveButtonText("Predict Time Left");
#droid.dialogShow()
droid.dialogCreateAlert("Usage",output[1])
droid.dialogSetNegativeButtonText("Exit");
droid.dialogSetPositiveButtonText("Predict Time Left");
droid.dialogShow()
response=droid.dialogGetResponse().result
droid.dialogDismiss()


if response.has_key("which"):
    result=response["which"]
time.sleep(1)
if result=="positive":
    Prediction()
elif result=="negative":
    sys.exit()
