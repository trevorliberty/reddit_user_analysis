import boto3

client = boto3.client('comprehend')

response = client.detect_sentiment(
    Text="I hate everyone!", 
    LanguageCode="en"
    )

print(response)
