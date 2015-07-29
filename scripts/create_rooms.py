"""create_rooms.py

Usage:
    create_rooms <input> <url> [--from=<n>]
"""

from docopt import docopt
import json
import requests
import yaml


def create_room(host, room_no, users):
    create_url = "%s/_matrix/client/api/v1/createRoom" % (host,)
    access_token = "token_%d" % (users[0],)

    r = requests.post(
        create_url,
        params={"access_token": access_token},
        data=json.dumps({
            "preset": "public_chat",
            "room_alias_name": "room_%d" % (room_no,),
        }),
        headers={'Content-type': 'application/json'},
    )

    assert r.status_code == 200, "Status code: %d. %r" % (r.status_code, r.json())

    room_id = r.json()["room_id"]

    join_url = "%s/_matrix/client/api/v1/join/%s" % (host, room_id)

    for user in users[1:]:
        r = requests.post(
            join_url,
            params={"access_token": "token_%d" % (user,)},
            data={},
        )

        assert(r.status_code == 200)

    print "Finished room no. %d" % (room_no,)


if __name__ == "__main__":
    arguments = docopt(__doc__)

    input_file = arguments["<input>"]
    url = arguments["<url>"]
    from_room = int(arguments.get("--from", 0))

    rooms = yaml.load(file(input_file))

    for room, conf in list(enumerate(rooms))[from_room:]:
        create_room(url, room, conf["users"])

