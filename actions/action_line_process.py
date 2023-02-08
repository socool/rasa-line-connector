# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

from rasa_sdk.events import (
    ActionExecuted,
    SlotSet,
)

logger = logging.getLogger(__name__)

class ActionLineProcess(Action):

    def name(self) -> Text:
        return "action_line_process"

    def run(
            self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message_type = tracker.get_slot("message_type")[0]
        entities = tracker.latest_message['entities']
        print("message_type:",message_type, " entities:",entities)
        if message_type == "flex":
            # dispatcher.utter_message(response = f"utter_slots_line_{message_type}")
            dispatcher.utter_message(json_message={"flex":True, "response":"utter_slots_line_flex"})
        dispatcher.utter_message(response = f"utter_slots_line")
