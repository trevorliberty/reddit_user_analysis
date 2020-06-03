import praw

reddit = praw.Reddit(client_id="zcpKwNZG8DvpMg",
                     client_secret="urYURxN7NEao8TlE-gB_33f3ANE", user_agent="trevor")


def instantiate(username):
    return getNewComments(retrieveUser(username))


def retrieveUser(username):
    return reddit.redditor(name=username)


def getNewComments(user):
    comments = []
    for comment in user.comments.new(limit=5):
        parent = comment.parent()
        if comment.is_root:
            par = {
                'body': parent.selftext,
                'score': parent.score,
                'username': parent.author
            }
        else:
            par = {
                'body': parent.body,
                'score': parent.score,
                'username': parent.author
            }
        commentObj = {
            'body': comment.body,
            'parent': par,
            'subreddit': comment.subreddit,
            'score': comment.score
        }
        comments.append(commentObj)

    return comments
