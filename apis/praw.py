import praw

reddit = praw.Reddit(client_id="zcpKwNZG8DvpMg",
                     client_secret="urYURxN7NEao8TlE-gB_33f3ANE", user_agent="trevor")

weirdo = reddit.redditor(name="spez")

comments = []

for comment in weirdo.comments.new(limit=None):
    comments.append(comment.body)

print(comments[0])
