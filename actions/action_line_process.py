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
            dispatcher.utter_message(response="utter_slots_line_flex")
        elif message_type == "sticker":
            dispatcher.utter_message(response="utter_slots_line_sticker")
        elif message_type == "image":
            dispatcher.utter_message(response="utter_slots_line_image")
        elif message_type == "video":
            dispatcher.utter_message(response="utter_slots_line_video")
        elif message_type == "audio":
            dispatcher.utter_message(response="utter_slots_line_audio")
        elif message_type == "location":
            dispatcher.utter_message(response="utter_slots_line_location")
        elif message_type == "text_with_quickreply":
            dispatcher.utter_message(response="utter_slots_line_text_with_quickreply")
        elif message_type == "text_with_emoji":
            dispatcher.utter_message(response="utter_slots_line_text_with_emoji")
        elif message_type == "template":
            dispatcher.utter_message(response="utter_slots_line_template")
        elif message_type == "template_with_button":
            dispatcher.utter_message(response="utter_slots_line_template_with_button")
        elif message_type == "template_with_confirm":
            dispatcher.utter_message(response="utter_slots_line_template_with_confirm")
        else:
            dispatcher.utter_message(response = f"utter_slots_line")
