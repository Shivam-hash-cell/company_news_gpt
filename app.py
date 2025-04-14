from flask import Flask, request, jsonify
import feedparser

app = Flask(__name__)

def fetch_news(company_name):
    rss_url = f"https://news.google.com/rss/search?q={company_name.replace(' ', '+')}"
    feed = feedparser.parse(rss_url)

    results = []

    for entry in feed.entries:
        results.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published if 'published' in entry else 'N/A'
        })

    return results

@app.route('/get-news', methods=['GET'])
def get_news():
    company = request.args.get('company')
    if not company:
        return jsonify({'error': 'Company name is required'}), 400

    news = fetch_news(company)
    return jsonify(news)

if __name__ == '__main__':
    app.run(debug=True)
