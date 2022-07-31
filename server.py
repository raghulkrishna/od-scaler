import os
import re
import logging

from flask import Flask, make_response, request
from slackify import OK, Slack, Slackify, async_task
from flask_httpauth import HTTPBasicAuth as flask_auth
from requests.auth import HTTPBasicAuth
import pyee

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from od_downscaler import scaler
from od_downscaler.block_generator import kube_scaler_block, namespace_block
from od_downscaler.helper import get_all_namespaces

BOT_USER_ID = os.environ["BOT_USER_ID"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
user = os.environ['BASIC_AUTH_USER']
pw = os.environ['BASIC_AUTH_PASSWORD']


auth = flask_auth()
emitter = pyee.BaseEventEmitter()

users = {
    user: generate_password_hash(pw)
}
emitter = pyee.BaseEventEmitter()
auth = flask_auth()
app = Flask(__name__)
cli = Slack(SLACK_BOT_TOKEN)



app.route("/slack/events", methods=["POST"])

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

@app.route('/')
@auth.login_required
def index():
    return 'Slackify Home'


app.route('/slack/events',methods = ['POST'])
@auth.login_required
def events():
    event_data = request.get_json()
    # Respond to slack challenge to enable our endpoint as an event receiver
    if "challenge" in event_data:
        return make_response(
            event_data.get("challenge"), 200, {"Content-Type": "application/json"}
        )
    return make_response(400, {"Content-Type": "application/json"})

    if "event" in event_data:
        event_type = event_data["event"]["type"]
        print(event_type)
        self.emitter.emit(event_type, event_data)
        return make_response("", 200)

slackify = Slackify(app=app)

@slackify.event("app_mention")
def app_mention(payload):
    # print(payload)
    """Adds the same reaction as the user"""
    event = payload["event"]
    text = event["text"].replace(f"<@{BOT_USER_ID}>", "")
    all_namespaces = get_all_namespaces()
    if "upscale" in text:
        cli.chat_postMessage(
            channel=event["channel"],
            user_id=BOT_USER_ID,
            blocks=namespace_block(all_namespaces, text),
        )
    else:
        cli.chat_postMessage(
            channel=event["channel"],
            user_id=BOT_USER_ID,
            blocks=namespace_block(all_namespaces, text),
        )
    return OK


@slackify.action("multi_static_select-action")
@auth.login_required
def multi_static_select(payload):
    print(payload.keys())
    print(payload["actions"][0]["selected_options"])
    namespaces = [i["text"]["text"] for i in payload["actions"][0]["selected_options"]]
    print(payload["message"]["blocks"][0]["text"]["text"])
    scale_conf = payload["message"]["blocks"][0]["text"]["text"]
    cli.chat_postMessage(
        channel=payload["channel"]["id"],
        user_id=BOT_USER_ID,
        blocks=kube_scaler_block(namespaces, scale_conf),
    )
    cli.chat_delete(
        channel=payload["channel"]["id"], ts=payload["container"]["message_ts"]
    )
    return OK


@async_task
def workload(namespace_list, scale_conf, downscaler_exclude, min_replica):
    if "down" in scale_conf:
        print("Down scale started")
        scale_down = scaler.DownScaler(
            include_namespaces=namespace_list,
            exclude_namespaces=["kube-system"],
            downscaler_exclude=downscaler_exclude,
            min_replica=min_replica,
        )
        scale_down.down_scaler()
    else:
        print("Up scale started")
        scale_up = scaler.UpScaler(
            include_namespaces=namespace_list,
            exclude_namespaces=["kube-system"],
            downscaler_exclude=downscaler_exclude,
        )
        scale_up.up_scaler()
    return "Success"


@slackify.action("yes")
@slackify.action("no")
@auth.login_required
def yes(payload):
    scale_conf = payload["message"]["blocks"][0]["text"]["text"]
    namespaces = payload["actions"][0]["value"]
    downscaler_exclude_action = payload["actions"][0]["text"]["text"]
    downscaler_exclude = bool(downscaler_exclude_action == "yes")
    #     downscaler_exclude = True
    # else:
    #     downscaler_exclude = False
    print(scale_conf)
    if "replica" in scale_conf:
        min_replica = int(re.findall(r"\d", scale_conf)[0])
    else:
        min_replica = 0
    print(min_replica)
    print(downscaler_exclude)
    namespace_list = namespaces.split("****")
    workload(namespace_list, scale_conf, downscaler_exclude, min_replica)
    text = scale_conf + " :" + " ,".join(namespace_list)
    cli.chat_postMessage(
        channel=payload["channel"]["id"], user_id=BOT_USER_ID, text=text
    )
    cli.chat_delete(
        channel=payload["channel"]["id"], ts=payload["container"]["message_ts"]
    )
    return OK


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=False)
