import boto3

client = boto3.client('comprehend')

def detectLanguage(textData):
    """ 
    Detects the language of the passed in string
    :param textData string whose language is to be analyzed. Must be at least 20 characters long.
    :returns: RFC 5646 language code of the text or 'en' if an error occurs.
    :raises: Nothing (all exceptions are caught and 'en' [English] is returned as the default).
    """
    if len(textData) < 20 or len(textData.encode('utf-8')) < 5000:
        return 'en'

    try:
        return client.detect_dominant_language(
            Text=textData
        )['Languages'][0]['LanguageCode']
    except:
        return 'en'


def extractSentiment(textData, language = "N/A"):
    """ 
    Detects the language of the passed in string
    Text will be analyzed if it is smaller than 5000 bytes of UTF-8 encoded characters and in one of Amazon Comprehend's primary languages:
    Hindi (hi), German (de), Chinese (zh), Chinese (Taiwan) (zh-TW), Korean (ko), Portuguese (pt), English (en), Italian (it), French (fr), Spanish (es), Arabic (ar), Japanese (ja).

    :param textData: string whose sentiment is to be analyzed.
    :param language: RFC 5646 language code of the text to be analyzed. If none is provided, the language will be detected automatically.
    :returns: Extracted sentiment of the text as a string ('POSITIVE', 'NEGATIVE', 'NEUTRAL', 'MIXED'). If unable to process for whatever reason, returns 'UNDEFINED'.
    :raises: Nothing (all exceptions are caught and 0 is returned as the default)
    """

    if language == "N/A":
        language = detectLanguage(textData)

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
