from flask import Flask, request, jsonify
import feedparser
import datetime

app = Flask(__name__)

def fetch_news(company_name, keyword=None, months=None):
    rss_url = f"https://news.google.com/rss/search?q={company_name.replace(' ', '+')}"
    feed = feedparser.parse(rss_url)

    results = []

    for entry in feed.entries:
        # Keyword filter
        if keyword and keyword.lower() not in entry.title.lower() and keyword.lower() not in entry.summary.lower():
            continue

        # Months filter
        if months:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                entry_date = datetime.datetime(*entry.published_parsed[:6])
                if entry_date < datetime.datetime.now() - datetime.timedelta(days=int(months)*30):
                    continue

        results.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published
        })

    return results


@app.route('/get-news', methods=['GET'])
def get_news():
    company = request.args.get('company')
    keyword = request.args.get('keyword')
    months = request.args.get('months')

    if not company:
        return jsonify({'error': 'Company name is required'}), 400

    news = fetch_news(company, keyword, months)
    return jsonify(news)


if __name__ == '__main__':
    app.run(debug=True)
