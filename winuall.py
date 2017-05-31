import json, requests

def send(query):

    url = "https://winuall.com/winuallapi/public/api/search_messenger?q="+query

    data = requests.get(url)

    proper = json.loads(data.text)
    
    solved = []
    for i in proper['result']:
        if i['solved'] == 1:
            solved.append(i)

    return solved
