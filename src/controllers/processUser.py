from apis.praw import instantiate
from collections import Counter
# from apis.gcloud import extactSentiment
"""
Link the apis together
"""

import random
# random.uniform is being used. we will need to patch in the actual api that analyzes sentiments
# pull in the ids of each  comment


class Parent():
    def __init__(self, score=0, contents=None, sentiment=0.0):
        self.score = score
        self.contents = contents
        self.sentiment = sentiment

    def display(self):
        print('*****')
        print(f'Score: {str(self.score)}')
        print(f'Contents: {self.contents}')
        print(f'Sentiment: {str(self.sentiment)}')
        print('*****')


class Comment():
    def __init__(self, score=0, contents=None, subreddit=None, sentiment=0.0, parent=None):
        self.score = score
        self.contents = contents
        self.subreddit = subreddit
        self.sentiment = sentiment
        self.parent = parent

    def display(self):
        print('-----')
        print(f'Score: {str(self.score)}')
        print(f'Contents: {self.contents}')
        print(f'Sentiment: {str(self.sentiment)}')
        print(f'Subreddit: {self.subreddit}')
        print(f'ParentComment')
        self.parent.display()
        print('-----')


class User():
    def __init__(self):
        self.karma = 0
        self.sentimentAverage = 0.0
        self.sentimentHighestComment = Comment()
        self.sentimentLowestComment = Comment()
        self.lowestRatedComment = Comment()
        self.topRatedComment = Comment()
        self.sentimentRatios = {}
        self.subreddits = {}
        self.comments = []

    def getTopSubreddits(self):
        subReddits = [c.subreddit for c in self.comments]
        c = Counter(subReddits)
        return c.most_common(3)

    def getLowestRatedComments(self):
        return sorted(self.comments, key=lambda x: x.score)

    def getHighestRatedComments(self):
        return sorted(self.comments, key=lambda x: x.score, reverse=True)


def populateUser(username) -> User:
    userObj = User()
    redditor = instantiate(username)
    userObj.karma = redditor[0]
    user_comments = redditor[1]
    subreddits = userObj.subreddits

    for comment in user_comments:
        subreddit = comment['subreddit']
        commentSentiment = random.uniform(0, 1)
        try:
            mapLoc = subreddits[subreddit]
            mapLoc.append(commentSentiment)
        except:
            subreddits[subreddit] = [commentSentiment]

        parent = comment['parent']
        parentObj = Parent(
            # this frequently will not contain any text ,need toaccount for what type of thing the parent comment is
            score=parent['score'],
            contents=parent['body'],
            sentiment=random.uniform(0, 1)
        )

        commentObj = Comment(
            score=comment['score'],
            subreddit=subreddit,
            sentiment=commentSentiment,
            contents=comment['body'],
            parent=parentObj
        )
        userObj.comments.append(commentObj)

    # sentiment average calculations
    # can sort all of these to be by rating, sentiment, etc.
    return userObj


def processUser(username):
    user = populateUser(username)
    karma = user.karma
    topSubreddits = user.getTopSubreddits()
    lowestRatedComments = user.getLowestRatedComments()
    highestRatedComments = user.getHighestRatedComments()
    for comment in highestRatedComments:
        print(comment.contents)
        print(comment.score)


processUser('spez')
