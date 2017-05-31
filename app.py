import os
import sys
import json
import winuall

import requests
from flask import Flask, request

app = Flask(__name__)



@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    
    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing
    if data["object"] == "page":
        
        for entry in data["entry"]:
            
            for messaging_event in entry["messaging"]:
                
                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

                    try:
                        message_text = messaging_event["message"]["text"]  # the message's text
                        
                        soln = winuall.send(message_text)

                        if soln != []:

                            a_msg(sender_id, "Hey I got you some links!! Why not check them?")

                            for i in soln:
                                if soln.index(i) == len(soln) -1:
                                    send_message(sender_id, str(i['slug']))
                                else:
                                    a_msg(sender_id, str(i['slug']))
                        else:
                            send_message(sender_id, "I am sorry. I am unable to find links. Why not visit winuall.com!!")

                    except KeyError:
                        send_message(sender_id, "Hey, please text me to get proper replies.")

                    break
                    

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    message_text = messaging_event['postback']['payload']
                    sender_id = messaging_event["sender"]["id"]
                    send_message(sender_id, message_text)

    return "ok", 200


def a_msg(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
    "attachment":{
      "type":"template",
      "payload":{
        "template_type":"button",
        "text":message_text,
        "buttons":[
          {
            "type":"postback",
            "title":"Ask a Question!!",
            "payload":"Type your question, keyword or phrase."
          },
          {
            "type":"web_url",
            "url":"https://www.winuall.com/",
            "title":"Go to Winuall!!"
          }
        ]
      }
    }
  }
    })

    
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
  
def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
##    buttons()
    app.run(debug=True)
