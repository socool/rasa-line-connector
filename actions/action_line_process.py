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

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        covid_resources = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [{
                    "title": "MBMC",
                    "subtitle": "FIND BED, SAVE LIFE.",
                    "image_url": "static/hospital-beds-application.jpg",
                    "buttons": [{
                        "title": "Hospital Beds Availability",
                        "url": "https://www.covidbedmbmc.in/",
                        "type": "web_url"
                    },
                        {
                            "title": "MBMC",
                            "type": "postback",
                            "payload": "/affirm"
                        }
                    ]
                },
                    {
                        "title": "COVID.ARMY",
                        "subtitle": "OUR NATION, SAVE NATION.",
                        "image_url": "static/oxygen-cylinder-55-cft-500x554-500x500.jpg",
                        "buttons": [{
                            "title": "RESOURCES AVAILABILITY",
                            "url": "https://covid.army/",
                            "type": "web_url"
                        },
                            {
                                "title": "COVID ARMY",
                                "type": "postback",
                                "payload": "/deny"
                            }
                        ]
                    },
                    {
                        "title": "Innovate Youself",
                        "subtitle": "Get It, Make it.",
                        "image_url": "static/test.jpg",
                        "buttons": [{
                            "title": "Innovate Yourself",
                            "url": "https://www.innovationyourself.com/",
                            "type": "web_url"
                        },
                            {
                                "title": "Innovate Yourself",
                                "type": "postback",
                                "payload": "/greet"
                            }
                        ]
                    },
                    {
                        "title": "RASA CHATBOT",
                        "subtitle": "Conversational AI",
                        "image_url": "static/rasa.png",
                        "buttons": [{
                            "title": "Rasa",
                            "url": "https://www.rasa.com",
                            "type": "web_url"
                        },
                            {
                                "title": "Rasa Chatbot",
                                "type": "postback",
                                "payload": "/greet"
                            }
                        ]
                    }
                ]
            }
        }
        
        print(next(tracker.get_latest_entity_values("message_type"), None))

        entities = tracker.latest_message["entities"]
        for e in entities:
            if e["entity"] == "message_type":
                slot_value = e["value"]
                logger.debug(f"slot_value:{slot_value}")
                dispatcher.utter_message(response = "utter_slots_line_values")
                return [SlotSet("message_type", slot_value)]
        
        # print("tracker:",tracker)
        # print("MESSAGE_TYPE:",message_type)
        # dispatcher.utter_message(attachment=covid_resources)
        # return []