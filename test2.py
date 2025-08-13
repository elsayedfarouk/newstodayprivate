from gnews import GNews

google_news = GNews()
pakistan_news = google_news.get_news_by_topic('WORLD')
print(pakistan_news)

