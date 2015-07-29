"""create_room_distribution

Usage:
    create_room_distribution --num-rooms=<n> --num-users=<n> --largest-room=<n> --room-dist=<distribution> --user-dist=<distribution>
"""

from docopt import docopt
import random
import yaml


if __name__ == '__main__':
    arguments = docopt(__doc__)

    room_dist_split = arguments["--room-dist"].split(",")
    room_dist_args = [float(a) for a in room_dist_split[1:]]
    room_dist = getattr(random, room_dist_split[0])

    user_dist_split = arguments["--user-dist"].split(",")
    user_dist_args = [float(a) for a in user_dist_split[1:]]
    user_dist = getattr(random, user_dist_split[0])

    users = int(arguments["--num-users"])
    num_rooms = int(arguments["--num-rooms"])
    largest_room = int(arguments["--largest-room"])

    result = [{"users": set()} for _ in xrange(num_rooms)]


    room_to_num_users = [2 for _ in xrange(num_rooms)]

    while max(room_to_num_users) < largest_room:
        r = -1
        while not 0 <= r < num_rooms or room_to_num_users[r] == int(users/2):
            r = int(round(room_dist(*room_dist_args)))

        room_to_num_users[r] += 1

    def get_user_for_room(room):
        r = -1
        while (not 0 <= r < users) or r in result[room]["users"]:
            r = int(round(user_dist(*user_dist_args)))
        return r

    for room, n in enumerate(room_to_num_users):
        print "Room %d with %d members." % (room, n,)
        for _ in xrange(n):
            user = get_user_for_room(room)
            result[room]["users"].add(user)
        print "Room %d done." % (room,)

    print yaml.dump([
        {"users": list(r["users"])}
        for r in result
        if len(r["users"]) > 1
    ])
