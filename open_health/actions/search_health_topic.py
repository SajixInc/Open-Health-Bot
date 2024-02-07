from typing import Any, Text, Dict, List
from main import get_details
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import Restarted, EventType, SlotSet, FollowupAction

class ActionFifthdepressionscoring(Action):
    def name(self) -> Text:
        return "get_info_about_your_query"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
    
        message= get_details(tracker.get_slot("Query")) 
        # print(message, "this is in actions file")
        dispatcher.utter_message(text=message)   
        return [FollowupAction("slot_ask_health_query_form"), SlotSet("Query", None)]