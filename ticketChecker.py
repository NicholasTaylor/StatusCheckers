#!/Users/nicholas/py-sandbox/statusChecks/env/bin/python3.7

def sendNotification(msg):
	import requests, json
	discordRaw = ''
	with open('discord.json','r') as discordFile:
		for line in discordFile:
			discordRaw += line
	discord = json.loads(discordRaw)
	url = discord['url']
	headers = {'Content-Type':'application/x-www-form-urlencoded'}
	data = {'content':msg}
	r = requests.post(url, data=data, headers=headers)

def getJson(url,bearerToken):
	import requests
	r = requests.get(url,headers={'Authorization': 'Bearer ' +bearerToken})
	jsonRaw = r.json()
	ticketClasses = jsonRaw['ticket_classes']
	ticketZero = ticketClasses[0]
	currentStatus = ticketZero['on_sale_status']
	maximumQuantity = ticketZero['maximum_quantity']
	maximumQuantityOrder = ticketZero['maximum_quantity_per_order']
	quantityList = {'maximumQuantity':maximumQuantity,'maximumQuantityOrder':maximumQuantityOrder}
	return {'status':currentStatus,'maxQuantity':quantityList}

def fileUpload(fileName):
	import ftplib, os, json
	from ftplib import FTP
	fileCredentials = 'ftp.json'
	fileUpload = fileName
	with open(fileCredentials,'r') as fileOpenCredentials:
		fileContents = fileOpenCredentials.read()
		credentialsJson = json.loads(fileContents)
		username = credentialsJson['username']
		password = credentialsJson['password']
		server_addr = credentialsJson['server']
		outputDir = credentialsJson['path']
	ftp = FTP(server_addr)
	ftp.login(username,password)
	ftp.cwd(outputDir)
	fileUploadObject = open(fileUpload,'rb')
	ftp.storbinary('STOR ' +fileUpload, fileUploadObject)
	ftp.quit()
	fileUploadObject.close()

def checkEventStatus(eventId):
	import datetime,csv,os,json
	authRaw = ''
	with open('eventBrite.json', 'r') as authFile:
		for line in authFile:
			authRaw += line
	authJson = json.loads(authRaw)
	auth = authJson['key']
	statusDict = getJson('https://www.eventbriteapi.com/v3/events/' +str(eventId) +'/ticket_classes/',auth)
	currentQuantity = statusDict['maxQuantity']
	if statusDict['status'].lower() != 'available':
		sendNotification('Oh no! :( Tickets unavailable! Check the EventBrite page for more details!')
	elif any(currentQuantity[i] < 6 for i in currentQuantity):
		flagCorrectField = False
		correctField = None
		for i in currentQuantity:
			if currentQuantity[i] < 6 and flagCorrectField == False:
				correctField = currentQuantity[i]
				fieldIter = i
				flagCorrectField = True
		sendNotification('Hurry! ' +str(correctField) +' tickets remain! Get yours before they are gone!')
	currentDateTimeRaw = datetime.datetime.now()
	currentDate = currentDateTimeRaw.strftime('%Y%m%d')
	currentDateTime = currentDateTimeRaw.strftime('%Y-%m-%d %H:%M:%S')
	fields = ['datetime','status','maximum_quantity','maximum_quantity_per_order']
	logFileName = 'ticketChecker-' +currentDate +'.csv'
	fileExists = os.path.isfile(logFileName)
	with open(logFileName, 'a') as logFile:
		writer = csv.DictWriter(logFile, fieldnames=fields)
		if not fileExists:
			writer.writeheader()
		writer.writerow({'datetime':currentDateTime,'status':statusDict['status'],'maximum_quantity':currentQuantity['maximumQuantity'],'maximum_quantity_per_order':currentQuantity['maximumQuantityOrder']})
	fileUpload(logFileName)

eventID = 00000000000
#Replace the zeros above with the EventBrite Event ID of your choice
checkEventStatus(eventID)