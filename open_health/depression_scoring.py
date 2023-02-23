import requests
import json
def get_depression_scoring(userId):
    # try:
    Api = 'http://localhost:8000/OpenHealthBot/OpenHealthAssessmentByUserId/{}/'.format(userId)
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer <replace with your token>'}
    response = requests.get(url=Api, headers=headers)
    data = response.json()['Result']
    # print(data)
    concatination = ''
    try:
        a = data['Risk to Depression']
        # a1 = data['Risk to Depression'][1:45]
        b = " ".join(map(str, a))
        # b1 = " ".join(map(str, a1))
        # print(concatination[9:])
        concatination += b
        return concatination[9:]
    except:
        a = 'No'
        concatination += a
        print(concatination)
    return concatination
# print(get_depression_scoring(17))