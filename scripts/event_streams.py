"""event_streams.py

Usage:
    event_streams <number_user> <url>
"""

from docopt import docopt
from twisted.internet import defer, reactor
import treq
import time
import random


def get_time():
    return int(time.time() * 1000)


def sleep(seconds):
    d = defer.Deferred()
    reactor.callLater(seconds, d.callback, seconds)
    return d


@defer.inlineCallbacks
def start_streaming(host, user):
    print "Initial Sync for testuser_%d" % (user,)

    r = yield treq.get(
        "%s/_matrix/client/api/v1/events" % (host,),
        params={
            "access_token": "token_%d" % (user,),
            "timeout": "0",
        },
    )

    initialSync = yield r.json()

    assert r.code == 200, "InitialSync %d. %r" % (r.code, initialSync,)

    from_token = initialSync["end"]

    yield sleep(5 * random.random())  # This is to even requests out.

    print "Starting event stream for testuser_%d" % (user,)

    while True:
        try:
            start = get_time()
            r = yield treq.get(
                "%s/_matrix/client/api/v1/events" % (host,),
                params={
                    "access_token": "token_%d" % (user,),
                    "from": from_token,
                    "timeout": "30000",
                },
            )
            end = get_time()

            stream = yield r.json()

            assert r.code == 200, "Event stream %d. %r" % (r.code, stream,)

            if end - start > 35000:
                print "Took more than %ds to get response" % ((end-start)/1000,)

            from_token = stream["end"]
        except Exception as e:
            print "Failed to do event stream for %d: %s" % (user, e)
            yield sleep(5)


@defer.inlineCallbacks
def start(url, users):

    sleep_ts = max(30./users, 0.5)
    for user in xrange(users):
        start_streaming(url, user)
#        yield sleep(sleep_ts)

    #print "All initial syncs started"
    yield
    defer.returnValue(None)


if __name__ == "__main__":
    args = docopt(__doc__)

    users = int(args["<number_user>"])
    url = args["<url>"]

    reactor.callWhenRunning(start, url, users)
    reactor.run()
