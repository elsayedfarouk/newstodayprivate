import get_news as news
import json
import os
from datetime import datetime
import googlesheet


def main():
    topics = ["WORLD", "NATION", "BUSINESS", "TECHNOLOGY", "ENTERTAINMENT", "SPORTS", "SCIENCE", "HEALTH"]
    for topic in topics[:1]:

        # Get recent news
        recent_news_entries = news.get_news_by_topic1(topic)

        for each_news_entry in recent_news_entries[:1]:
            print(each_news_entry)
            # Extract data for each entry
            # news_data = news.extract_data4(each_news_entry)

            article_url = each_news_entry['url']
            title = each_news_entry['title']
            publisher = each_news_entry['publisher']



            status = ""
            # title = news_data['title']
            # date = news_data['date']
            # summary = news_data['summary']
            # image_path_original = news_data['image']
            # website = news_data['website']
            # article_url = news_data['link']
            # timestamp = ""

            # Check if any of the required fields are empty
            # if not title or not summary or not image_path_original:
            #     print("Error: Missing title, summary, or image path. Skipping video generation.")
            #     print(f"title: {title}\n\n summar: {summary}\n\n image: {image_path_original}")
            # else:

            # new_row_data = [status, title, date, summary, image_path_original, website, article_url, timestamp]
            #
            # googlesheet.add_row_to_sheet(new_row_data, "NewsToday", "Sheet1")

            new_row_data = [status, title, publisher]

            googlesheet.add_row_to_sheet(new_row_data, "NewsToday", "Sheet1")

if __name__ == "__main__":
    main()
