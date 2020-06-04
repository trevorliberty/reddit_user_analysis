import requests
"""BACKUP TO AWS"""

sentimentUrl = "https://twinword-sentiment-analysis.p.rapidapi.com/analyze/"

def extractSentiment(textData):
    payload = "text=" + str(textData)
    headers = {
        'x-rapidapi-host': "twinword-sentiment-analysis.p.rapidapi.com",
        'x-rapidapi-key': "09e32c1f41mshfb7d5522017cdd3p18bd8fjsnb1b575e4cc6f",
        'content-type': "application/x-www-form-urlencoded"
    }
    response = requests.request('POST', sentimentUrl, data=payload, headers=headers)
    if response:
        return response.json()['score']
    else:
        return None