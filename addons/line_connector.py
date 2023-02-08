from linebot import LineBotApi, WebhookParser
from linebot.exceptions import LineBotApiError
from rasa.core.channels.channel import InputChannel, UserMessage, OutputChannel
from typing import Dict, Text, Any, List, Optional, Callable, Awaitable,Union
from sanic import Blueprint, response
from sanic.response import HTTPResponse
from sanic.request import Request
import json
import logging


from linebot.models import (
    MessageEvent, 
    TextSendMessage, 
    FlexSendMessage, 
    BubbleContainer,
    ImageComponent,
    URIAction,
    BotInfo)

logger = logging.getLogger(__name__)

class Line:
    """Implement a line to parse incoming webhooks and send msgs."""

    @classmethod
    def name(cls) -> Text:
        return "line"

    def __init__(
        self,
        access_token: Text,
        on_new_message: Callable[[UserMessage], Awaitable[Any]],
    ) -> None:

        self.on_new_message = on_new_message
        self.client = LineBotApi(access_token)
        self.last_message: Dict[Text, Any] = {}
        self.access_token = access_token
    
    def get_user_id(self) -> Text:
        return self.last_message.source.sender_id

    async def handle(self, event: MessageEvent, metadata: Optional[Dict[Text, Any]]) -> None:
        self.last_message = event
        return await self.message(event, metadata)

    @staticmethod
    def _is_user_message(event: MessageEvent) -> bool:
        """Check if the message is a message from the user"""
        logger.debug(f"souce type:{type(event)}")
        return (event.source.type == "user")

    async def message(
        self, event: MessageEvent, metadata: Optional[Dict[Text, Any]]
    ) -> None:
        """Handle an incoming event from the fb webhook."""

        # quick reply and user message both share 'text' attribute
        # so quick reply should be checked first
        if self._is_user_message(event):
            text = event.message.text     
        else:
            logger.warning(
                "Received a message from facebook that we can not "
                f"handle. Event: {event}"
            )
            return  

        await self._handle_user_message(event,text, self.get_user_id(), metadata)
    
    async def _handle_user_message(
        self, event: MessageEvent, text: Text, sender_id: Text, metadata: Optional[Dict[Text, Any]]
    ) -> None:
        """Pass on the text to the dialogue engine for processing."""

        out_channel = LineConnectorOutput(self.access_token,event)
        
        user_msg = UserMessage(
            text, out_channel, sender_id, input_channel=self.name(), metadata=metadata
        )
        # test send text to line
        # await out_channel.send_text_message(sender_id, text)
        try:
            await self.on_new_message(user_msg)
        except Exception:
            logger.exception(
                "Exception when trying to handle webhook for facebook message."
            )
            pass
       

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
    
    async def send_to_line(
            self,
            payload_object: [TextSendMessage,
                             FlexSendMessage],
            **kwargs: Any) -> None:
        try:
            if self.reply_token:
                self.line_client.reply_message(
                    self.reply_token,
                    messages=payload_object
                )
            else:
                self.line_client.push_message(to=self.sender_id,
                                              messages=payload_object)
        except LineBotApiError as e:
            logger.error(f"Line Error: {e.error.message}")
            logger.error(f"Payload: {payload_object}")
            if e.status_code == 400 or e.error.message == 'Invalid reply token, trying to push message.':
                logger.info('Pushing Message...')
                self.line_client.push_message(to=self.sender_id,
                                              messages=payload_object)

    async def send_text_message(
            self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        try:
            json_converted = json.loads(text)
            print("json_converted:",json_converted)
            
            if json_converted.get('type') == 'flex':
                await self.send_to_line(
                    FlexSendMessage(
                        alt_text=json_converted.get('alt_text'),
                        contents=json_converted.get('contens')
                    ))
            else:
                await self.send_to_line(TextSendMessage(text=text))
        except ValueError:
            message_object = TextSendMessage(text=text)
            await self.send_to_line(message_object)


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
                    logger.debug(f"Web Hook Receive:{events}")
                    for event in events:
                        line = Line(self.access_token, on_new_message)
                        metadata = self.get_metadata(request)
                        await line.handle(event, metadata)
                        # line_output = LineConnectorOutput(self.access_token, event)
                        # if isinstance(event, MessageEvent):
                        #     metadata = self.get_metadata(request)
                        #     msg = event.message
                        #     user_id = event.source.user_id
                        #     if isinstance(msg, TextMessage):
                        #             # Send to RASA
                        #             await on_new_message(UserMessage(
                        #                 text=msg.text,
                        #                 output_channel=line_output,
                        #                 input_channel=self.name(),
                        #                 sender_id=user_id,
                        #                 metadata=metadata
                        #             ))
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