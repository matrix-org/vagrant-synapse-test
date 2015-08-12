"""send_messages.py

Usage:
    send_messages <input> <url> --interval=<n> --concurrent=<n>
"""

from docopt import docopt
from twisted.internet import defer, reactor
import json
import random
import treq
import yaml
import time


WINDOW = []


def sleep(seconds):
    d = defer.Deferred()
    reactor.callLater(seconds, d.callback, seconds)
    return d


def get_time():
    return int(time.time() * 1000)


@defer.inlineCallbacks
def send_messages(host, user_to_rooms, interval):
    while True:
        user, rooms = random.choice(user_to_rooms.items())
        room = random.choice(rooms)
        room_id = room["room_id"]

        start = get_time()

        r = yield treq.post(
            "%s/_matrix/client/api/v1/rooms/%s/send/m.room.message" % (host, str(room_id)),
            params={
                "access_token": "token_%d" % (user,),
            },
            data=json.dumps({
                "msgtype": "m.text",
                "body": "Hello",
            }),
            headers={'Content-Type': ['application/json']}
        )

        yield r.json()

        end = get_time()

        assert r.code == 200

        WINDOW.append(end)
        while WINDOW and start - WINDOW[0] > 2000:
            WINDOW.pop(0)

        if len(WINDOW) > 1:
            rate = len(WINDOW) * 1000./(WINDOW[-1] - WINDOW[0])
        else:
            rate = 0

        print "Sent from %d into %s. Rate: %.2f/s. Latency: %dms" % (user, room["alias"], rate, end-start)

        yield sleep(interval * random.uniform(0.7, 1.3) / 1000.)


@defer.inlineCallbacks
def start(url, rooms, interval, concurrent):
    user_to_rooms = {}

    for room in rooms.values():
        for user in room["users"]:
            user_to_rooms.setdefault(user, []).append(room)

    ds = []
    for _ in range(concurrent):
        d = send_messages(url, user_to_rooms, interval)
        ds.append(d)
        yield sleep(0.2)

    yield defer.gatherResults(ds)
    reactor.stop()

if __name__ == "__main__":
    arguments = docopt(__doc__)

    input_file = arguments["<input>"]
    url = arguments["<url>"]

    interval = float(arguments["--interval"])
    concurrent = int(arguments["--concurrent"])

    rooms = yaml.load(file(input_file))

    reactor.callWhenRunning(start, url, rooms, interval, concurrent)
    reactor.run()
