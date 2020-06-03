# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

# Instantiates a client
client = language.LanguageServiceClient()


def extactSentiment(textData):
    doc = types.Document(
        content=textData,
        type=enums.Document.Type.PLAIN_TEXT)
    return client.analyze_sentiment(document=doc).document_sentiment.score
