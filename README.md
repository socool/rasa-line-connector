### RASA Line Connector

folk from
https://github.com/jakkritz/line_rasa_connector

### Create your credential file contain
```
rasa:
  url: "http://localhost:5002/api"

addons.line_connector.LineConnectorInput:
  app_secret: "[APP_SECRET]"
  access_token: "ACCESS_TOKEN"
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