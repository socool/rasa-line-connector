### RASA Line Connector

Commmit pattern
- feat (✨): new feature
- fix (🐛): fix some bug
- refactor (📦): code refactor
- style (💎): code style
- test (🚨): add/edit test case
- perf (🚀): performance tuning
- build (🔨): build script
- ci (⚙️): cd/ci
- docs (📚): add/edit document

folk from
https://github.com/jakkritz/line_rasa_connector

<a name="line-app-setup"></a>
### Line app setup

- [Create an app](https://developers.line.biz/en/services/messaging-api/)
- Add the Messaging API app
- Install ngrok
- Enable line webhook
- Setting webhook url in (https://developers.line.biz/en/docs/messaging-api/building-bot/#set-up-bot-on-line-developers-console)

### Create your credential file contain
credentials.yml
```
rasa:
  url: "http://localhost:5002/api"

addons.line_connector.LineConnectorInput:
  app_secret: "[APP_SECRET]"
  access_token: "[ACCESS_TOKEN]"
```

### Train your models
```
rasa train
```

### Run RASA server
commands for run server to test callback
```
rasa run -m models --credentials credentials.yml --enable-api
```

### Run Action server
for test line component
```
rasa run actions
```

run with debug mode
```
rasa run -m models --credentials credentials.yml --enable-api --cors "*" --debug
```

using this curl for test line webhook payload
```
curl --request POST \
     --url http://localhost:5005/webhooks/line/callback \
     --header 'Content-Type: application/json' \
     --data '{
            "sender": "test_user",
            "message": "Hi there!",
            "metadata": {}
          }'
```

check bot info using this command
```
curl --request GET \
     --url http://localhost:5005/webhooks/line/bot/info
```