import android,commands,os,sys,time
from collections import defaultdict
droid = android.Android()

keyDict=[]

def mkdir():
    directory = commands.getstatusoutput('mkdir -p  /sdcard/daily_logs')

def getLaunchableApps():
    listofApps = droid.getLaunchableApplications().result
    #print listofApps
    f = open('List.txt','w')
    f.write(str(listofApps))
    f.close()
    


def getUsageStats() :
    dumpsys = commands.getstatusoutput('dumpsys usagestats > usagestats.txt')
    #droid.makeToast('Generating logs ...)

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
        #droid.makeToast("\n--\n--\nNo Data Available\n--\n--\n--")
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

    fileSaver = open('HashtoString.txt','w')
    for app in Apps :
        fileSaver.write(app)
  	fileSaver.write(",")
  	fileSaver.write(str(Apps[app][totalTime]))
        fileSaver.write(",")
        fileSaver.write(str(Apps[app][averageUsage]))
        fileSaver.write(",")
        fileSaver.write(str(Apps[app][starts]))
        fileSaver.write(os.linesep)
    fileSaver.close()
    #os.system('cat HashtoString.txt')


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
        print "Wrong log filename, please enter a complete path to your log file."

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




mkdir()
getLaunchableApps()
getUsageStats()
parser_main(keyDict, 0)
fileHash()
output = commands.getstatusoutput("cat HashtoString.txt")
droid.makeToast(output[1])
time.sleep(5)
droid.dialogGetInput("Usage",output[1])
#droid.dialogSetPositiveButtonText("Ok")
droid.dialogShow()
