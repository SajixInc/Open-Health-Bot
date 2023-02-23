

import json
import requests


def Get_By_District(district_name,state_name):
    api = "http://localhost:8000/OpenHealthBot/vaccineSlotsbydistrict/{}/{}/".format(state_name,district_name)
    headers = {'Content-Type': 'application/json','Authorization':'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    response = requests.get(api,headers=headers)
    data=response.json()
    total=[]
    output=""
    a=data['Message']
    print(a)
    if a=="Successful":
        for i in data['Result']:
            a = i['min_age_limit']
            total.append("**Vaccination Center Name: **"+i['name']+" | "+"** Address: **"+i['address']+" | "+"** Age: **"+str(a)+" | "+"** Vaccine Name: **"+i['vaccine'])
        for j in total:
            output+=str(j)+"||"
        return output[:-2]
    else:
        return a
print(Get_By_District("Visakhapatnam","Andhra Pradesh"))

def Get_By_Pincode(pincode):
    api = "http://localhost:8000/OpenHealthBot/vaccineSlotsbypincode/{}/".format(pincode)
    headers = {'Content-Type': 'application/json','Authorization':'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    response = requests.get(api,headers=headers)
    data=response.json()
    total=[]
    output=""
    a=data['Message']
    if a=="Successful":
        for i in data['Result']:
            print(i)
            a = i['min_age_limit']
            total.append("**Vaccination Center Name: **"+i['name']+" | "+"** Address: **"+i['address']+" | "+"** Age: **"+str(a)+" | "+"** Vaccine Name: **"+i['vaccine'])
        for j in total:
            output+=str(j)+"||"
            return output[:-2]
    else:
        return a

def Get_By_Pincode_Date(pincode,Date):
    api = "http://localhost:8000/OpenHealthBot/vaccineSlotsbypincodeanddate/{}/{}/".format(pincode,Date)
    headers = {'Content-Type': 'application/json','Authorization':'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    response = requests.get(api,headers=headers)
    data=response.json()
    total=[]
    output=""
    #print("dad")
    a=data['Message']
    if a=="Successful":
        for i in data['Result']:
            print(i)
            total.append("**Vaccination Center Name: **"+i['name']+" | "+"** Address: **"+i['address'])
        for j in total:
            output+=str(j)+"||"
        return output[:-2]
    else:
        return a

##############################################################################################################


def Get_Question(id):
    api = "http://localhost:8000/UserAssessment/GetAllQuestionsLifeStyleScoringV2/"
    headers = {'Content-Type': 'application/json',
            'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    response = requests.get(url=api, headers=headers)
    data=response.json()['Result']
    qid = data[id]['id']
    question = data[id]['Question']
    sub_category = data[id]['Sub_category']

    return qid,question,sub_category



##################################################################################################################


def question_post(userId,questionid,answer,age,category,sub_category,interaction_id):
    Api = 'http://localhost:8000/OpenHealthBot/OpenHealthLifestyleScorePostAPI/'
    headers = {'Content-Type': 'application/json',
            'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    # null = None
    score1 = {
        "UserId": userId,
        # "FamilyId": None,
        "QuestionId": questionid,
        "Answer": answer,
        "Age": age,
        "Category": category,
        "Sub_category": sub_category,
        "InteractionId": interaction_id
    }
    r = requests.post(Api, json=score1, headers=headers)
    a1 = r.json()
    return a1

    #######################################################################################################

def question_postretake(userId,questionid,answer,age1,category,sub_category,interaction_id1):
    Api = 'http://localhost:8000/OpenHealthBot/OpenHealthLifestyleScorePostAPI/'
    headers = {'Content-Type': 'application/json',
            'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    score1 = {
        "UserId": userId,
        "QuestionId": questionid,
        "Answer": answer,
        "Age": age1,
        "Category": category,
        "Sub_category": sub_category,
        "InteractionId": interaction_id1
    }
    r = requests.post(Api, json=score1, headers=headers)
    a2 = r.json()
    return a2
 

    a = r.json()
    # print(a)

    #######################################################################################################
 
def get_interaction(userid):
    data = {
    "UserId": userid,
    "Category": "Lifestyle"
    }
    api = "http://localhost:8000/OpenHealthBot/OpenHealthIntractionPostApi/"
    headers = {'Content-Type': 'application/json',
                'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    
    r = requests.post(api, json=data, headers=headers)
    print("ss",r)
    a = r.json()
    # print(a)
    interaction_id = a['Result']['id']
    return interaction_id
# print(get_interaction(5))

############################################



def get_userid(number):

    api = "http://localhost:8000/OpenHealthBot/"
    headers = {'Content-Type': 'application/json',
                'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    
    phone = {
        "MobileNumber": '+91'+str(number),

    }
    get = requests.get(f'{api}OpenHealthBotUserByMobile/{phone["MobileNumber"]}/', headers=headers)
    data = get.json()
    if data['HasError'] == True:
        r = requests.post(f'{api}OpenHealthRegister/', json=phone, headers=headers)
        a = r.json()
        print(a)
        userId = a['Result']['id']
        return userId
    else:
        # print(data)
        # global userId
        userId = data['Result']['id']
        return userId






####################################depression################################


def Get_depression_Question(id):
    api = "http://localhost:8000/UserAssessment/GetAllQuestionsDepressionV2/"
    headers = {'Content-Type': 'application/json',
            'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    response = requests.get(url=api, headers=headers)
    data=response.json()['Result']
    # print(data)
    # global qid
    # global question
    # global category
    qid1 = data[id]['id']
    question1 = data[id]['Question']

    return qid1,question1


def depression_question_post(userId,questionid1,depressionanswer,age,category,interaction_id):
    Api = 'http://localhost:8000/OpenHealthBot/OpenHealthDepressionPostAPI/'
    headers = {'Content-Type': 'application/json',
            'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    # null = None
    score1 = {
        "UserId": userId,
        "QuestionId": questionid1,
        "Answer": depressionanswer,
        "Age": age,
        "Category": category,
        "InteractionId": interaction_id
    }
    r = requests.post(Api, json=score1, headers=headers)
    a = r.json()
    # print(a)
    return a

def depression_get_interaction(userid):
    data = {
        "UserId": userid,
        "Category": "Depression"
    }
    api = "http://localhost:8000/OpenHealthBot/OpenHealthIntractionPostApi/"
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}

    r = requests.post(api, json=data, headers=headers)
    # print("ss", r)
    a = r.json()
    # print(a)
    interaction_id1 = a['Result']['InteractionId']
    print(interaction_id1)
    return interaction_id1


################################################diabetes#######################################


def Get_diabetes_Question(id):
    api = "http://localhost:8000/UserAssessment/GetAllQuestionsDiabetesV2/"
    headers = {'Content-Type': 'application/json',
            'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    response = requests.get(url=api, headers=headers)
    data=response.json()['Result']
    # print(data)
    # global qid
    # global question
    # global category
    qid2 = data[id]['id']
    question2 = data[id]['Question']

    return qid2,question2


def diabetes_question_post(userId,questionid2,diabetesanswer,age,category,interaction_id):
    Api = 'http://localhost:8000/OpenHealthBot/OpenHealthDiabetesPost/'
    headers = {'Content-Type': 'application/json',
            'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    # null = None
    score1 = {
        "UserId": userId,
        "QuestionId": questionid2,
        "Answer": diabetesanswer,
        "Age": age,
        "Category": category,
        "InteractionId": interaction_id
    }
    r = requests.post(Api, json=score1, headers=headers)
    a = r.json()
    # print(a)
    return a

def diabetes_get_interaction(userid):
    data = {
        "UserId": userid,
        "Category": "Diabetes"
    }
    api = "http://localhost:8000/OpenHealthBot/OpenHealthIntractionPostApi/"
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}

    r = requests.post(api, json=data, headers=headers)
    # print("ss", r)
    a = r.json()
    # print(a)
    interaction_id2 = a['Result']['InteractionId']
    # print(interaction_id2)
    return interaction_id2
# print(diabetes_get_interaction(7))
