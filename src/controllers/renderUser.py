from flask import redirect, request, url_for, render_template, Response, abort
from flask.views import MethodView, View
import src.models as models
from .processUser import processUser, User


def fixSubreddits(subreddits):
    d = {"POSTIVE", "NEGATIVE", "NEUTRAL", "MIXED"}
    for v in subreddits.values():
        for va in v['sentimentCounts'].keys():
            for d_ in d:
                if d_ not in va:
                    va[d] = 0

    print(subreddits)


def renderUser(user):
    subreddits = fixSubreddits(user['subreddits'])
    for k, v in user.items():
        print(k)
    return render_template(
        'user.html',
        name=user['name'],
        # language=user['language'],
        karma=user['karma'],
        topSubreddits=user['topSubreddits'],
        languageComplexity=user['languageComplexity'],
        # dominantSentiment=user['dominantSentiment'],
        lowestRatedComment={
            'contents': user['lowestRatedComment']['contents'],
            'score': user['lowestRatedComment']['score'],
            'subreddit': user['lowestRatedComment']['subreddit'],
            'sentiment': user['lowestRatedComment']['sentiment']
        },
        topRatedComment={
            'contents': user['topRatedComment']['contents'],
            'score': user['topRatedComment']['score'],
            'subreddit': user['topRatedComment']['subreddit'],
            'sentiment': user['topRatedComment']['sentiment'],
        },
        sentimentRatios={
            'positive': user['sentimentRatios']['positive'],
            'negative': user['sentimentRatios']['negative'],
            'neutral': user['sentimentRatios']['neutral'],
            'mixed': user['sentimentRatios']['mixed']
        },
        sentimentChangeRatios={
            'positiveToPositive': user['sentimentChangeRatios']['positiveToPositive'],
            'positiveToNegative': user['sentimentChangeRatios']['positiveToNegative'],
            'positiveToNeutral': user['sentimentChangeRatios']['positiveToNeutral'],
            'positiveToMixed': user['sentimentChangeRatios']['positiveToMixed'],
            'negativeToPositive': user['sentimentChangeRatios']['negativeToPositive'],
            'negativeToNegative': user['sentimentChangeRatios']['negativeToNegative'],
            'negativeToNeutral': user['sentimentChangeRatios']['negativeToNeutral'],
            'negativeToMixed': user['sentimentChangeRatios']['negativeToMixed'],
            'neutralToPositive': user['sentimentChangeRatios']['neutralToPositive'],
            'neutralToNegative': user['sentimentChangeRatios']['neutralToNegative'],
            'neutralToNeutral': user['sentimentChangeRatios']['neutralToNeutral'],
            'neutralToMixed': user['sentimentChangeRatios']['neutralToMixed'],
            'mixedToPositive': user['sentimentChangeRatios']['mixedToPositive'],
            'mixedToNegative': user['sentimentChangeRatios']['mixedToNegative'],
            'mixedToNeutral': user['sentimentChangeRatios']['mixedToNeutral'],
            'mixedToMixed': user['sentimentChangeRatios']['mixedToMixed'],
        },
        dominantSentiment=user['dominantSentiment'],
        subreddits=user['subreddits']
    )


def renderUserObj(user):
    return render_template(
        'user.html',
        name=user.name,
        language=user.language,
        karma=user.karma,
        topSubreddits=user.topSubreddits,
        dominantSentiment=user.dominantSentiment,
        languageComplexity=user.languageComplexity,
        lowestRatedComment={
            'contents': user.lowestRatedComment.contents,
            'score': user.lowestRatedComment.score,
            'subreddit': user.lowestRatedComment.subreddit,
            'sentiment': user.lowestRatedComment.sentiment,
        },
        topRatedComment={
            'contents': user.topRatedComment.contents,
            'score': user.topRatedComment.score,
            'subreddit': user.topRatedComment.subreddit,
            'sentiment': user.topRatedComment.sentiment,
        },
        sentimentChangeRatios={
            'positiveToPositive': user.sentimentChangeRatios.positiveToPositive,
            'positiveToNegative': user.sentimentChangeRatios.positiveToNegative,
            'positiveToNeutral': user.sentimentChangeRatios.positiveToNeutral,
            'positiveToMixed': user.sentimentChangeRatios.positiveToMixed,
            'negativeToPositive': user.sentimentChangeRatios.negativeToPositive,
            'negativeToNegative': user.sentimentChangeRatios.negativeToNegative,
            'negativeToNeutral': user.sentimentChangeRatios.negativeToNeutral,
            'negativeToMixed': user.sentimentChangeRatios.negativeToMixed,
            'neutralToPositive': user.sentimentChangeRatios.neutralToPositive,
            'neutralToNegative': user.sentimentChangeRatios.neutralToNegative,
            'neutralToNeutral': user.sentimentChangeRatios.neutralToNeutral,
            'neutralToMixed': user.sentimentChangeRatios.neutralToMixed,
            'mixedToPositive': user.sentimentChangeRatios.mixedToPositive,
            'mixedToNegative': user.sentimentChangeRatios.mixedToNegative,
            'mixedToNeutral': user.sentimentChangeRatios.mixedToNeutral,
            'mixedToMixed': user.sentimentChangeRatios.mixedToMixed,
        },
        sentimentRatios={
            'positive': user.sentimentRatios.positive,
            'negative': user.sentimentRatios.negative,
            'neutral': user.sentimentRatios.neutral,
            'mixed': user.sentimentRatios.mixed
        },
        subreddits=user.subreddits
    )


class userView(View):
    """
    View that handles a dispatch request that is overloaded
    """

    def dispatch_request(self, username):
        """
        Routes to the page of the user
        """
        model = models.init()
        user = model.getUser(username)
        if user:
            print("dynamodb")
            return renderUser(user)
        else:
            userObj = processUser(username)
            if userObj == 404:
                abort(404)
            model.insertUser(userObj)
            return renderUserObj(userObj)
