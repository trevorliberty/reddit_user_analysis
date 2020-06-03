from apis.praw import instantiate
"""
Link the apis together
"""


def processUser(username):
    user = instantiate(username)
    print(user)
