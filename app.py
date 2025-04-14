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
    query = f"{company_name} {keyword}" if keyword else company_name

    params = {
        "apikey": NEWS_API_KEY,
        "q": query,
        "language": "en",
        "country": "in"
    }

    if months:
        from_date = (datetime.datetime.now() - datetime.timedelta(days=int(months) * 30)).strftime("%Y-%m-%d")
        params["from_date"] = from_date

    results = []
    page = 1
    max_pages = 3  # Limit to avoid too many API calls

    while page <= max_pages:
        response = requests.get(base_url, params=params)

        if 'application/json' not in response.headers.get('Content-Type', ''):
            break  # Exit if invalid response

        try:
            data = response.json()
        except Exception:
            break

        if "results" in data and isinstance(data["results"], list):
            for article in data["results"]:
                results.append({
                    'title': article.get('title', 'No title'),
                    'link': article.get('link', ''),
                    'published': article.get('pubDate', '')
                })

        # Check for next page token
        if data.get('nextPage'):
            params['page'] = data['nextPage']
            page += 1
        else:
            break

    return results


@app.route('/get-news', methods=['GET'])
def get_news():
    company = request.args.get('company')
    keyword = request.args.get('keyword')
    months = request.args.get('months')

    if not company:
        return jsonify({'error': 'Company name is required'}), 400

    # Try Newsdata.io first (fully optimized)
    news = fetch_news_newsdata(company, keyword, months)

    # If Newsdata.io fails or gives nothing → fallback to Google RSS
    if not news:
        news = fetch_news_google(company)

    # If both fail
    if not news:
        news = [{
            'title': 'No relevant news found for your query',
            'link': '',
            'published': ''
        }]

    return jsonify(news)


if __name__ == '__main__':
    app.run(debug=True)
