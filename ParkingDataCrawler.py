import sys
import requests
from bs4 import BeautifulSoup

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
    # connect with website
    result = requests.get('https://www.stadt-muenster.de/tiefbauamt/parkleitsystem')
    if result.status_code != 200:
        print("Request failed with status code: {:d}!".format(result.status_code), file=sys.stderr)

    # get parking table
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
        scores.append(int(score))
        stati.append(translateStatus(status))
        
    print(date)
    print(dbtitles)
    print(scores)
    print(stati)


if __name__ == "__main__":
    main()
