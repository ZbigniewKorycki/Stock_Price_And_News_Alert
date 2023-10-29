import requests
from twilio.rest import Client
import config

TICKER = input("Input company ticket symbol: ")
COMPANY_NAME = input("Input company name: ")

account_sid_twilio = config.account_sid_twilio
auth_token_twilio = config.auth_token_twilio
client = Client(account_sid_twilio, auth_token_twilio)

api_key_alphavantage = config.api_key_alphavantage
api_alphavantage = "https://www.alphavantage.co/query"
parameters_alphavantage = {
    "function": "TIME_SERIES_DAILY",
    "symbol": TICKER,
    "interval": "60min",
    "apikey": api_key_alphavantage,
}

connection_alphavantage = requests.get(
    url=api_alphavantage, params=parameters_alphavantage
)
connection_alphavantage.raise_for_status()

alphavantage_data = connection_alphavantage.json()["Time Series (Daily)"]
print(alphavantage_data)
data_list = [value for (key, value) in alphavantage_data.items()]
yesterday_data = data_list[0]
yesterday_closing_price = data_list[0]["4. close"]
day_before_data = data_list[1]
day_before_closing_price = data_list[1]["4. close"]


def check_difference():
    difference = (
        float(yesterday_closing_price) - float(day_before_closing_price)
    ) / float(yesterday_closing_price)
    percent_difference = round(difference * 100, 2)
    return percent_difference


if check_difference() >= 1 or check_difference() <= -1:
    api_news_api = "https://newsapi.org/v2/everything"
    api_key_newsapi = config.api_key_newsapi
    parameters_news_api = {
        "q": COMPANY_NAME,
        "sortBy": "publishedAt",
        "apiKey": api_key_newsapi,
    }
    connection_news_api = requests.get(url=api_news_api, params=parameters_news_api)
    connection_news_api.raise_for_status()
    articles = connection_news_api.json()["articles"]
    three_articles = articles[0:3]
    formatted_articles = [
        f"Headline: {article['title']}\nBrief: {article['description']}"
        for article in three_articles
    ]
    print(formatted_articles)
    for sms in formatted_articles:
        client = Client(account_sid_twilio, auth_token_twilio)
        if check_difference() > 0:
            difference_with_icon = f"🔺 {check_difference()}%"
        else:
            difference_with_icon = f"🔻 {check_difference()}%"
        message = client.messages.create(
            body=f"{TICKER}: {difference_with_icon}\n{sms}",
            from_=config.twilio_phone_from,
            to=config.phone_to,
        )
        print(message.status)
