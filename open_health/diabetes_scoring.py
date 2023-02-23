import requests
import json


def get_diabetes_scoring(userId):
    # try:
    Api = 'http://localhost:8000/OpenHealthBot/OpenHealthAssessmentByUserId/{}/'.format(userId)
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    response = requests.get(url=Api, headers=headers)
    data = response.json()['Result']
    # print(data)
    concatination = ''
    try:
        a = data['Risk to Diabities']
        # a1 = data['Risk to Diabetes'][1:45]
        b = " ".join(map(str, a))
        # b1 = " ".join(map(str, a1))
        concatination += b
        # print(concatination[9:])
        return concatination[9:]
    except:
        a = 'No'
        concatination += a
        print(concatination)
    return concatination


# print(get_diabetes_scoring(7))
