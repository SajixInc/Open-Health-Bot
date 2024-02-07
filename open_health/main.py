

import json
import requests
from urls import url, token


def Get_By_District(district_name,state_name):
    # api = "http://localhost:8000/OpenHealthBot/vaccineSlotsbydistrict/{}/{}/".format(state_name,district_name)
    # headers = {'Content-Type': 'application/json','Authorization':'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    api = url+"OpenHealthBot/vaccineSlotsbydistrict/{}/{}/".format(state_name,district_name)
    headers = {'Content-Type': "application/json",'Authorization': token}

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
# print(Get_By_District("Visakhapatnam","Andhra Pradesh"))

def Get_By_Pincode(pincode):
    # api = "http://localhost:8000/OpenHealthBot/vaccineSlotsbypincode/{}/".format(pincode)
    # headers = {'Content-Type': 'application/json','Authorization':'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    api = url+"OpenHealthBot/vaccineSlotsbypincode/{}/".format(pincode)
    print(api, "12345")
    headers = {'Content-Type': "application/json",'Authorization': token}
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
    # api = "http://localhost:8000/OpenHealthBot/vaccineSlotsbypincodeanddate/{}/{}/".format(pincode,Date)
    # headers = {'Content-Type': 'application/json','Authorization':'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    api = url+"OpenHealthBot/vaccineSlotsbypincodeanddate/{}/{}/".format(pincode,Date)
    headers = {'Content-Type': "application/json",'Authorization': token}
    
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
    # api = "http://localhost:8000/UserAssessment/GetAllQuestionsLifeStyleScoringV2/"
    # headers = {'Content-Type': 'application/json',
    #         'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    
    api = url+ "OpenHealthBot/GetAllQuestionsLifeStyleScoringV2/"
    headers = {'Content-Type': "application/json",'Authorization': token}
    response = requests.get(api, headers=headers)
    data=response.json()['Result']
    qid = data[id]['id']
    question = data[id]['Question']
    sub_category = data[id]['Sub_category']

    return qid,question,sub_category



##################################################################################################################


def question_post(userId,questionid,answer,age,category,sub_category,interaction_id):
    # Api = 'http://localhost:8000/OpenHealthBot/OpenHealthLifestyleScorePostAPI/'
    # headers = {'Content-Type': 'application/json',
    #         'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    # null = None
    api = url+"OpenHealthBot/OpenHealthLifestyleScorePostAPI/"
    print(api,"apiiiii")
    headers = {'Content-Type': "application/json",'Authorization': token}
    print(headers,"its headersksjskss")
    score1 = {
        "UserId": userId,
        "QuestionId": questionid,
        "Answer": answer,
        "Age": age,
        "Category": category,
        "Sub_category": sub_category,
        "InteractionId": interaction_id
    }
    print(score1,"asdfghjk")
    r = requests.post(api, json=score1, headers=headers)
    print(r,"lkjhgfds")
    a1 = r.json()
    return a1

    #######################################################################################################

def question_postretake(userId,questionid,answer,age1,category,sub_category,interaction_id1):
    # Api = 'http://localhost:8000/OpenHealthBot/OpenHealthLifestyleScorePostAPI/'
    # headers = {'Content-Type': 'application/json',
    #         'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    
    api = url + "OpenHealthBot/OpenHealthLifestyleScorePostAPI/"
    headers = {'Content-Type': "application/json",'Authorization': token} 
    score1 = {
    "UserId": userId,
    "QuestionId": questionid,
    "Answer": answer,
    "Age": age1,
    "Category": category,
    "Sub_category": sub_category,
    "InteractionId": interaction_id1
    }
    print(score1, "its printing")
    r = requests.post(api, json=score1, headers=headers)
    a2 = r.json()
    print(a2,"aaaaaaaaaaaaaa22222222222222222")
    return a2
 

    a = r.json()
    # print(a)

    #######################################################################################################
 
def get_interaction(userid):
    data = {
    "UserId": userid,
    "Category": "Lifestyle"
    }
    # api = "http://localhost:8000/OpenHealthBot/OpenHealthIntractionPostApi/"
    # headers = {'Content-Type': 'application/json',
    #             'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    
    api = url+"OpenHealthBot/OpenHealthIntractionPostApi/"
    headers = {'Content-Type': "application/json",'Authorization': token}
    r = requests.post(api, json=data, headers=headers)
    print("ss",r)
    a = r.json()
    # print(a)
    interaction_id = a['Result']['id']
    return interaction_id
# print(get_interaction(5))

############################################



def get_userid(number):

    # api = "http://localhost:8000/OpenHealthBot/"
    # headers = {'Content-Type': 'application/json',
    #             'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    api = url+"OpenHealthBot/"
    headers = {'Content-Type': "application/json",'Authorization': token}

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
    # api = "http://localhost:8000/UserAssessment/GetAllQuestionsDepressionV2/"
    # headers = {'Content-Type': 'application/json',
    #         'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    
    api = url+"OpenHealthBot/GetAllQuestionsDepressionV2/"
    print(api, "12345")
    headers = {'Content-Type': "application/json",'Authorization': token}
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
    # Api = 'http://localhost:8000/OpenHealthBot/OpenHealthDepressionPostAPI/'
    # headers = {'Content-Type': 'application/json',
    #         'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    # null = None
    api = url+"OpenHealthBot/OpenHealthDepressionPostAPI/"
    headers = {'Content-Type': "application/json",'Authorization': token}
    score1 = {
        "UserId": userId,
        "QuestionId": questionid1,
        "Answer": depressionanswer,
        "Age": age,
        "Category": category,
        "InteractionId": interaction_id
    }
    print(score1, "its printing")
    r = requests.post(api, json=score1, headers=headers)
    a = r.json()
    print(a,"aaaaaaaaaaaaaaaaaaaaaa")
    return a

def depression_get_interaction(userid):
    data = {
        "UserId": userid,
        "Category": "Depression"
    }
    # api = "http://localhost:8000/OpenHealthBot/OpenHealthIntractionPostApi/"
    # headers = {'Content-Type': 'application/json',
    #            'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}

    api = url+"OpenHealthBot/OpenHealthIntractionPostApi/"
    headers = {'Content-Type': "application/json",'Authorization': token}
    r = requests.post(api, json=data, headers=headers)
    # print("ss", r)
    a = r.json()
    # print(a)
    interaction_id1 = a['Result']['InteractionId']
    print(interaction_id1)
    return interaction_id1


################################################diabetes#######################################


def Get_diabetes_Question(id):
    # api = "http://localhost:8000/UserAssessment/GetAllQuestionsDiabetesV2/"
    # headers = {'Content-Type': 'application/json',
    #         'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    
    api = url+"OpenHealthBot/GetAllQuestionsDiabetesV2/"
    headers = {'Content-Type': "application/json",'Authorization': token}
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
    # Api = 'http://localhost:8000/OpenHealthBot/OpenHealthDiabetesPost/'
    # headers = {'Content-Type': 'application/json',
    #         'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
    # null = None
    api = url+"OpenHealthBot/OpenHealthDiabetesPost/"
    headers = {'Content-Type': "application/json",'Authorization': token}
    score1 = {
        "UserId": userId,
        "QuestionId": questionid2,
        "Answer": diabetesanswer,
        "Age": age,
        "Category": category,
        "InteractionId": interaction_id
    }
    r = requests.post(api, json=score1, headers=headers)
    a = r.json()
    # print(a)
    return a

def diabetes_get_interaction(userid):
    data = {
        "UserId": userid,
        "Category": "Diabetes"
    }
    # api = "http://localhost:8000/OpenHealthBot/OpenHealthIntractionPostApi/"
    # headers = {'Content-Type': 'application/json',
    #            'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}

    api = url+"OpenHealthBot/OpenHealthIntractionPostApi/"
    headers = {'Content-Type': "application/json",'Authorization': token}
    r = requests.post(api, json=data, headers=headers)
    # print("ss", r)
    a = r.json()
    # print(a)
    interaction_id2 = a['Result']['InteractionId']
    # print(interaction_id2)
    return interaction_id2
# print(diabetes_get_interaction(7))





###################################### Search helath topic function ###############################


# import requests
# import webbrowser
# import json
# def get_details(query):
#     Api = 'https://www.googleapis.com/customsearch/v1?key=###########################################={}'.format(query)
#     print(Api)
#     response = requests.get(url=Api)
#     print(response)
#     count=response.json()['queries']['request'][0]['count']
#     title=response.json()['items'][0]['link']
#     print(title)
#     print(count)
#     message=""
#     if count<5:
#         for i in range(count):
#             link=response.json()['items'][i]['link']
#             title=response.json()['items'][i]['title']
#             link1 = link + '\n'
#             message +='['+title+']'+'('+link1+')' + '\n' + '\n'
#         return message
    
#     else:
#         for i in range(5):
#             link=response.json()['items'][i]['link']
#             title=response.json()['items'][i]['title']
#             link1 = link + '\n'
#             message +='['+title+']'+'('+link1+')' + '\n' + '\n'
#         return message
    

# # print(get_details("covid"))    


import requests

def get_details(query):
    api_key = 'AIzaSyCh5jPsn1NoB1B9AVL9PvFRS-s13QNnis4'
    cx = '62398b8d5473f42ae'
    url = f'https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx}&q={query}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()
        
        if 'items' in data:
            message = ""
            for item in data['items'][:5]:  
                link = item['link']
                title = item['title']
                message += f"[{title}]({link})\n\n"
            return message
        else:
            return "No results found."
            
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# Example usage:
# query = input("Enter your search query: ")
# print(get_details(query))
