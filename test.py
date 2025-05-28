import googlesheet
from newspaper import *
import google.generativeai as genai
import traceback
import inspect
import get_final_url_with_selenium
from gnews import GNews


def get_latest_news():
    return google_news.get_top_news()


def get_news_by_topic(topic):
    return google_news.get_news(topic)


def get_news_by_country(country_code):
    google_news.country = country_code.upper()
    return google_news.get_top_news()


def get_full_article(news_url):
    print("Getting full article details.....")
    try:
        first_article = Article(url=news_url, fetch_images=True, keep_article_html=True)
        first_article.download()
        first_article.parse()

        newstext = first_article.text
        top_image = first_article.top_image
        article_html = first_article.article_html
        canonical_link = first_article.canonical_link

        return newstext, top_image, article_html, canonical_link

    except Exception as e:
        print(e)
        return "", "", "", ""


def generate_content2(article_text):
    try:
        print("Generating the summary.....")

        api_key = "AIzaSyCWexOEMVgiIViLc8oLnZ3HLcBmrt2-g9w"
        model_name = "gemini-1.5-flash-8b"
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            # "max_output_tokens": 1024,
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name=model_name,
                                      safety_settings=safety_settings)

        response = model.generate_content(
            f"Summarize this news article in the style of a professional news anchor delivering a report. The summary should be exactly 1000 characters long, ensuring a natural flow suitable for text-to-speech conversion."
            f" {article_text}")

        # print(response.parts)
        # print(response.parts[0].text)
        # Access the generated content
        # def get_generated_text(response):
        try:
            # Try to get generated text from response.parts
            generated_text = response.parts[0].text if response.parts else response.text
            return generated_text
        except Exception as e:
            print(f"An exception occurred in the first block: {e}")

            try:
                # Fallback to response.text
                return response.text
            except Exception as e:
                print(f"An exception occurred in the second block: {e}")

                try:
                    # Final fallback logic (custom operation as needed, example given for illustration)
                    x = response.candidates[0].content.parts
                    return x
                except Exception as e:
                    print(f"An exception occurred in the second block: {e}")
                    return ""

        # print("response")
        # print(generated_text)
        # return generated_text
    except Exception as e:
        print(f"An exception occurred: {e}")
        print(f"Current line number: {inspect.currentframe().f_lineno}")
        traceback.print_exc()
        return ""


def extract_data6(entry):
    print("extracting news details......")

    newstext, top_image, article_html, canonical_link = "", "", "", ""
    print(entry)
    try:
        link = entry.get("url")
        newlink = get_final_url_with_selenium.get_final_url_with_selenium(link)
        result = get_full_article(newlink)

        if result:
            newstext, top_image, article_html, canonical_link = result
    except Exception as e:
        print(e)
    title = entry.get("title")
    sep = '-'
    title_stripped = title.rsplit(sep, 1)[0]
    description = entry.get("description")
    summary = generate_content2(entry.get("title") + description + newstext)
    summary2 = summary + "If you like our content, don't forget to like and subscribe to our channel, NEWS TODAY."
    data = {
        "title": title_stripped,
        "date": entry.get("published date"),
        "summary": summary2,
        "image": top_image,
        "website": entry["publisher"].get("href"),
        "link": entry.get("link")
    }

    # res = posttosupabase.insert_data_into_table(table_name="news_article", data=data)

    return data


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
    # latest_news = extract_news_data(get_latest_news())

    # Get recent news
    recent_news_entries = get_latest_news()

    # Example: Print titles only
    print("🔹 Latest News Titles:")
    for each_news_entry in recent_news_entries[:1]:

        try:
            # print(news_data)
            # Extract data for each entry
            news_data = extract_data6(each_news_entry)

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


        except Exception as e:
            print(f"Error processing news item: {e}")


def news_by_topic():
    topics = ["WORLD", "NATION", "BUSINESS", "TECHNOLOGY", "ENTERTAINMENT", "SPORTS", "SCIENCE", "HEALTH"]
    for topic in topics:

        # Get recent news
        topic_news_entries = extract_news_data(get_news_by_topic(topic))

        for news_datax in topic_news_entries[:3]:
            # Extract data for each entry
            news_data = extract_data6(news_datax)

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
