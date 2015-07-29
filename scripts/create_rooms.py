"""create_rooms.py

Usage:
    create_rooms <input> <url> [--from=<n>] [--alias=<alias_prefix>]
"""

from twisted.internet import defer, reactor
from docopt import docopt
import json
import treq
import sys
import yaml

results = {}

@defer.inlineCallbacks
def create_room(host, room_no, users, alias_prefix):
    create_url = "%s/_matrix/client/api/v1/createRoom" % (str(host),)
    access_token = "token_%d" % (users[0],)

    r = yield treq.post(
        create_url,
        params={"access_token": access_token},
        data=json.dumps({
            "preset": "public_chat",
            "room_alias_name": "%s_%d" % (alias_prefix, room_no,),
        }),
        headers={'Content-type': ['application/json']},
    )

    js = yield r.json()

    assert r.code == 200, "Status code: %d. %r" % (r.code, js)

    room_id = js["room_id"]

    results[room_no] = {
        "room_id": str(room_id),
        "alias": str(js["room_alias"]),
        "users": users,
    }

    join_url = "%s/_matrix/client/api/v1/join/%s" % (str(host), str(room_id))

    sys.stderr.write("Created %s (%s). Joing %d users.\n" % (room_no, room_id, len(users),))
    sys.stderr.flush()

    for user in users[1:]:
        r = yield treq.post(
            join_url,
            params={"access_token": "token_%d" % (user,)},
            headers={'Content-type': ['application/json']},
            data={},
        )

        yield r.json()

        assert(r.code == 200)

    sys.stderr.write("Finished room no. %d\n" % (room_no,))
    sys.stderr.flush()

@defer.inlineCallbacks
def drain(url, room_queue, alias_prefix):
    while room_queue:
        room, config = room_queue.pop()
        yield create_room(url, room, config["users"], alias_prefix)

@defer.inlineCallbacks
def start(url, rooms, alias_prefix):
    enum = list(enumerate(rooms))
    enum.reverse()

    yield defer.gatherResults([
        drain(url, enum, alias_prefix)
        for _ in range(5)
    ])

    reactor.stop()

if __name__ == "__main__":
    arguments = docopt(__doc__)

    input_file = arguments["<input>"]
    url = arguments["<url>"]
    from_room = int(arguments["--from"] or 0)
    alias_prefix = arguments["--alias"] or "room_"

    rooms = yaml.load(file(input_file))

    reactor.callWhenRunning(start, url, rooms, alias_prefix)

    reactor.run()

    print yaml.dump(results)
