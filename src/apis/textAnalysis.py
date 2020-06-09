import boto3
import re
import requests
import random
import os

client = boto3.client('comprehend')


def getLanguage(textData):
    """
    Detects the language of the passed in string
    :param textData string whose language is to be analyzed. Must be at least 20 characters long and have fewer than 5000 bytes of UTF-8 compliant characters.
    :returns: RFC 5646 language code of the text or 'en' if an error occurs.
    :raises: Nothing (all exceptions are caught and 'UNDEFINED' is returned if something goes wrong).
    """

    if len(textData) < 20 or len(textData.encode('utf-8')) > 5000:
        return 'UNDEFINED'

    try:
        return client.detect_dominant_language(
            Text=textData
        )['Languages'][0]['LanguageCode']
    except:
        return 'UNDEFINED'


def getSentiment(textData, language="UNDEFINED"):
    """
    Detects the language of the passed in string
    Text will be analyzed if it is smaller than 5000 bytes of UTF-8 encoded characters and in one of Amazon Comprehend's primary languages:
    Hindi (hi), German (de), Chinese (zh), Chinese (Taiwan) (zh-TW), Korean (ko), Portuguese (pt), English (en), Italian (it), French (fr), Spanish (es), Arabic (ar), Japanese (ja).

    :param textData: string whose sentiment is to be analyzed.
    :param language: RFC 5646 language code of the text to be analyzed. If none is provided, the language will be detected automatically.
    :returns: Extracted sentiment of the text as a string ('POSITIVE', 'NEGATIVE', 'NEUTRAL', 'MIXED'). If unable to process for whatever reason, returns 'UNDEFINED'.
    :raises: Nothing (all exceptions are caught and 'UNDEFINED' is returned as the default)
    """

    if language == "UNDEFINED":
        language = getLanguage(textData)

    if language in ['hi', 'de', 'zh-TW', 'ko', 'pt', 'en', 'it', 'fr', 'zh', 'es', 'ar', 'ja'] and len(textData.encode('utf-8')) < 5000:
        try:
            response = client.detect_sentiment(
                Text=textData,
                LanguageCode=language
            )
            return response['Sentiment']
        except:
            return 'UNDEFINED'
    else:
        return 'UNDEFINED'


def getComplexity(textData):
    """
    Analyzes and ranks text on its linguistic complexity on a scale of 1 to 10 where 1 is least complex and 10 is most complex.
    Note: most text stacks around 4-5 range. So, 1 - extremely below average, 2-3 - below average, 4 - average, 5-6 above average, 7+ genius.
    The text is expected to be no longer than 200 words or 3000 characters whichever comes first.

    :param textData: string whose complexity is to be analyzed.
    :returns: Complexity score on a scale of 1 to 10 where 1 is least complex and 10 is most complex. If unable to process for whatever reason, returns -1.
    :raises: Nothing, -1 is returned if something fails.
    """
    key = os.environ['rapidapi_key']
    url = "https://twinword-language-scoring.p.rapidapi.com/text/"

    wordCount = len(re.findall(r'\w+', textData))
    charCount = len(textData)

    if wordCount <= 200 and charCount <= 3000:
        querystring = {"text": textData}
        headers = {
            'x-rapidapi-host': "twinword-language-scoring.p.rapidapi.com",
            'x-rapidapi-key': "09e32c1f41mshfb7d5522017cdd3p18bd8fjsnb1b575e4cc6f"
        }
        response = requests.request(
            "GET", url, headers=headers, params=querystring)
        if response:
            return response.json()['ten_degree']
        else:
            return -1
    else:
        return -1