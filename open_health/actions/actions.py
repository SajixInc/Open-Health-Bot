from  typing import Any, Text, Dict, List
from lifestyle_scoring import get_lifestyle_scoring

from main import Get_By_Pincode_Date, question_postretake

from main import Get_By_Pincode_Date,Get_depression_Question,Get_diabetes_Question,diabetes_get_interaction
from depression_scoring import get_depression_scoring
from diabetes_scoring import get_diabetes_scoring
from main import Get_By_Pincode
from main import get_userid, Get_By_District, Get_Question, question_post, depression_question_post, \
    depression_get_interaction,diabetes_question_post
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import Restarted, EventType, SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
import requests
import re
import json


class ValidatemobilenumberForm(FormValidationAction):
    def name(self) -> Text:
        return "mobile_number_validation"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        global number
        number = tracker.get_slot('MobileNumber')
        vnumber=re.fullmatch('[6-9][0-9]{9}',number)
        print(vnumber)
        if vnumber!=None:
            phone = {
                "phone_number": '+91' + number,

            }
            api = "http://localhost:8000/OpenHealthBot/otp_generation"
            headers = {'Content-Type': 'application/json',
                        'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
            
            r = requests.post(api, json=phone, headers=headers)
            print(r)
            a = r.json()
            print(a)
            otp = a['Result']['Otp']
            global otp1
            global Id
            otp1 = otp
            Id = a['Result']['id']
            return [FollowupAction("slot_otp_validation_form")]
        else:
            dispatcher.utter_message(text="Incorrect MobileNumber, Mobile number should be 10 digits")
            return [FollowupAction("slot_open_health_form"),SlotSet('MobileNumber', None)]




class ValidateotpForm(FormValidationAction):
    def name(self) -> Text:
        return "validation_for_otp"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        OTP = tracker.get_slot('Otp')

        if otp1 == OTP:
            print("You have Successfully verified the session with mobile# ending with xxxx"+number[6:])
          
            dispatcher.utter_message(text="You have Successfully verified the session with mobile# ending with xxxx"+number[6:])
        else:
            print("You entered Invalid OTP")
            dispatcher.utter_message(text="You entered Invalid OTP")
            return [FollowupAction("slot_otp_validation_form"),SlotSet("Otp", None)]
        return [FollowupAction("slot_user_registration_form")]


class User_Validation(FormValidationAction):

    def name(self) -> Text:
        return "user_validation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict) -> List[EventType]:
        age = tracker.get_slot("Age")
        global age_val
        age_val =age
        

        buttons = [
            {'payload': '/male_option{"options_button":"Male"}', 'title': "Male"},
            {'payload': '/female_option{"options_button":"Female"}', 'title': "Female"},
            {'payload': '/others_option{"options_button":"Others"}', 'title': "Others"}
        ]
        dispatcher.utter_message(
            text="Please provide me your gender to assist you with the relevant health information", buttons=buttons)
        return []


class SubmitGenderOptionsForm(FormValidationAction):

    def name(self) -> Text:
        return "submit_validation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict) -> List[EventType]:
        buttons = [
            {'payload': '/white_option{"ethnicity_button":"white"}', 'title': "white"},
            {'payload': '/Black or African American_option{"ethnicity_button":"Black or African American"}',
             'title': "Black"},
            {'payload': '/Asian_option{"ethnicity_button":"Asian"}', 'title': "Asian"},
            {
                'payload': '/Native Hawaiian or Other Pacific Islander_option{"ethnicity_button":"Native Hawaiian or Other Pacific Islander"}',
                'title': "Native Hawaiian"},
            {
                'payload': '/American Indian or Alaska Native_option{"ethnicity_button":"American Indian or Alaska Native"}',
                'title': "American Indian"},
            {'payload': '/Hispanic or Latino_option{"ethnicity_button":"Hispanic or Latino"}',
             'title': "Hispanic or Latino"}
        ]
        dispatcher.utter_message(
            text="Please provide me your ethenicity to assist you with the relevant health information, Please check this link to know about Ethnicity-[Link](https://grants.nih.gov/grants/guide/notice-files/NOT-OD-15-089.html)",
            buttons=buttons)
        return []


class SubmitEthenicityOptionsForm(FormValidationAction):

    def name(self) -> Text:
        return "Ethnicity_validation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict) -> List[EventType]:

        api = "http://localhost:8000/OpenHealthBot/demographic_generation"

        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}

        user = {
            "InteractionId": Id,
            "age": age_val,
            "gender": tracker.get_slot("options_button"),
            "ethnicity": tracker.get_slot("ethnicity_button")
        }

        r = requests.post(api, json=user, headers=headers)
        h = r.json()['Message']
        if h == 'Successful':
            buttons = [
            {'payload': "/Covid-19", 'title': "Covid19"},
            {'payload': "/Lifeeasy_Assessment", 'title': "Health Assessment"},
            # {'payload': "/Back", 'title': "Go Back"},
            # {'payload': "/MainMenu", 'title': "Main Menu"}
            ]
            dispatcher.utter_message(text="Hi Anonymous User,You can proceed with the options provided below.",
                                     buttons=buttons)
            return []
        else:
            dispatcher.utter_message(text=h)
            return []
        

######################################


class ActionGetByDistrict(Action):

    def name(self) -> Text:
        return "show_Details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message=Get_By_District(tracker.get_slot("District_Name"),tracker.get_slot("State_Name"))
        District_Name = tracker.get_slot("District_Name")
        State_Name = tracker.get_slot("State_Name")
        buttons = [
            {'payload': "/Back_to_Menu", 'title': "Back to Menu"}
        ]
        dispatcher.utter_message(text=f"Here are the vaccination centers available for {District_Name} {State_Name}")
        dispatcher.utter_message(text=message, buttons=buttons)
        return [SlotSet("District_Name", None), SlotSet("State_Name")]


class ActionGetByPincode(Action):

    def name(self) -> Text:
        return "show_Details_with_pincode"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pincode=tracker.get_slot("pincode")
        message=Get_By_Pincode(tracker.get_slot("pincode"))
        buttons = [
            {'payload': "/Back_to_Menu", 'title': "Back to Menu"}
        ]
        dispatcher.utter_message(text=f"Here are the vaccination centers available for this pincode {pincode}")
        dispatcher.utter_message(text=message, buttons=buttons)
        return [SlotSet("pincode", None)]


class ActionGetByPincodeAndDate(Action):

    def name(self) -> Text:
        return "show_Details_with_pincode_Date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = Get_By_Pincode_Date(tracker.get_slot("pincode1"), tracker.get_slot("Date"))
        pincode1 = tracker.get_slot("pincode1")
        Date = tracker.get_slot("Date")
        buttons = [
            {'payload': "/Back_to_Menu", 'title': "Back to Menu"}
        ]
        dispatcher.utter_message(text=f"Here are the vaccination centers available for {pincode1} {Date}")
        dispatcher.utter_message(text=message,buttons=buttons)
        return [SlotSet("pincode1",None),SlotSet("Date",None)]
#############################################################
class ActionZeroLifestylescoring(Action):
    def name(self) -> Text:
        return "Zero_lifestyle_score_assessment"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global lifestyle_score
        userId=get_userid(number)
        lifestyle_score = get_lifestyle_scoring(userId)
        if lifestyle_score == 'No':
            buttons = [
            {'payload': "/take_assessment", 'title': "Take Assessment"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
            ]
            dispatcher.utter_message(text="😮 You have not taken the personalized health assessment yet. Please get your free personalized health assessment and it will be completed in no time.")
            dispatcher.utter_message(text="Take a quiz and get your free personalized health assessment", buttons=buttons)
            return []
        else:
            print(lifestyle_score, "sdfsdf")              
            buttons = [
                {'payload': "/Retake_assessment_first", 'title': "Retake Assessment"},
                {'payload': "/assessment_options", 'title': "Go Back"},
                {'payload': "/MainMenu", 'title': "Main Menu"}
            ]
            if lifestyle_score <= str(20):
                dispatcher.utter_message(text="**Your lifestyle score is: **" + lifestyle_score + ' - We suggest to Consult with General Physician for better clarity')
                dispatcher.utter_message(text="Take a quiz and get your free personalized health assessment", buttons=buttons)
                return []
            else:
                dispatcher.utter_message(text="**Your lifestyle score is: **" + lifestyle_score + ' -  But you can always consult with General Physician for better clarity')
                dispatcher.utter_message(text="Take a quiz and get your free personalized health assessment", buttons=buttons)
            return []



###########################################################   1st  lifestylescoring   ################################

class ActionFirstLifestylescoring(Action):
    def name(self) -> Text:
        return "First_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        global userId
        global age
        age = tracker.get_slot("Age")
        message=get_userid(tracker.get_slot('MobileNumber'))
        
        userId=message
        print(userId)
        data = {
            "UserId": userId,
            "Category": "Lifestyle"
        }
        print(data)
        api = "http://localhost:8000/OpenHealthBot/OpenHealthIntractionPostApi/"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
        
        r = requests.post(api, json=data, headers=headers)
        ab = r.json()
        print(ab)
        global interaction_id
        inter = ab['Result']['InteractionId']
        interaction_id = inter
        print(interaction_id)
        global qid
        global a
        qid,question,sub_category=Get_Question(0)
        a = sub_category 
        print(question)
        print(qid)
        print(sub_category)
        
        buttons = [
            {'payload': '/scoring_yes1{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no1{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


######################################  2nd   lifestylescoring   ################################

class ActionSecondLifestylescoring(Action):
    def name(self) -> Text:
        return "Second_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message=get_userid(tracker.get_slot('MobileNumber'))
        id1 = message
        print(id1)
        print(question_post(id1,1,tracker.get_slot("Answer"),age,"Lifestyle",a,interaction_id))
        global b
        qid,question,sub_category=Get_Question(1)
        b = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes2{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no2{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
       
        return[]

################################# 3rd   lifestylescoring   ####################################

class ActionThirdLifestylescoring(Action):
    def name(self) -> Text:
        return "Third_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,2,tracker.get_slot("Answer"),age,"Lifestyle",b,interaction_id))
        global c
        qid,question,sub_category=Get_Question(2)
        c = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes3{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no3{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


############################ 4th   lifestylescoring  #############################################

class ActionFourthLifestylescoring(Action):
    def name(self) -> Text:
        return "Fourth_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,3,tracker.get_slot("Answer"),age,"Lifestyle",c,interaction_id))

        global d
        qid,question,sub_category=Get_Question(3)
        d = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes4{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no4{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


#################################### 5th  lifestylescoring   ########################################

class ActionFifthLifestylescoring(Action):
    def name(self) -> Text:
        return "Fifth_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,4,tracker.get_slot("Answer"),age,"Lifestyle",d,interaction_id))
        global e
        qid,question,sub_category=Get_Question(4)
        e = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes5{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no5{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  6th  lifestylescoring   ###################################


class ActionSixthLifestylescoring(Action):
    def name(self) -> Text:
        return "Sixth_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,5,tracker.get_slot("Answer"),age,"Lifestyle",e,interaction_id))
        global f

        qid,question,sub_category=Get_Question(5)
        f = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes6_0{"Answer":"less than 30"}', 'title': "Less than 30"},
            {'payload': '/scoring_yes6_1{"Answer":"30"}', 'title': "30"},
            {'payload': '/scoring_yes6_2{"Answer":"45"}', 'title': "45"},
            {'payload': '/scoring_yes6_3{"Answer":"60"}', 'title': "60"},
            {'payload': '/scoring_yes6_4{"Answer":"90"}', 'title': "90"},
            {'payload': '/scoring_yes6_5{"Answer":"120"}', 'title': "120"},
            {'payload': '/scoring_yes6_6{"Answer":"150"}', 'title': "150"},
            {'payload': '/scoring_yes6_7{"Answer":"180"}', 'title': "180"},
            {'payload': '/scoring_yes6_8{"Answer":"210"}', 'title': "210"},
            {'payload': '/scoring_yes6_9{"Answer":"240"}', 'title': "240"},
            {'payload': '/scoring_yes6_10{"Answer":"270"}', 'title': "270"},
            {'payload': '/scoring_yes6_11{"Answer":"300+"}', 'title': "300+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  7th  lifestylescoring   ###################################


class ActionSeventhLifestylescoring(Action):
    def name(self) -> Text:
        return "Seventh_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,6,tracker.get_slot("Answer"),age,"Lifestyle",f,interaction_id))
        global g

        qid,question,sub_category=Get_Question(6)
        g = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes7_0{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes7_1{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes7_2{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes7_3{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes7_4{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes7_5{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes7_6{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes7_7{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes7_8{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes7_9{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes7_10{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  8th   lifestylescoring  ###################################


class ActionEighthLifestylescoring(Action):
    def name(self) -> Text:
        return "Eighth_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,7,tracker.get_slot("Answer"),age,"Lifestyle",g,interaction_id))
        global h

        qid,question,sub_category=Get_Question(7)
        h = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes8_0{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes8_1{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes8_2{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes8_3{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes8_4{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes8_5{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes8_6{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes8_7{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes8_8{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes8_9{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes8_10{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  9th   lifestylescoring  ###################################


class ActionNinthLifestylescoring(Action):
    def name(self) -> Text:
        return "Ninth_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,8,tracker.get_slot("Answer"),age,"Lifestyle",h,interaction_id))
        global i
        qid,question,sub_category=Get_Question(8)
        i = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes9_0{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes9_1{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes9_2{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes9_3{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes9_4{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes9_5{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes9_6{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes9_7{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes9_8{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes9_9{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes9_10{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  10th   lifestylescoring  ###################################


class ActionTenLifestylescoring(Action):
    def name(self) -> Text:
        return "Ten_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,9,tracker.get_slot("Answer"),age,"Lifestyle",i,interaction_id))
        
        global j
       
        qid,question,sub_category=Get_Question(9)
        j = sub_category
        print(j)
        buttons = [
            {'payload': '/scoring_yes10_0{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes10_1{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes10_2{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes10_3{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes10_4{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes10_5{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes10_6{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes10_7{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes10_8{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes10_9{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes10_10{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  11th   lifestylescoring   ###################################


class ActionElevenLifestylescoring(Action):
    def name(self) -> Text:
        return "Eleven_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,10,tracker.get_slot("Answer"),age,"Lifestyle",j,interaction_id))
        global k

        qid,question,sub_category=Get_Question(10)
        k = sub_category
        buttons = [

            {'payload': '/scoring_yes11{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no11{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  12th   lifestylescoring    ###################################


class ActionTwelveLifestylescoring(Action):
    def name(self) -> Text:
        return "Twelve_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,11,tracker.get_slot("Answer"),age,"Lifestyle",k,interaction_id))

        global l
        qid,question,sub_category=Get_Question(11)
        l = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes12_0{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes12_1{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes12_2{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes12_3{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes12_4{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes12_5{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes12_6{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes12_7{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes12_8{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes12_9{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes12_10{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
       
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  13th   lifestylescoring   ###################################


class ActionThirteenLifestylescoring(Action):
    def name(self) -> Text:
        return "Thirteen_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,12,tracker.get_slot("Answer"),age,"Lifestyle",l,interaction_id))
        global m
       
        qid,question,sub_category=Get_Question(12)
        m = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes13_0{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes13_1{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes13_2{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes13_3{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes13_4{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes13_5{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes13_6{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes13_7{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes13_8{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes13_9{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes13_10{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}

        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  14th    lifestylescoring   ###################################


class ActionFourteenLifestylescoring(Action):
    def name(self) -> Text:
        return "Fourteen_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,13,tracker.get_slot("Answer"),age,"Lifestyle",m,interaction_id))
        global n

        qid,question,sub_category=Get_Question(13)
        n = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes14_0{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes14_1{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes14_2{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes14_3{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes14_4{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes14_5{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes14_6{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes14_7{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes14_8{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes14_9{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes14_10{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  15th    lifestylescoring   ###################################


class ActionFifteenLifestylescoring(Action):
    def name(self) -> Text:
        return "Fifteen_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,14,tracker.get_slot("Answer"),age,"Lifestyle",n,interaction_id))
        global o

        qid,question,sub_category=Get_Question(14)
        o = sub_category
        print(o)
        buttons = [
            {'payload': '/scoring_yes15_0{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes15_1{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes15_2{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes15_3{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes15_4{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes15_5{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes15_6{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes15_7{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes15_8{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes15_9{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes15_10{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  16th   lifestylescoring  ###################################


class ActionSixteenLifestylescoring(Action):
    def name(self) -> Text:
        return "Sixteen_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,15,tracker.get_slot("Answer"),age,"Lifestyle",o,interaction_id))
        global p

        qid,question,sub_category=Get_Question(15)
        p = sub_category
        print(p)
        buttons = [
            
            {'payload': '/scoring_yes16{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no16{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  17th  lifestylescoring ###################################


class ActionSeventeenLifestylescoring(Action):
    def name(self) -> Text:
        return "Seventeen_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,16,tracker.get_slot("Answer"),age,"Lifestyle",p,interaction_id))
        global q
        qid,question,sub_category=Get_Question(16)
        q = sub_category
        print(q)
       
        buttons = [
            {'payload': '/scoring_yes17{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no17{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  18th  lifestylescoring ###################################


class ActionfirstLifestylescoring(Action):
    def name(self) -> Text:
        return "Eighteen_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,17,tracker.get_slot("Answer"),age,"Lifestyle",q,interaction_id))
        global r
  
        qid,question,sub_category=Get_Question(17)
        r = sub_category
        print(r)
       
        buttons = [
            {'payload': '/scoring_yes18{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no18{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  19th lifestylescoring ###################################


class ActionEighteenLifestylescoring(Action):
    def name(self) -> Text:
        return "Ninteen_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,18,tracker.get_slot("Answer"),age,"Lifestyle",r,interaction_id))
        global s
       
        qid,question,sub_category=Get_Question(18)
        s = sub_category
        print(s)
     
        buttons = [
            {'payload': '/scoring_yes19{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no19{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  20th lifestylescoring ###################################


                 
class ActionNinteenLifestylescoring(Action):
    def name(self) -> Text:
        return "Twenty_lifestyle_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,19,tracker.get_slot("Answer"),age,"Lifestyle",s,interaction_id))
        global t
         
        qid,question,sub_category=Get_Question(19)
        t = sub_category
        print(t)
        buttons = [
            {'payload': '/scoring_yes20_0{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes20_1{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes20_2{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes20_3{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes20_4{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes20_5{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes20_6{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes20_7{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes20_8{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes20_9{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes20_10{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        
        dispatcher.utter_message(text=question, buttons=buttons)
        return []

###########################################


class ActionTwentyLifestylescoring(Action):
    def name(self) -> Text:
        return "Twentyone_lifestyle_score_assessment"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,20,tracker.get_slot("Answer"),age,"Lifestyle",t,interaction_id))
        global u

        qid,question,sub_category=Get_Question(20)
        u = sub_category
        print(u)
        buttons = [
            
            {'payload': '/scoring_yes21_0{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes21_1{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes21_2{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes21_3{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes21_4{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes21_5{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes21_6{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes21_7{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes21_8{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes21_9{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes21_10{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []



###########################################

class ActionTwentyoneLifestylescoring(Action):
    def name(self) -> Text:
        return "Twentytwo_lifestyle_score_assessment"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_post(userId,21,tracker.get_slot("Answer"),age,"Lifestyle",u,interaction_id))
        lifestyle_score = get_lifestyle_scoring(userId)
        buttons = [
                    {'payload': "/Retake_assessment_first1", 'title': "Retake Assessment"},
                    {'payload': "/assessment_options", 'title': "Go Back"},
                    {'payload': "/MainMenu", 'title': "Main Menu"}
                ]
        dispatcher.utter_message(text="**Your lifestyle score is: **" + lifestyle_score + ' - We suggest to Consult with General Physician for better clarity')
        dispatcher.utter_message(text="Take a quiz and get your free personalized health assessment", buttons=buttons)
        return []






###########################################################   1st  lifestylescoring   ################################

class ActionFirstLifestylescoringretake(Action):
    def name(self) -> Text:
        return "First_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
        global age1
        age1 = tracker.get_slot("Age")
        message1=get_userid(tracker.get_slot('MobileNumber'))
        
        userId1=message1

        data = {
            "UserId": userId1,
            "Category": "Lifestyle"
        }
        print(data)
        api = "http://localhost:8000/OpenHealthBot/OpenHealthIntractionPostApi/"
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer <replace the token with open health bot Api (https://github.com/vivifyhealthcare/Open-Health-Bot-API) >'}
        
        r = requests.post(api, json=data, headers=headers)
        abc = r.json()
        print(abc)
        global interaction_id1
        interid1 = abc['Result']['InteractionId']
        interaction_id1 = interid1
        print(interaction_id1)

       
        qid,question,sub_category=Get_Question(0)
    
        print(question)
        print(qid)
        print(sub_category)
        
        buttons = [
            {'payload': '/scoring_yes1retake{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no1retake{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        # buttons = [
        #     {'payload': '/scoring_yes20{"Answer":"Yes"}', 'title': "Yes"},
        #     {'payload': '/scoring_no20{"Answer":"No"}', 'title': "No"},
        #     {'payload': "/assessment_options", 'title': "Go Back"},
        #     {'payload': "/MainMenu", 'title': "Main Menu"}
        # ]
        # dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


######################################  2nd   lifestylescoring   ################################

class ActionSecondLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Second_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message=get_userid(tracker.get_slot('MobileNumber'))
        id1 = message
        print(id1)
        print(question_postretake(id1,1,tracker.get_slot("Answer"),age1,"Lifestyle",a,interaction_id1))
        global b
        qid,question,sub_category=Get_Question(1)
        b = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes2retake{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no2retake{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
 
        return[]

################################# 3rd   lifestylescoring   ####################################

class ActionThirdLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Third_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,2,tracker.get_slot("Answer"),age1,"Lifestyle",b,interaction_id1))
        

        global c
        qid,question,sub_category=Get_Question(2)
        c = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes3retake{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no3retake{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []

############################ 4th   lifestylescoring  #############################################

class ActionFourthLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Fourth_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,3,tracker.get_slot("Answer"),age1,"Lifestyle",c,interaction_id1))

        global d
        qid,question,sub_category=Get_Question(3)
        d = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes4retake{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no4retake{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


#################################### 5th  lifestylescoring   ########################################

class ActionFifthLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Fifth_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,4,tracker.get_slot("Answer"),age1,"Lifestyle",d,interaction_id1))
        global e
        qid,question,sub_category=Get_Question(4)
        e = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes5retake{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no5retake{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


##########################################  6th  lifestylescoring   ###################################


class ActionSixthLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Sixth_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,5,tracker.get_slot("Answer"),age1,"Lifestyle",e,interaction_id1))
        global f
        qid,question,sub_category=Get_Question(5)
        f = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes6_0retake{"Answer":"less than 30"}', 'title': "Less than 30"},
            {'payload': '/scoring_yes6_1retake{"Answer":"30"}', 'title': "30"},
            {'payload': '/scoring_yes6_2retake{"Answer":"45"}', 'title': "45"},
            {'payload': '/scoring_yes6_3retake{"Answer":"60"}', 'title': "60"},
            {'payload': '/scoring_yes6_4retake{"Answer":"90"}', 'title': "90"},
            {'payload': '/scoring_yes6_5retake{"Answer":"120"}', 'title': "120"},
            {'payload': '/scoring_yes6_6retake{"Answer":"150"}', 'title': "150"},
            {'payload': '/scoring_yes6_7retake{"Answer":"180"}', 'title': "180"},
            {'payload': '/scoring_yes6_8retake{"Answer":"210"}', 'title': "210"},
            {'payload': '/scoring_yes6_9retake{"Answer":"240"}', 'title': "240"},
            {'payload': '/scoring_yes6_10retake{"Answer":"270"}', 'title': "270"},
            {'payload': '/scoring_yes6_11retake{"Answer":"300+"}', 'title': "300+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []


###########################################

##########################################  7th  lifestylescoring   ###################################




class ActionSeventhLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Seventh_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,6,tracker.get_slot("Answer"),age1,"Lifestyle",f,interaction_id1))
        global g

        qid,question,sub_category=Get_Question(6)
        g = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes7_0retake{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes7_1retake{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes7_2retake{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes7_3retake{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes7_4retake{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes7_5retake{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes7_6retake{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes7_7retake{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes7_8retake{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes7_9retake{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes7_10retake{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []




##########################################  8th   lifestylescoring  ###################################



class ActionEighthLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Eighth_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,7,tracker.get_slot("Answer"),age1,"Lifestyle",g,interaction_id1))
        global h

        qid,question,sub_category=Get_Question(7)
        h = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes8_0retake{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes8_1retake{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes8_2retake{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes8_3retake{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes8_4retake{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes8_5retake{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes8_6retake{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes8_7retake{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes8_8retake{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes8_9retake{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes8_10retake{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []




##########################################  9th   lifestylescoring  ###################################



class ActionNinthLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Ninth_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,8,tracker.get_slot("Answer"),age1,"Lifestyle",h,interaction_id1))
        global i

        qid,question,sub_category=Get_Question(8)
        i = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes9_0retake{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes9_1retake{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes9_2retake{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes9_3retake{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes9_4retake{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes9_5retake{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes9_6retake{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes9_7retake{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes9_8retake{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes9_9retake{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes9_10retake{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []



##########################################  10th   lifestylescoring  ###################################





class ActionTenLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Ten_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,9,tracker.get_slot("Answer"),age1,"Lifestyle",i,interaction_id1))
        
        global j

        qid,question,sub_category=Get_Question(9)
        j = sub_category
        print(j)
        buttons = [
            {'payload': '/scoring_yes10_0retake{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes10_1retake{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes10_2retake{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes10_3retake{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes10_4retake{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes10_5retake{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes10_6retake{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes10_7retake{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes10_8retake{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes10_9retake{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes10_10retake{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []



##########################################  11th   lifestylescoring   ###################################




class ActionElevenLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Eleven_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,10,tracker.get_slot("Answer"),age1,"Lifestyle",j,interaction_id1))
        global k
        qid,question,sub_category=Get_Question(10)
        k = sub_category
        buttons = [
            
            {'payload': '/scoring_yes11retake{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no11retake{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []





##########################################  12th   lifestylescoring    ###################################



class ActionTwelveLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Twelve_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,11,tracker.get_slot("Answer"),age1,"Lifestyle",k,interaction_id1))

        global l
        qid,question,sub_category=Get_Question(11)
        l = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes12_0retake{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes12_1retake{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes12_2retake{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes12_3retake{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes12_4retake{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes12_5retake{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes12_6retake{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes12_7retake{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes12_8retake{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes12_9retake{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes12_10retake{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
       
        dispatcher.utter_message(text=question, buttons=buttons)
        return []



##########################################  13th   lifestylescoring   ###################################




class ActionThirteenLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Thirteen_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,12,tracker.get_slot("Answer"),age1,"Lifestyle",l,interaction_id1))
        global m

        qid,question,sub_category=Get_Question(12)
        m = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes13_0retake{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes13_1retake{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes13_2retake{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes13_3retake{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes13_4retake{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes13_5retake{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes13_6retake{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes13_7retake{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes13_8retake{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes13_9retake{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes13_10retake{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}

        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []



##########################################  14th    lifestylescoring   ###################################




class ActionFourteenLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Fourteen_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,13,tracker.get_slot("Answer"),age1,"Lifestyle",m,interaction_id1))
        global n
  
        qid,question,sub_category=Get_Question(13)
        n = sub_category
        print(sub_category)
        buttons = [
            {'payload': '/scoring_yes14_0retake{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes14_1retake{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes14_2retake{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes14_3retake{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes14_4retake{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes14_5retake{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes14_6retake{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes14_7retake{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes14_8retake{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes14_9retake{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes14_10retake{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []





##########################################  15th    lifestylescoring   ###################################



class ActionFifteenLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Fifteen_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,14,tracker.get_slot("Answer"),age1,"Lifestyle",n,interaction_id1))
        global o
  
        qid,question,sub_category=Get_Question(14)
        o = sub_category
        print(o)
        buttons = [
            {'payload': '/scoring_yes15_0retake{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes15_1retake{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes15_2retake{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes15_3retake{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes15_4retake{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes15_5retake{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes15_6retake{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes15_7retake{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes15_8retake{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes15_9retake{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes15_10retake{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []



##########################################  16th   lifestylescoring  ###################################


class ActionSixteenLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Sixteen_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,15,tracker.get_slot("Answer"),age1,"Lifestyle",o,interaction_id1))
        global p
     
        qid,question,sub_category=Get_Question(15)
        p = sub_category
        print(p)
        buttons = [
           
            {'payload': '/scoring_yes16retake{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no16retake{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []



##########################################  17th  lifestylescoring ###################################




class ActionSeventeenLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Seventeen_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,16,tracker.get_slot("Answer"),age1,"Lifestyle",p,interaction_id1))
        global q
        
        qid,question,sub_category=Get_Question(16)
        q = sub_category
        print(q)
        
        buttons = [
            {'payload': '/scoring_yes17retake{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no17retake{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []





##########################################  18th  lifestylescoring ###################################



class ActionFirstLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Eighteen_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,17,tracker.get_slot("Answer"),age1,"Lifestyle",q,interaction_id1))
        global r

        qid,question,sub_category=Get_Question(17)
        r = sub_category
        print(r)
      
        buttons = [
            {'payload': '/scoring_yes18retake{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no18retake{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []





##########################################  19th lifestylescoring ###################################



class ActionEighteenLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Ninteen_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,18,tracker.get_slot("Answer"),age1,"Lifestyle",r,interaction_id1))
        global s

        qid,question,sub_category=Get_Question(18)
        s = sub_category
        print(s)
       
        buttons = [
            {'payload': '/scoring_yes19retake{"Answer":"Yes"}', 'title': "Yes"},
            {'payload': '/scoring_no19retake{"Answer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question, buttons=buttons)
        return []




##########################################  20th lifestylescoring ###################################


                 
class ActionNinteenLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Twenty_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,19,tracker.get_slot("Answer"),age1,"Lifestyle",s,interaction_id1))
        global t
         
        qid,question,sub_category=Get_Question(19)
        t = sub_category
        print(t)
        buttons = [
            {'payload': '/scoring_yes20_0retake{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes20_1retake{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes20_2retake{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes20_3retake{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes20_4retake{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes20_5retake{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes20_6retake{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes20_7retake{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes20_8retake{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes20_9retake{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes20_10retake{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        
        dispatcher.utter_message(text=question, buttons=buttons)
        return []

###########################################


class ActionTwentyLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Twentyone_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,20,tracker.get_slot("Answer"),age1,"Lifestyle",t,interaction_id1))
        global u

        qid,question,sub_category=Get_Question(20)
        u = sub_category
        print(u)
        buttons = [
            {'payload': '/scoring_yes21_0retake{"Answer":"less than 1"}', 'title': "Less than 1"},
            {'payload': '/scoring_yes21_1retake{"Answer":"1"}', 'title': "1"},
            {'payload': '/scoring_yes21_2retake{"Answer":"2"}', 'title': "2"},
            {'payload': '/scoring_yes21_3retake{"Answer":"3"}', 'title': "3"},
            {'payload': '/scoring_yes21_4retake{"Answer":"4"}', 'title': "4"},
            {'payload': '/scoring_yes21_5retake{"Answer":"5"}', 'title': "5"},
            {'payload': '/scoring_yes21_6retake{"Answer":"6"}', 'title': "6"},
            {'payload': '/scoring_yes21_7retake{"Answer":"7"}', 'title': "7"},
            {'payload': '/scoring_yes21_8retake{"Answer":"8"}', 'title': "8"},
            {'payload': '/scoring_yes21_9retake{"Answer":"9"}', 'title': "9"},
            {'payload': '/scoring_yes21_10retake{"Answer":"10+"}', 'title': "10+"},
            {'payload': "/Retake_assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text=question, buttons=buttons)
        return []



###########################################

class ActionTwentyoneLifestylescoringretake(Action):
    def name(self) -> Text:
        return "Twentytwo_lifestyle_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(question_postretake(userId,21,tracker.get_slot("Answer"),age1,"Lifestyle",u,interaction_id1))
        lifestyle_score = get_lifestyle_scoring(userId)
        buttons = [
                    {'payload': "/Retake_assessment_first1", 'title': "Retake Assessment"},
                    {'payload': "/assessment_options", 'title': "Go Back"},
                    {'payload': "/MainMenu", 'title': "Main Menu"}
                ]
        dispatcher.utter_message(text="**Your lifestyle score is: **" + lifestyle_score + ' - We suggest to Consult with General Physician for better clarity')
        dispatcher.utter_message(text="Take a quiz and get your free personalized health assessment", buttons=buttons)
        return []


####################################depression####################################################


#####################################1st depression_score###############################


class ActionZerodepressionscoring(Action):
    def name(self) -> Text:
        return "Zero_depression_score_assessment"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # global userId
        global lifestyle_score
        userId=get_userid(number)
        depression_score = get_depression_scoring(userId)
        if depression_score == 'No':
            buttons = [
            {'payload': "/take_assessment1", 'title': "Take Assessment"},
            # {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
            ]
            dispatcher.utter_message(text="😮 You have not taken the personalized depression assessment yet. Please get your free depression  assessment and it will be completed in no time.")
            dispatcher.utter_message(text="Take a quiz and get your free  depression assessment", buttons=buttons)
            return []
        else:
            print(depression_score, "sdfsdf")
            buttons = [
                {'payload': "/Retake_assessment_depression_first", 'title': "Retake Assessment"},
                {'payload': "/assessment_options", 'title': "Go Back"},
                {'payload': "/MainMenu", 'title': "Main Menu"}
            ]
            dispatcher.utter_message(
            text="**Your depression is: **" + depression_score + ' - We suggest to Consult with General Physician for better clarity')
            dispatcher.utter_message(text="Take a quiz and get your free depression assessment", buttons=buttons)
            return []
class Actiondepressionscoring(Action):
    def name(self) -> Text:
        return "First_depression_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global userId
        message = get_userid(tracker.get_slot('MobileNumber'))
        # print(message)
        userId = message
        print(userId)
        global age
        age = tracker.get_slot("Age")
        global qid1
        # global interaction_id1
        global i1
        interaction_id2 = depression_get_interaction(userId)
        i1 = interaction_id2
        print(i1)
        qid1, question1 = Get_depression_Question(0)
        # print(question1)
        # print(qid1)
        buttons = [
            {'payload': '/depressscoring_yes1{"depressionAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/depressscoring_no1{"depressionAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question1, buttons=buttons)
        return []


##################################2nd depression_score##############################################

class ActionSeconddepressionscoring(Action):
    def name(self) -> Text:
        return "Second_depression_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(depression_question_post(userId, 1, tracker.get_slot("depressionAnswer"),age, "Depression", i1))

        # global qid
        # global question
        # global category
        qid1, question1 = Get_depression_Question(1)
        # print(question1)
        buttons = [
            {'payload': '/depressscoring_yes2{"depressionAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/depressscoring_no2{"depressionAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question1, buttons=buttons)
        # dispatcher.utter_message(text=" ", buttons=buttons)
        # return [SlotSet("Answer", None)]
        return []


##################################3rd depression_score#######################################
class ActionThirddepressionscoring(Action):
    def name(self) -> Text:
        return "Third_depression_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(depression_question_post(userId, 2, tracker.get_slot("depressionAnswer"), age,"Depression", i1))

        # global qid
        # global question
        # global category
        qid1, question1 = Get_depression_Question(2)
        buttons = [
            {'payload': '/depressscoring_yes3{"depressionAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/depressscoring_no3{"depressionAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question1, buttons=buttons)
        # dispatcher.utter_message(text=" ", buttons=buttons)
        return []


################################4th depression_score###########################################
class ActionFourthdepressionscoring(Action):
    def name(self) -> Text:
        return "Fourth_depression_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(depression_question_post(userId, 3, tracker.get_slot("depressionAnswer"), age,"Depression", i1))
        # global qid
        # global question
        # global category
        qid1, question1 = Get_depression_Question(3)
        buttons = [
            {'payload': '/depressscoring_yes4{"depressionAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/depressscoring_no4{"depressionAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question1, buttons=buttons)
        # dispatcher.utter_message(text=" ", buttons=buttons)
        return []


class ActionFifthdepressionscoring(Action):
    def name(self) -> Text:
        return "Fifth_depression_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(depression_question_post(userId, 4, tracker.get_slot("depressionAnswer"),age, "Depression", i1))
        concatination = get_depression_scoring(userId)
        buttons = [
            {'payload': "/Retake_assessment_depression_first1", 'title': "Retake Assessment"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(
            text="**Your depression is: **" + concatination + ' - We suggest to Consult with General Physician for better clarity')
        dispatcher.utter_message(text="Take a quiz and get your free personalized health assessment", buttons=buttons)

        return []


############################################Diabetes#########################################


##################################1st diabetes_score##############################################

class ActionZerodiabetesscoring(Action):
    def name(self) -> Text:
        return "Zero_diabetes_score_assessment"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # global userId
        # global lifestyle_score
        userId=get_userid(number)
        diabetes_score = get_diabetes_scoring(userId)
        if diabetes_score == 'No':
            buttons = [
            {'payload': "/take_assessment2", 'title': "Take Assessment"},
            # {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
            ]
            dispatcher.utter_message(text="😮 You have not taken the personalized daibetes assessment yet. Please get your free diabetes  assessment and it will be completed in no time.")
            dispatcher.utter_message(text="Take a quiz and get your free  diabetes assessment", buttons=buttons)
            return []
        else:
            print(diabetes_score, "sdfsdf")
            buttons = [
                {'payload': "/Retake_assessment_first12", 'title': "Retake Assessment"},
                {'payload': "/assessment_options", 'title': "Go Back"},
                {'payload': "/MainMenu", 'title': "Main Menu"}
            ]
            dispatcher.utter_message(
            text="**Your diabetes is: **" + diabetes_score + ' - We suggest to Consult with General Physician for better clarity')
            dispatcher.utter_message(text="Take a quiz and get your free diabetes assessment", buttons=buttons)
            return []

class Actiondiabetesscoring(Action):
    def name(self) -> Text:
        return "First_diabetes_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global userId
        message = get_userid(tracker.get_slot('MobileNumber'))
        # print(message)
        userId = message
        print(userId)
        global age
        age = tracker.get_slot("Age")
        # global qid1
        # global interaction_id1
        global i2
        interaction_id2 = diabetes_get_interaction(userId)
        i2 = interaction_id2
        print(i2)
        qid2, question2 = Get_diabetes_Question(0)
        # print(question1)
        # print(qid1)
        buttons = [
            {'payload': '/diabetesscoring_yes1{"diabetesAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/diabetesscoring_no1{"diabetesAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question2, buttons=buttons)
        return []


##################################2nd diabetes_score##############################################

class ActionSeconddiabetesscoring(Action):
    def name(self) -> Text:
        return "Second_diabetes_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(diabetes_question_post(userId, 1, tracker.get_slot("diabetesAnswer"),age, "Diabetes", i2))

        # global qid
        # global question
        # global category
        qid2, question2 = Get_diabetes_Question(1)
        # print(question1)
        buttons = [
            {'payload': '/diabetesscoring_yes2{"diabetesAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/diabetesscoring_no2{"diabetesAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question2, buttons=buttons)
        # dispatcher.utter_message(text=" ", buttons=buttons)
        # return [SlotSet("Answer", None)]
        return []


##################################3rd diabetes_score#######################################
class ActionThirddiabetesscoring(Action):
    def name(self) -> Text:
        return "Third_diabetes_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(diabetes_question_post(userId, 2, tracker.get_slot("diabetesAnswer"), age,"Diabetes", i2))

        # global qid
        # global question
        # global category
        qid2, question2 = Get_diabetes_Question(2)
        buttons = [
            {'payload': '/diabetesscoring_yes3{"diabetesAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/diabetesscoring_no3{"diabetesAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question2, buttons=buttons)
        return []


################################4th diabetes_score###########################################
class ActionFourthdiabetesscoring(Action):
    def name(self) -> Text:
        return "Fourth_diabetes_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(diabetes_question_post(userId, 3, tracker.get_slot("diabetesAnswer"), age,"Diabetes", i2))
        # global qid
        # global question
        # global category
        qid2, question2 = Get_diabetes_Question(3)
        buttons = [
            {'payload': '/diabetesscoring_yes4{"diabetesAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/diabetesscoring_no4{"diabetesAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question2, buttons=buttons)
        # dispatcher.utter_message(text=" ", buttons=buttons)
        return []

######################################################################
class ActionFifthdiabetesscoring(Action):
    def name(self) -> Text:
        return "Fifth_diabetes_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(diabetes_question_post(userId, 4, tracker.get_slot("diabetesAnswer"), age,"Diabetes", i2))
        # global qid
        # global question
        # global category
        qid2, question2 = Get_diabetes_Question(4)
        buttons = [
            {'payload': '/diabetesscoring_yes5{"diabetesAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/diabetesscoring_no5{"diabetesAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question2, buttons=buttons)
        # dispatcher.utter_message(text=" ", buttons=buttons)
        return []



################################5th diabetes_score###########################################
class ActionSixthdiabetesscoring(Action):
    def name(self) -> Text:
        return "Sixth_diabetes_score_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(diabetes_question_post(userId, 5, tracker.get_slot("diabetesAnswer"), age,"Diabetes", i2))
        concatination = get_diabetes_scoring(userId)
        buttons = [
            {'payload': "/Retake_assessment_first2", 'title': "Retake Assessment"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(
            text="**Your diabetes is: **" + concatination + ' - We suggest to Consult with General Physician for better clarity')
        dispatcher.utter_message(text="Take a quiz and get your free diabetes health assessment", buttons=buttons)

        return []


#########################################################depression_retake_assisment####################################


class ActionZerodepressionscoringretake(Action):
    def name(self) -> Text:
        return "Zero_depression_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # global userId
        global lifestyle_score
        userId=get_userid(number)
        depression_score = get_depression_scoring(userId)
        if depression_score == 'No':
            buttons = [
            {'payload': "/take_assessment1", 'title': "Take Assessment"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
            ]
            dispatcher.utter_message(text="😮 You have not taken the personalized depression assessment yet. Please get your free depression  assessment and it will be completed in no time.")
            dispatcher.utter_message(text="Take a quiz and get your free  depression assessment", buttons=buttons)
            return []
        else:
            print(lifestyle_score, "sdfsdf")
            buttons = [
                {'payload': "/Retake_assessment_first", 'title': "Retake Assessment"},
                {'payload': "/assessment_options", 'title': "Go Back"},
                {'payload': "/MainMenu", 'title': "Main Menu"}
            ]
            dispatcher.utter_message(text="Take a quiz and get your free depression assessment", buttons=buttons)
            return []
class Actiondepressionscoringretake(Action):
    def name(self) -> Text:
        return "First_depression_score_assessmentretake"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global userId
        message = get_userid(tracker.get_slot('MobileNumber'))
        # print(message)
        userId = message
        print(userId)
        global age
        age = tracker.get_slot("Age")
        global qid1
        # global interaction_id1
        global i1
        interaction_id2 = depression_get_interaction(userId)
        i1 = interaction_id2
        print(i1)
        qid1, question1 = Get_depression_Question(0)
        # print(question1)
        # print(qid1)
        buttons = [
            {'payload': '/depressscoring_yes1retake{"depressionAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/depressscoring_no1retake{"depressionAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question1, buttons=buttons)
        return []


##################################2nd depression_score##############################################

class ActionSeconddepressionscoringretake(Action):
    def name(self) -> Text:
        return "Second_depression_score_assessmentretake"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(depression_question_post(userId, 1, tracker.get_slot("depressionAnswer"),age, "Depression", i1))

        # global qid
        # global question
        # global category
        qid1, question1 = Get_depression_Question(1)
        # print(question1)
        buttons = [
            {'payload': '/depressscoring_yes2retake{"depressionAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/depressscoring_no2retake{"depressionAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question1, buttons=buttons)
        # dispatcher.utter_message(text=" ", buttons=buttons)
        # return [SlotSet("Answer", None)]
        return []


##################################3rd depression_score#######################################
class ActionThirddepressionscoringretake(Action):
    def name(self) -> Text:
        return "Third_depression_score_assessmentretake"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(depression_question_post(userId, 2, tracker.get_slot("depressionAnswer"), age,"Depression", i1))

        # global qid
        # global question
        # global category
        qid1, question1 = Get_depression_Question(2)
        buttons = [
            {'payload': '/depressscoring_yes3retake{"depressionAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/depressscoring_no3retake{"depressionAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question1, buttons=buttons)
        # dispatcher.utter_message(text=" ", buttons=buttons)
        return []


################################4th depression_score###########################################
class ActionFourthdepressionscoringretake(Action):
    def name(self) -> Text:
        return "Fourth_depression_score_assessmentretake"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(depression_question_post(userId, 3, tracker.get_slot("depressionAnswer"), age,"Depression", i1))
        # global qid
        # global question
        # global category
        qid1, question1 = Get_depression_Question(3)
        buttons = [
            {'payload': '/depressscoring_yes4retake{"depressionAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/depressscoring_no4retake{"depressionAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question1, buttons=buttons)
        # dispatcher.utter_message(text=" ", buttons=buttons)
        return []


class ActionFifthdepressionscoringretake(Action):
    def name(self) -> Text:
        return "Fifth_depression_score_assessmentretake"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(depression_question_post(userId, 4, tracker.get_slot("depressionAnswer"),age, "Depression", i1))
        concatination = get_depression_scoring(userId)
        buttons = [
            {'payload': "/Retake_assessment_first1", 'title': "Retake Assessment"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(
            text="**Your depression is: **" + concatination + ' - We suggest to Consult with General Physician for better clarity')
        dispatcher.utter_message(text="Take a quiz and get your free personalized health assessment", buttons=buttons)

        return []


#############################diabetes_retake#########################################

class ActionZerodiabetesscoringretake(Action):
    def name(self) -> Text:
        return "Zero_diabetes_score_assessmentretake"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # global userId
        # global lifestyle_score
        userId=get_userid(number)
        diabetes_score = get_depression_scoring(userId)
        if diabetes_score == 'No':
            buttons = [
            {'payload': "/take_assessment2", 'title': "Take Assessment"},
            # {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
            ]
            dispatcher.utter_message(text="😮 You have not taken the personalized daibetes assessment yet. Please get your free diabetes  assessment and it will be completed in no time.")
            dispatcher.utter_message(text="Take a quiz and get your free  diabetes assessment", buttons=buttons)
            return []
        else:
            # print(lifestyle_score, "sdfsdf")
            buttons = [
                {'payload': "/Retake_assessment_second", 'title': "Retake Assessment"},
                {'payload': "/assessment_options", 'title': "Go Back"},
                {'payload': "/MainMenu", 'title': "Main Menu"}
            ]
            dispatcher.utter_message(text="Take a quiz and get your free diabetes assessment", buttons=buttons)
            return []

class Actiondiabetesscoringretake(Action):
    def name(self) -> Text:
        return "First_diabetes_score_assessmentretake"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global userId
        message = get_userid(tracker.get_slot('MobileNumber'))
        # print(message)
        userId = message
        print(userId)
        global age
        age = tracker.get_slot("Age")
        # global qid1
        # global interaction_id1
        global i2
        interaction_id2 = diabetes_get_interaction(userId)
        i2 = interaction_id2
        print(i2)
        qid2, question2 = Get_diabetes_Question(0)
        # print(question1)
        # print(qid1)
        buttons = [
            {'payload': '/diabetesscoring_yes1retake{"diabetesAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/diabetesscoring_no1retake{"diabetesAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question2, buttons=buttons)
        return []


##################################2nd diabetes_score##############################################

class ActionSeconddiabetesscoringretake(Action):
    def name(self) -> Text:
        return "Second_diabetes_score_assessmentretake"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(diabetes_question_post(userId, 1, tracker.get_slot("diabetesAnswer"),age, "Diabetes", i2))

        # global qid
        # global question
        # global category
        qid2, question2 = Get_diabetes_Question(1)
        # print(question1)
        buttons = [
            {'payload': '/diabetesscoring_yes2retake{"diabetesAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/diabetesscoring_no2retake{"diabetesAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question2, buttons=buttons)

        return []


##################################3rd diabetes_score#######################################
class ActionThirddiabetesscoringretake(Action):
    def name(self) -> Text:
        return "Third_diabetes_score_assessmentretake"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(diabetes_question_post(userId, 2, tracker.get_slot("diabetesAnswer"), age,"Diabetes", i2))

        # global qid
        # global question
        # global category
        qid2, question2 = Get_diabetes_Question(2)
        buttons = [
            {'payload': '/diabetesscoring_yes3retake{"diabetesAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/diabetesscoring_no3retake{"diabetesAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question2, buttons=buttons)
        return []


################################4th diabetes_score###########################################
class ActionFourthdiabetesscoringretake(Action):
    def name(self) -> Text:
        return "Fourth_diabetes_score_assessmentretake"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(diabetes_question_post(userId, 3, tracker.get_slot("diabetesAnswer"), age,"Diabetes", i2))

        qid2, question2 = Get_diabetes_Question(3)
        buttons = [
            {'payload': '/diabetesscoring_yes4retake{"diabetesAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/diabetesscoring_no4retake{"diabetesAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question2, buttons=buttons)
        return []

######################################################################
class ActionFifthdiabetesscoringretake(Action):
    def name(self) -> Text:
        return "Fifth_diabetes_score_assessmentretake"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(diabetes_question_post(userId, 4, tracker.get_slot("diabetesAnswer"), age,"Diabetes", i2))
        # global qid
        # global question
        # global category
        qid2, question2 = Get_diabetes_Question(4)
        buttons = [
            {'payload': '/diabetesscoring_yes5retake{"diabetesAnswer":"Yes"}', 'title': "Yes"},
            {'payload': '/diabetesscoring_no5retake{"diabetesAnswer":"No"}', 'title': "No"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(text="Please think about the last seven days and answer 'Yes' or 'No' if you....")
        dispatcher.utter_message(text=question2, buttons=buttons)
        return []



################################4th diabetes_score###########################################
class ActionSixthdiabetesscoringretake(Action):
    def name(self) -> Text:
        return "Sixth_diabetes_score_assessmentretake"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(diabetes_question_post(userId, 5, tracker.get_slot("diabetesAnswer"), age,"Diabetes", i2))
        concatination = get_diabetes_scoring(userId)
        buttons = [
            {'payload': "/Retake_assessment_first2", 'title': "Retake Assessment"},
            {'payload': "/assessment_options", 'title': "Go Back"},
            {'payload': "/MainMenu", 'title': "Main Menu"}
        ]
        dispatcher.utter_message(
            text="**Your diabetes is: **" + concatination + ' - We suggest to Consult with General Physician for better clarity')
        dispatcher.utter_message(text="Take a quiz and get your free personalized health assessment", buttons=buttons)

        return []
