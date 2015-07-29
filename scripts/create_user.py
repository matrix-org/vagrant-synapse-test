"""create_user

Usage:
    create_user <from> <to>
"""

from docopt import docopt

CREATE_USER_SQL = "INSERT INTO users (name, admin) VALUES ('@testuser_{0}:localhost', 0);"
CREATE_ACCESS_TOKEN_SQL = "INSERT INTO access_tokens (id, user_id, token) VALUES ({0}, '@testuser_{0}:localhost', 'token_{0}');"
CREATE_PROFILE = "INSERT INTO profiles (user_id) VALUES ('testuser_{0}');"
CREATE_PRESENCE = "INSERT INTO presence (user_id) VALUES ('testuser_{0}');"

def print_sql(from_user, to_user):
    print "BEGIN;"
    for i in range(from_user, to_user + 1):
        print CREATE_USER_SQL.format(i)
        print CREATE_ACCESS_TOKEN_SQL.format(i)
        print CREATE_PROFILE.format(i)
        print CREATE_PRESENCE.format(i)
    print "COMMIT;"

if __name__ == '__main__':
    arguments = docopt(__doc__)
    print_sql(int(arguments["<from>"]), int(arguments["<to>"]))
