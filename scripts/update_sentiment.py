"""
Fetches financial news headlines via Yahoo Finance RSS and scores sentiment
with VADER (no model download, no API key, runs offline).
Output: sentiment.json, read by dossier.html.
"""
import json
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timezone

SYMBOLS = [
    'NVDA', 'MSFT', 'GOOGL', 'META', 'AAPL', 'TSLA', 'AMZN',
    'PLTR', 'AMD', 'BX', 'KKR', 'APO', 'GS', 'JPM',
    'BIDU', 'BABA', 'XOM', 'CVX', 'LLY', 'NFLX', 'COIN',
]

analyzer = SentimentIntensityAnalyzer()
results = {}

for sym in SYMBOLS:
    try:
        url = f'https://feeds.finance.yahoo.com/rss/2.0/headline?s={sym}&region=US&lang=en-US'
        feed = feedparser.parse(url)
        titles = [e.title for e in feed.entries[:6] if hasattr(e, 'title')]
        if titles:
            scores = [analyzer.polarity_scores(t)['compound'] for t in titles]
            results[sym] = round(sum(scores) / len(scores), 3)
        else:
            results[sym] = 0.0
    except Exception as ex:
        print(f'[sentiment] {sym} error: {ex}')
        results[sym] = 0.0

results['updated'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

with open('sentiment.json', 'w') as f:
    json.dump(results, f, indent=2)

scored = {k: v for k, v in results.items() if k != 'updated'}
print(f'[sentiment] scored {len(scored)} symbols')
