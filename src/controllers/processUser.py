from src.apis.praw import instantiate
from src.apis.textAnalysis import getLanguage, getSentiment, getComplexity
from collections import Counter
import random
import re
from functools import reduce

"""
Contains functionality for querying and processing reddit user information.
"""


class Parent():
    """
        Used to store parent comment information inside 'Comment' objects.
    """

    def __init__(self, score=0, contents=None, sentiment=None):
        self.score = score
        self.contents = contents
        self.sentiment = sentiment


class Comment():
    """
        Used to store comment information inside 'User' objects.
    """

    def __init__(self, score=0, contents=None, subreddit=None, sentiment=None, parent=None):
        self.score = score
        self.contents = contents
        self.subreddit = subreddit
        self.sentiment = sentiment
        self.parent = parent


class SentimentChangeRatios():
    """
        Used to store information about sentiment change between parent comment and user comment inside 'User' objects.
    """

    def __init__(self):
        self.positiveToNegative = 0.0
        self.positiveToNeutral = 0.0
        self.positiveToMixed = 0.0
        self.negativeToPositive = 0.0
        self.negativeToNeutral = 0.0
        self.negativeToMixed = 0.0
        self.neutralToPositive = 0.0
        self.neutralToNegative = 0.0
        self.neutralToMixed = 0.0
        self.mixedToPositive = 0.0
        self.mixedToNegative = 0.0
        self.mixedToNeutral = 0.0


class SentimentRatios():
    """
        Used to store information about comment sentiment ratios inside 'User' objects.
    """

    def __init__(self):
        self.positive = 0
        self.negative = 0
        self.neutral = 0
        self.mixed = 0


class User():
    """
        Used object stores all information collected about a reddit user.
    """

    def __init__(self):
        # Raw data (data to be read from praw and assigned sentiment values)
        self.name = "UNDEFINED"
        self.language = "UNDEFINED"
        self.karma = 0
        self.comments = []
        self.commentCount = 0

        # Processed data (extracted from raw data):
        self.languageComplexity = -1.0
        self.topSubreddits = None
        self.dominantSentiment = "UNDEFINED"
        self.lowestRatedComment = Comment()
        self.topRatedComment = Comment()
        self.sentimentChangeRatios = SentimentChangeRatios()
        self.sentimentRatios = SentimentRatios()
        self.subreddits = {}


def guessUserLanguage(comments):
    """
    Accepts a list of comments and guesses the language of the user who generated them based on 15 randomly selected comments.
    Only generates a guess if at least 15 comments are provided.
    This is problematic for actively multilingual users but saves a decent amount of processing time and drains API funds slower.

    :param comments: List of comments based upon which the guess is to be made.
    :returns: RFC 5646 language code of the best guess or 'UNDEFINED' if filed to make a guess for whatever reason.
    """
    langSampleList = list()
    commentCount = len(comments)
    guessedLanguage = 'UNDEFINED'

    if(commentCount < 15):
        return 'UNDEFINED'
    else:
        # Extracts 15 random comments from the comment pool and get their language.
        commentRandomIndexList = random.sample(range(commentCount), 15)
        for index in commentRandomIndexList:
            langSampleList.append(getLanguage(comments[index]))

        # Determines the most commonly occuring language in random sample.
        rankedLanguages = Counter(langSampleList).most_common()
        if rankedLanguages[0][0] == "UNDEFINED" and len(rankedLanguages) > 1:
            return rankedLanguages[1][0]
        return rankedLanguages[0][0]


def generateUserWithRawData(prawData, username) -> User:
    """
    Accepts raw data from the praw api and returns a User with populated raw data fields.
    Reads User's information from praw api, assigns the user a language, and assigns sentiment scores to all relevant comments.

    :param prawData: raw data from praw api
    :returns: User with 'raw data' filled in
    """

    prawDataComments = prawData[1]

    constructedUser = User()

    constructedUser.name = username
    constructedUser.karma = prawData[0]
    constructedUser.commentCount = len(prawDataComments)

    # Predicts the user's language.
    if(constructedUser.commentCount >= 20):
        rawCommentArray = []
        for comment in prawDataComments:
            rawCommentArray.append(comment['body'])
        constructedUser.language = guessUserLanguage(rawCommentArray)

    # Loops over comments retrieved from praw api and processes relevant values for original comment and parent comment.
    for comment in prawDataComments:

        # Determines sentiment for comment and parent comment.
        commentSentiment = getSentiment(
            comment['body'], constructedUser.language)
        parentCommentSentiment = 'UNDEFINED'
        # Only determiens parent comment sentiment if child sentiment is defined since it won't be needed otherwise.
        if commentSentiment != 'UNDEFINED':
            parentCommentSentiment = getSentiment(
                comment['parent']['body'], constructedUser.language)

        parentObj = Parent(
            score=comment['parent']['score'],
            contents=comment['parent']['body'],
            sentiment=parentCommentSentiment
        )

        commentObj = Comment(
            subreddit=comment['subreddit'],
            sentiment=commentSentiment,
            score=comment['score'],
            contents=comment['body'],
        )
        if constructedUser.subreddits:
            try:
                dictVal = constructedUser.subreddits[commentObj.subreddit]
                dictVal.append(
                    {
                        'sentiment': commentSentiment,
                        'score': comment['score'],
                    }
                )
            except:
                constructedUser.subreddits[commentObj.subreddit] = [
                    {
                        'sentiment': commentSentiment,
                        'score': comment['score'],
                    }]
        else:
            constructedUser.subreddits = {
                comment['subreddit']: [
                    {
                        'sentiment': commentSentiment,
                        'score': comment['score'],
                    }
                ]}

        commentObj.parent = parentObj
        constructedUser.comments.append(commentObj)

    return constructedUser


def processLanguageComplexity(comments):
    """
    Determines user's language complexity score by analyzing a poriton of their comments and taking the average.

    :param comments: List of comments whose complexity is to be analyzed.
    :returns: Calculated complexity of the user (1-10). -1 If the complexity was not able to be calculated for any reason.
    """

    # Filter out comments that are compliant with API requirements.
    validComments = []
    for comment in comments:
        commentWordCount = len(re.findall(r'\w+', comment))
        commentCharCount = len(comment)
        if commentWordCount <= 200 and commentCharCount <= 3000:
            validComments.append(comment)

    # Determine the amount of comments to be processed (as many as possible between 10 and 40)
    commentCountToProcess = 0
    validCommentCount = len(validComments)
    if(validCommentCount < 10):  # No Point in analyzing less than 10 comments
        return -1.0
    elif(validCommentCount >= 40):
        commentCountToProcess = 40
    else:
        commentCountToProcess = validCommentCount

    # Create a random range of indexes of size commentCountToProcess within the validCommentCount range and calculate the complexity average for the comments at those indexes.
    commentRandomIndexList = random.sample(
        range(validCommentCount), commentCountToProcess)
    complexityAccumulator = 0
    validComplexityCount = 0
    for index in commentRandomIndexList:
        calculatedComplexity = getComplexity(validComments[index])
        if(calculatedComplexity > 0):
            complexityAccumulator += calculatedComplexity
            validComplexityCount += 1
    return complexityAccumulator / validComplexityCount


def processSubreddits(subreddits, user):
    processed = {}
    for k, v in subreddits.items():
        sentimentCounts = Counter(x['sentiment'] for x in v)
        numComments = len(v)
        avgScore = float(sum(d['score'] for d in v)) / numComments
        print(avgScore)
        processed[k] = {
            'sentimentCounts': dict(sentimentCounts),
            'numComments': numComments,
            'avgScore': avgScore
        }
    return processed


def processRawUserData(user):
    """
    Accepts a user with filled in 'raw data' fields, processes them and fills in 'processed data' fields.

    :param user: User object with filled in 'raw data'
    :returns: User with all data filled in.
    """
    # Determine favorite subreddits with ratio of all comments posted on each one.
    subreddits = [c.subreddit for c in user.comments]
    c = Counter(sr for sr in subreddits)
    c = c.most_common(5)
    dc = dict(c)
    # list comprehension
    subreddits = {k: v for (k, v) in user.subreddits.items() if k in dc}
    for subreddit in c:
        if user.topSubreddits:
            user.topSubreddits.update(
                {subreddit[0]: subreddit[1]/user.commentCount})
        else:
            user.topSubreddits = {subreddit[0]: subreddit[1]/user.commentCount}

    user.subreddits = processSubreddits(subreddits, user)
    # Determine best and worst rated comment.
    commentsSortedByScore = sorted(user.comments, key=lambda x: x.score)
    user.lowestRatedComment = commentsSortedByScore[0]
    user.topRatedComment = commentsSortedByScore[user.commentCount - 1]
    # Deterime highest and lowest sentiment comment

    # Determine user's language complexity.
    user.languageComplexity = processLanguageComplexity(
        [comment.contents for comment in user.comments])

    # Process comment sentiment data.
    commentsWithValidSentiment = 0.0
    commentPairsWithValidSentiment = 0.0
    for comment in user.comments:
        # Increment before operations
        commentPairsWithValidSentiment += 1.0
        commentsWithValidSentiment += 1.0

        if comment.sentiment == 'POSITIVE':
            user.sentimentRatios.positive += 1
            if comment.parent.sentiment == 'NEGATIVE':
                user.sentimentChangeRatios.negativeToPositive += 1
            elif comment.parent.sentiment == 'NEUTRAL':
                user.sentimentChangeRatios.neutralToPositive += 1
            elif comment.parent.sentiment == 'MIXED':
                user.sentimentChangeRatios.mixedToPositive += 1
            else:
                commentPairsWithValidSentiment -= 1

        elif comment.sentiment == 'NEGATIVE':
            user.sentimentRatios.negative += 1
            if comment.parent.sentiment == 'POSITIVE':
                user.sentimentChangeRatios.positiveToNegative += 1
            elif comment.parent.sentiment == 'NEUTRAL':
                user.sentimentChangeRatios.neutralToNegative += 1
            elif comment.parent.sentiment == 'MIXED':
                user.sentimentChangeRatios.mixedToNegative += 1
            else:
                commentPairsWithValidSentiment -= 1

        elif comment.sentiment == 'NEUTRAL':
            user.sentimentRatios.neutral += 1
            if comment.parent.sentiment == 'POSITIVE':
                user.sentimentChangeRatios.positiveToNeutral += 1
            elif comment.parent.sentiment == 'NEGATIVE':
                user.sentimentChangeRatios.negativeToNeutral += 1
            elif comment.parent.sentiment == 'MIXED':
                user.sentimentChangeRatios.mixedToNeutral += 1
            else:
                commentPairsWithValidSentiment -= 1

        elif comment.sentiment == 'MIXED':
            user.sentimentRatios.mixed += 1
            if comment.parent.sentiment == 'POSITIVE':
                user.sentimentChangeRatios.positiveToMixed += 1
            elif comment.parent.sentiment == 'NEGATIVE':
                user.sentimentChangeRatios.negativeToMixed += 1
            elif comment.parent.sentiment == 'NEUTRAL':
                user.sentimentChangeRatios.neutralToMixed += 1
            else:
                commentPairsWithValidSentiment -= 1

        else:  # If the comment is 'UNDEFINED', then we've failed to fined either a valid comment or comment pair.
            commentPairsWithValidSentiment -= 1
            commentsWithValidSentiment -= 1

    if(commentsWithValidSentiment > 0.0):
        user.sentimentRatios.positive /= commentsWithValidSentiment
        user.sentimentRatios.negative /= commentsWithValidSentiment
        user.sentimentRatios.neutral /= commentsWithValidSentiment
        user.sentimentRatios.mixed /= commentsWithValidSentiment

        dominantSentimentCount = max([user.sentimentRatios.positive, user.sentimentRatios.negative,
                                      user.sentimentRatios.neutral, user.sentimentRatios.mixed])
        if(dominantSentimentCount == user.sentimentRatios.positive):
            user.dominantSentiment = "POSITIVE"
        if(dominantSentimentCount == user.sentimentRatios.negative):
            user.dominantSentiment = "NEGATIVE"
        if(dominantSentimentCount == user.sentimentRatios.neutral):
            user.dominantSentiment = "NEUTRAL"
        if(dominantSentimentCount == user.sentimentRatios.mixed):
            user.dominantSentiment = "MIXED"

    if(commentPairsWithValidSentiment > 0.0):
        user.sentimentChangeRatios.positiveToNegative /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.positiveToNeutral /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.positiveToMixed /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.negativeToPositive /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.negativeToNeutral /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.negativeToMixed /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.neutralToPositive /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.neutralToNegative /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.neutralToMixed /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.mixedToPositive /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.mixedToNegative /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.mixedToNeutral /= commentPairsWithValidSentiment


def processUser(username):
    prawData = instantiate(username)
    if prawData != 404:
        user = generateUserWithRawData(prawData, username)
        processRawUserData(user)
        return user
    else:
        return 404
