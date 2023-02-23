import requests
import json
def get_lifestyle_scoring(userId):
    Api = 'http://localhost:8000/OpenHealthBot/OpenHealthAssessmentByUserId/{}/'.format(userId)
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer <replace with your token>'}
    response = requests.get(url=Api, headers=headers)
    data = response.json()['Result']
    # print(data)
    concatination = ''
    try:
        a = data['Life Style Scoring']['Overall_Lifestyle'][:1]
        a1 = data['Life Style Scoring']['Overall_Lifestyle'][1:2]
        b = " ".join(map(str, a))
        b1 = " ".join(map(str, a1))
        concatination += b + " **|** " + b1
        print(concatination)
    except:
        a = 'No'
        concatination += a
        print(concatination)
    return concatination
