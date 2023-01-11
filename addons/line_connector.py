from linebot import LineBotApi, WebhookParser
from rasa.core.channels.channel import InputChannel, UserMessage, OutputChannel
from typing import Dict, Text, Any, List, Optional, Callable, Awaitable
from sanic import Blueprint, response
from sanic.response import HTTPResponse
from sanic.request import Request
import json

from linebot.models import (
    MessageEvent, TextMessage, BotInfo)

class LineConnectorOutput(OutputChannel):
    """Output channel for Line."""

    @classmethod
    def name(cls) -> Text:
        return "line"

    def __init__(self,
                 channel_access_token: Optional[Text],
                 event: Any
                 ) -> None:
        self.line_client = LineBotApi(channel_access_token)
        self.reply_token = event.reply_token
        self.sender_id = event.source.user_id
        super().__init__()

class LineConnectorInput(InputChannel):
    """Line input channel"""

    @classmethod
    def name(cls) -> Text:
        return "line"

    @classmethod
    def from_credentials(cls, credentials: Optional[Dict[Text, Any]]) -> InputChannel:
        if not credentials:
            cls.raise_missing_credentials_exception()

        return cls(
            credentials.get("app_secret"),
            credentials.get("access_token"),
        )

    def __init__(
            self,
            app_secret: Text,
            access_token: Text,
    ) -> None:
        self.app_secret = app_secret
        self.access_token = access_token

    def blueprint(
            self, on_new_message: Callable[[UserMessage], Awaitable[Any]]
    ) -> Blueprint:
        """ Send line payload to call back url: https://{HOST}/webhooks/line/callback"""

        line_webhook = Blueprint("line_webhook", __name__)
        parser = self.get_line_message_parser()

        @line_webhook.route("/", methods=["GET"])
        async def health(_: Request) -> HTTPResponse:
            return response.json({"status": "ok"})
        
        @line_webhook.route("/bot/info", methods=["GET"])
        async def info(_: Request) -> HTTPResponse:
            bot_info = LineBotApi(self.access_token).get_bot_info()
            return response.json(json.dumps(bot_info,cls=BotInfoEncoder))

        @line_webhook.route("/callback", methods=["POST"])
        async def message(request: Request) -> Any:
            if request.method == "POST":
                # CHECK IF FROM LINE APP
                signature = request.headers.get('X-Line-Signature', None)
                if signature:
                    body = request.body.decode('utf-8')
                    events = parser.parse(body, signature)
                    for event in events:
                        line_output = LineConnectorOutput(self.access_token, event)
                        if isinstance(event, MessageEvent):
                            metadata = self.get_metadata(request)
                            msg = event.message
                            reply_token = event.reply_token
                            user_id = event.source.user_id
                            if isinstance(msg, TextMessage):
                                    # Send to RASA
                                    await on_new_message(UserMessage(
                                        text=msg.text,
                                        output_channel=line_output,
                                        input_channel=self.name(),
                                        sender_id=user_id,
                                        metadata=metadata
                                    ))
                    return response.json({"status": "Line Webhook success"})

                # FROM CURL / EXTERNAL
                else:
                    return response.json(request.json)


        return line_webhook

    def get_line_message_parser(self) -> WebhookParser:
        """Loads Line WebhookParser"""
        parser = WebhookParser(self.app_secret)
        return parser

class BotInfoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BotInfo):
            # Return a serializable version of the object
            return obj.__dict__
        return super().default(obj)