import sys
import requests
import mysql.connector as mariadb
import config
import logging
import datetime
from bs4 import BeautifulSoup

def checkNumber (number):
    try:
        result = int(number)
    except:
        result = null
    return result

def sendToDB (statement):
    mariadb_connection = mariadb.connect(user=config.user, password=config.password, database=config.database)
    cursor = mariadb_connection.cursor()
    result = 1    
    try:
        cursor.execute(statement)
    except Exception as e:
        result = e
    mariadb_connection.commit()
    mariadb_connection.close()
    return result

def translateDate(dateString):
    day = dateString[0:2]
    month = dateString[3:5]
    year = dateString[6:10]
    hour = dateString[11:13]
    minute = dateString[14:16]
    result = str(year)+'-'+str(month)+'-'+str(day)+' '+str(hour)+':'+str(minute)+':00'
    return(result)    

def translateStatus (statusString):
    result = 0
    if statusString == 'frei':
        result = 1
    elif statusString == 'besetzt':
        result = 2
    elif statusString == 'geschlossen':
        result = 3
    elif statusString == 'keine Angabe':
        result = 4
    return result

def main():    
    logging.basicConfig(level=logging.WARNING, filename='warning.log')    
    result = requests.get('https://www.stadt-muenster.de/tiefbauamt/parkleitsystem')
    if result.status_code != 200:
        print("Request failed with status code: {:d}!".format(result.status_code), file=sys.stderr)

    soup = BeautifulSoup(result.text, 'html.parser')
    parking_table = soup.find('div', id='parkingList')('table')
    date = soup.find('strong', id='lastRefresh').text.strip()
    date = translateDate(date)
    
    parking_list = None
    for table in parking_table:
        parking_list = table('tr')[1:]


    titles = []
    dbtitles = []
    scores = []
    stati = []
    for row in parking_list:
        title = row('td', class_='name')[0].text.strip()
        score = row('td', class_='freeCount')[0].text.strip()
        status = row('td', class_='status')[0].text.strip()
        
        dbtitle = title.replace(' ','_')
        
        dbtitles.append(dbtitle)
        titles.append(title)        
        scores.append(checkNumber(score))
        stati.append(translateStatus(status))
        
    tableColumnCount = ''
    tableColumnState = ''
    countValues = ''
    statusValues = ''
    for i in dbtitles:
        tableColumnCount = tableColumnCount+', '+i+'_count'
        tableColumnState = tableColumnState+', '+i+'_status'
    for i in scores:
        countValues = countValues + ', '+str(i)
    for i in stati:
        statusValues = statusValues + ', '+str(i)
    
    statement = 'INSERT INTO parkingStatsTable (Zeit'+ tableColumnCount+tableColumnState+') VALUES ("'+date+'"'+countValues+statusValues+');'
    success = 0
    if (statement):
        success = sendToDB(statement)
    
    if (success != 1):
        logging.warning(str(datetime.datetime.now())+' | '+str(success)+' | '+statement)

if __name__ == "__main__":
    main()
