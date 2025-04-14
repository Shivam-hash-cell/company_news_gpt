from flask import Flask, request, jsonify
import feedparser
import datetime
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

NEWS_API_KEY = os.getenv("NEWSDATA_API_KEY")


def fetch_news_google(company_name):
    rss_url = f"https://news.google.com/rss/search?q={company_name.replace(' ', '+')}"
    feed = feedparser.parse(rss_url)

    results = []
    for entry in feed.entries:
        results.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published
        })
    return results


def fetch_news_newsdata(company_name, keyword=None, months=None):
    base_url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": NEWS_API_KEY,
        "q": f"{company_name} {keyword}" if keyword else company_name,
        "language": "en",
        "country": "in"
    }

    if months:
        from_date = (datetime.datetime.now() - datetime.timedelta(days=int(months) * 30)).strftime("%Y-%m-%d")
        params["from_date"] = from_date

    response = requests.get(base_url, params=params)

    results = []

    try:
        data = response.json()  # Try parsing JSON
    except Exception:
        return [{
            'title': 'Error: Unexpected response from Newsdata API',
            'link': '',
            'published': ''
        }]

    if isinstance(data, dict) and "results" in data and isinstance(data["results"], list):
        for article in data["results"]:
            results.append({
                'title': article.get('title', 'No title'),
                'link': article.get('link', ''),
                'published': article.get('pubDate', '')
            })
    else:
        results.append({
            'title': 'No news found or API limit reached',
            'link': '',
            'published': ''
        })

    return results


@app.route('/get-news', methods=['GET'])
def get_news():
    company = request.args.get('company')
    keyword = request.args.get('keyword')
    months = request.args.get('months')

    if not company:
        return jsonify({'error': 'Company name is required'}), 400

    # Smart decision: Newsdata.io if keyword or months provided
    if keyword or months:
        news = fetch_news_newsdata(company, keyword, months)
    else:
        news = fetch_news_google(company)

    return jsonify(news)


if __name__ == '__main__':
    app.run(debug=True)
