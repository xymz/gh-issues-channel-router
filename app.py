import json
import requests

from flask import Flask, request, jsonify

app = Flask(__name__)
url = ('https://spoqa.slack.com/services/hooks/incoming-webhook'
       '?token=EqCiU0T2MCimJLsn30j7JUPF')


class GhEventHandler(object):

    _handler_map = {}

    def add_event(self, event):
        def decorator(handler):
            if event not in self._handler_map:
                self._handler_map[event] = handler

            def decorated_function(*args, **kwargs):
                return handler(*args, **kwargs)
            return decorated_function
        return decorator

    def handle(self):
        event = request.headers['X-GitHub-Event']
        if event in self._handler_map:
            data = json.loads(request.data)
            self._handler_map[event](data)


handler = GhEventHandler()


@handler.add_event("issue_comment")
def issue_comment(data):
    for label in data['issue']['labels']:
        payload = {
            "username": "github",
            "icon_emoji": ":octocat:",
            "channel": u"#{0}".format(label['name']),
            "text": u"#{0} @{1}: {2}\n<{3}>".format(
                data['issue']['number'],
                data['comment']['user']['login'],
                data['comment']['body'],
                data['comment']['html_url']
            )
        }
        requests.post(url, data=json.dumps(payload))


@handler.add_event("issues")
def issues(data):
    for label in data['issue']['labels']:
        payload = {
            "username": "github",
            "con_emoji": ":octocat:",
            "channel": u"#{0}".format(label['name']),
            "text": u"#{0} {1} by @{2}\n{3}\n<{4}>".format(
                data['issue']['number'],
                data['issue']['title'],
                data['issue']['user']['login'],
                data['issue']['body'],
                data['issue']['html_url']
            )
        }
        requests.post(url, data=json.dumps(payload))


@app.route('/', methods=['GET', 'POST'])
def index():
    handler.handle()
    return jsonify(result='success')

if __name__ == "__main__":
    app.run(debug=True)
