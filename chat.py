import requests
import os
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# export SLACK_BOT_TOKEN=''
# export SLACK_CHANNEL=''
# export SLACK_APP_TOKEN=''
# export CHATGPT_BACKEND_URL=''


app = App(token=os.environ["SLACK_BOT_TOKEN"])
response = None

def make_post_request(ack, payload, event):
    url = os.environ["CHATGPT_BACKEND_URL"]
    response = requests.post(url, json=payload)
    botresponse = response.content.strip().decode("utf-8")
    data = json.loads(botresponse)
    jsonData = data["message"]
    print (jsonData)
    handle_chat(ack, jsonData, event)

def handle_response(ack, payload):
    global response
    response = payload.message.text
    print("Received response: ", response)
    ack("Thanks for the response!")
    payload = {response}
    make_post_request(ack, payload)

@app.command("/ai")
def handle_example(ack, command):
    user_id = command["user_id"]
    ack(f"Hi, <@{user_id}>, Please provide a response: ")
    app.action("handle_response")

def handle_chat(ack, botresponse, event):
    if event["channel"] == "general":
        # app.client.chat_postMessage(channel="#general", text=botresponse)
        app.client.chat_postMessage(channel=os.environ["SLACK_CHANNEL"], text=botresponse)
    elif event["channel_type"] == "im":
        app.client.chat_postMessage(channel=event["channel"], text=botresponse)
    else:
        app.client.chat_postMessage(channel=event["channel"], text=botresponse)

@app.event("app_mention")
@app.event("message")
def handle_message(ack, event):
    message = event["text"]
    message_text = message.split("<@")[0]
    ack("You said: " + message_text)
    payload = {"message": message_text}
    make_post_request(ack, payload, event)

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
