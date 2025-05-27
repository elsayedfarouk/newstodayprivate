from gnews import GNews
import get_final_url_with_selenium
import googlesheet
import get_news


def get_latest_news():
    return google_news.get_top_news()


def get_news_by_topic(topic):
    return google_news.get_news(topic)


def get_news_by_country(country_code):
    google_news.country = country_code.upper()
    return google_news.get_top_news()


# Convert news articles to structured dictionaries
def extract_news_data(articles):
    news_list = []
    if not articles:
        return news_list

    for article in articles:
        news_item = {
            "title": article.get("title"),
            "description": article.get("description"),
            "published_date": article.get("published date"),
            "url": get_final_url_with_selenium.get_final_url_with_selenium(article.get("url")),
            # "url": article.get("url"),
            "publisher_title": article.get("publisher", {}).get("title"),
            "publisher_href": article.get("publisher", {}).get("href")
        }
        news_list.append(news_item)

    return news_list


def latest_news():
    latest_news = extract_news_data(get_latest_news())

    # Example: Print titles only
    print("🔹 Latest News Titles:")
    for news_datax in latest_news[:1]:
        # print(news_data)
        # Extract data for each entry
        news_data = get_news.extract_data6(news_datax)

        title = news_data['title']
        date = news_data['date']
        summary = news_data['summary']
        image_path_original = news_data['image']
        website = news_data['website']
        article_url = news_data['link']

        status = "pending"
        # title = news_data['title']
        # description = news_data['description']
        # published_date = news_data['published_date']
        # url = news_data['url']
        # publisher_title = news_data['publisher_title']
        # publisher_href = news_data['publisher_href']

        new_row_data = [status, "Latest", country, title, date, summary, image_path_original, website, article_url]

        googlesheet.add_row_to_sheet(new_row_data, "NewsToday", "News")


def news_by_topic():
    topics = ["WORLD", "NATION", "BUSINESS", "TECHNOLOGY", "ENTERTAINMENT", "SPORTS", "SCIENCE", "HEALTH"]
    for topic in topics:

        # Get recent news
        topic_news_entries = extract_news_data(get_news_by_topic(topic))

        for news_datax in topic_news_entries[:1]:
            # Extract data for each entry
            news_data = get_news.extract_data6(news_datax)

            title = news_data['title']
            date = news_data['date']
            summary = news_data['summary']
            image_path_original = news_data['image']
            website = news_data['website']
            article_url = news_data['link']

            status = "pending"
            # title = news_data['title']
            # description = news_data['description']
            # published_date = news_data['published_date']
            # url = news_data['url']
            # publisher_title = news_data['publisher_title']
            # publisher_href = news_data['publisher_href']

            new_row_data = [status, topic, country, title, date, summary, image_path_original, website, article_url]

            # new_row_data = [status, topic, country, title, description, published_date, url, publisher_title,
            #                 publisher_href]
            googlesheet.add_row_to_sheet(new_row_data, "NewsToday", "News")


# Example usage
if __name__ == "__main__":
    # Initialize GNews client
    country = 'US'
    google_news = GNews(language='en', country=country, max_results=10)

    latest_news()
    # news_by_topic()

    # tech_news = extract_news_data(get_news_by_topic("Technology"))
    # india_news = extract_news_data(get_news_by_country("IN"))

    # print("\n🔹 Technology News URLs:")
    # for news in tech_news:
    #     print(news["url"])
    #
    # print("\n🔹 Publishers from India News:")
    # for news in india_news:
    #     print(news["publisher_title"])
