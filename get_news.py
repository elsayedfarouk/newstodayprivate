import json
import os
from datetime import datetime
from newspaper import *
from pygooglenews import GoogleNews
import google.generativeai as genai
import dateutil.parser as parser
import get_redirected_link
import traceback
import inspect
import get_final_url_with_selenium
from gnews import GNews

TOPICS = ["WORLD", "NATION", "BUSINESS", "TECHNOLOGY", "ENTERTAINMENT", "SPORTS", "SCIENCE", "HEALTH"]


def create_today_folder():
    # Create a folder with today's date formatted as %Y%m%d inside 'imgs/'
    today_date = datetime.now().strftime("%Y%m%d")
    folder_path = os.path.join("imgs", today_date)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


def convert_date_to_supabase(given_date):
    published_date = parser.parse(given_date).isoformat()
    return published_date


def generate_content(article_text):
    try:
        print("Generating the summary.....")

        api_key = "AIzaSyCWexOEMVgiIViLc8oLnZ3HLcBmrt2-g9w"
        model_name = "gemini-1.5-pro"
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 512,
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config,
                                      safety_settings=safety_settings)

        response = model.generate_content(f"Please summarize this news article or title into a 7 to 10 very small "
                                          f"paragraphs. dont reference yourself, dont replay with Paragraph 1, "
                                          f"no headings, no titles, no numbers, no dots, no points, just the paragraph's"
                                          f" {article_text}")
        print(response.text)
        return response.text
    except Exception as e:
        print(f"An exception occurred: {e}")
        print(f"Current line number: {inspect.currentframe().f_lineno}")
        traceback.print_exc()
        return ""


def generate_content1(article_text):
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

        prompt = """
        # News Article Summarization Prompt

        Create a compelling news summary script for a video that will be shared on YouTube and TikTok. The script should:

        1. START WITH A HOOK (10-15 seconds): Begin with an attention-grabbing statement, surprising fact, or provocative question from the article to immediately capture viewer interest.

        2. MAIN SUMMARY (45-60 seconds): Clearly explain the key points of the news article, maintaining journalistic integrity while highlighting the most compelling aspects.

        3. CONCLUSION (10-15 seconds): End with an impactful takeaway or thoughtful reflection that leaves viewers satisfied.

        FORMAT REQUIREMENTS:
        - Total length must be EXACTLY 1000 characters
        - Write in the style of a professional news anchor
        - Use natural speech patterns suitable for text-to-speech conversion
        - Include appropriate pauses (indicated by commas and periods)
        - Avoid complex words that might be mispronounced by TTS systems
        - Incorporate a balanced tone appropriate to the subject matter
        - Do not use any abbreviated or shortened words - write everything out in full (example: "cannot" instead of "can't", "would not" instead of "wouldn't", etc.)

        Remember that the first 10 seconds are crucial for retention - make them compelling enough that viewers will want to watch the entire video.
        """
        response = model.generate_content(f" {prompt} {article_text}")

        # print(response.parts)
        # print(response.parts[0].text)
        # Access the generated content
        # def get_generated_text(response):
        try:
            # Try to get generated text from response.parts
            generated_text = response.parts[0].text if response.parts else response.text
            print(f"Current line number: {inspect.currentframe().f_lineno}")
            traceback.print_exc()
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


article_text = """
U.S. stocks rallied on Friday after the all-important jobs data came in much stronger than economists expected.

The Dow Jones Industrial Average
 traded 242 points higher, or 0.6%. The S&P 500
 climbed 0.7%, and the Nasdaq Composite
 rose 1.1%.

Nonfarm payrolls grew by 254,000 jobs in September, far outpacing the forecasted gain of 150,000 from economists polled by Dow Jones. The unemployment rate ticked down to 4.1% despite expectations for it to hold steady at 4.2%.

Friday’s advances mark a turn after mounting geopolitical tensions in the Middle East gave way to a shaky start in October for stocks. The gains pulled the three major indexes near flat for the week, underscoring the strength of Friday’s rebound.

“After a summer of weak labor data readings, this is a reassuring reading that the U.S. economy remains resilient, supported by a healthy labor market,” said Michelle Cluver, head of ETF model portfolios at Global X. “We remain in an environment where good economic news is good news for the equity market as it increases the potential for a soft landing.”
"""


# print(generate_content2(article_text))

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

# get_full_article(news_url)
# Example usage
# url = "https://news.google.com/rss/articles/CBMifkFVX3lxTE1pbjl2bkJRUG56cEZNN19uSzlySnFMMHJEY2ZDZVZmVnJJcjk1ZGxyNF82RWJxREMwclVwNmlySlFtTnJpdGtWWHlDZmhMYzRnbFNoZEJSekxhZGs0Yk9EY21iekVfci1jNE9YRG4wcXkydW9LVURRV0swb3ZfZw?oc=5"
# get_full_article = get_full_article(url)
# print(f"Redirected link: {get_full_article}")
def get_full_article1(news_url):
    print("Getting full article details.....")
    first_article = Article(url=news_url, fetch_images=True, keep_article_html=True)
    first_article.download()
    first_article.parse()

    newstext = first_article.text
    top_image = first_article.top_image
    article_html = first_article.article_html
    canonical_link = first_article.canonical_link

    return newstext, top_image, article_html, canonical_link


def get_recent_news(returned_records):
    print("Getting recent news.....")

    gn = GoogleNews(lang='en', country='US')
    json_data = gn.top_news()
    entries = json_data.get("entries", [])
    print(len(entries))

    return entries[:returned_records]


# get_recent_news(1)


def get_recent_news1():
    print("Getting recent news.....")

    gn = GoogleNews(lang='en', country='US')
    json_data = gn.top_news()
    entries = json_data.get("entries", [])
    print(len(entries))

    return entries


def get_recent_news2():
    print("Getting recent news.....")

    gn = GoogleNews(lang='en', country='UK')
    json_data = gn.geo_headlines(geo='UK')
    entries = json_data.get("entries", [])
    # print(entries)
    # print(len(entries))

    return entries


def get_news_by_topic(topic, returned_records):
    print("Getting news by topics.....")

    gn = GoogleNews(lang='en', country='US')
    json_data = gn.topic_headlines(topic)
    entries = json_data.get("entries", [])

    return entries[:returned_records]


def get_news_by_topic1(topic):
    print("Getting news by topics.....")

    gn = GoogleNews(lang='en', country='US')
    json_data = gn.topic_headlines(topic)
    entries = json_data.get("entries", [])

    return entries


def get_today_trending_news():
    try:
        google_news = GNews()
        trending_news = google_news.get_top_news()
        # print(trending_news)
        return trending_news
    except Exception as e:
        print(f"Error fetching trending news: {e}")
        return None


# get_today_trending_news()


def extract_data(entry):
    print("extracting news details......")

    newstext, top_image, article_html, canonical_link = "", "", "", ""
    print(entry)
    try:
        link = entry.get("link")
        newlink = get_redirected_link.get_redirected_link(link)
        result = get_full_article(newlink)

        if result:
            newstext, top_image, article_html, canonical_link = result
    except Exception as e:
        print(e)
    title = entry.get("title")
    sep = '-'
    title_stripped = title.rsplit(sep, 1)[0]

    data = {
        "title": title_stripped,
        "date": entry.get("published"),
        "summary": generate_content1(entry.get("title") + newstext),
        "image": top_image,
        "website": entry["source"].get("href"),
        "link": entry.get("link")
    }

    # res = posttosupabase.insert_data_into_table(table_name="news_article", data=data)

    return data


def extract_data2(entry):
    print("extracting news details......")

    newstext, top_image, article_html, canonical_link = "", "", "", ""
    # print(entry)
    try:
        link = entry.get("link")
        newlink = get_redirected_link.get_redirected_link(link)
        result = get_full_article(newlink)

        if result:
            newstext, top_image, article_html, canonical_link = result
    except Exception as e:
        print(e)
    title = entry.get("title")
    sep = '-'
    title_stripped = title.rsplit(sep, 1)[0]

    data = {
        "title": title_stripped,
        "newstext": newstext,
        # "summary": generate_content(entry.get("title") + newstext),
        "image": top_image,
        # "website": entry["source"].get("href"),
        # "link": entry.get("link")
    }

    # res = posttosupabase.insert_data_into_table(table_name="news_article", data=data)

    return data


def extract_data3(entry):
    print("extracting news details......")

    newstext, top_image, article_html, canonical_link = "", "", "", ""
    print(entry)
    try:
        link = entry.get("link")
        newlink = get_redirected_link.get_redirected_link(link)
        result = get_full_article(newlink)

        if result:
            newstext, top_image, article_html, canonical_link = result
    except Exception as e:
        print(e)
    title = entry.get("title")
    sep = '-'
    title_stripped = title.rsplit(sep, 1)[0]

    data = {
        "title": title_stripped,
        "date": entry.get("published"),
        "summary": generate_content(entry.get("title") + newstext),
        "image": top_image,
        "website": entry["source"].get("href"),
        "link": entry.get("link")
    }

    # res = posttosupabase.insert_data_into_table(table_name="news_article", data=data)

    return newstext


def extract_data4(entry):
    print("extracting news details......")

    newstext, top_image, article_html, canonical_link = "", "", "", ""
    print(entry)
    try:
        link = entry.get("link")
        newlink = get_redirected_link.get_redirected_link(link)
        result = get_full_article(newlink)

        if result:
            newstext, top_image, article_html, canonical_link = result
    except Exception as e:
        print(e)
    title = entry.get("title")
    sep = '-'
    title_stripped = title.rsplit(sep, 1)[0]

    summary = generate_content1(entry.get("title") + newstext)
    summary2 = summary + "If you like our content, don't forget to like and subscribe to our channel, NEWS TODAY."
    data = {
        "title": title_stripped,
        "date": entry.get("published"),
        "summary": summary2,
        "image": top_image,
        "website": entry["source"].get("href"),
        "link": entry.get("link")
    }

    # res = posttosupabase.insert_data_into_table(table_name="news_article", data=data)

    return data


# def extract_data5(entry):
#     print("extracting news details......")
#
#     newstext, top_image, article_html, canonical_link = "", "", "", ""
#     print(entry)
#     try:
#         link = entry.get("link")
#         newlink = get_final_url_with_selenium.get_final_url_with_selenium(link)
#         result = get_full_article(newlink)
#
#         if result:
#             newstext, top_image, article_html, canonical_link = result
#     except Exception as e:
#         print(e)
#     title = entry.get("title")
#     sep = '-'
#     title_stripped = title.rsplit(sep, 1)[0]
#
#     summary = generate_content1(entry.get("title") + newstext)
#     summary2 = summary + "If you like our content, don't forget to like and subscribe to our channel, NEWS TODAY."
#     data = {
#         "title": title_stripped,
#         "date": entry.get("published"),
#         "summary": summary2,
#         "image": top_image,
#         "website": entry["source"].get("href"),
#         "link": entry.get("link")
#     }
#
#     # res = posttosupabase.insert_data_into_table(table_name="news_article", data=data)
#
#     return data


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
    summary = generate_content1(entry.get("title") + description + newstext)
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


# # # Get recent news
# recent_news_entries = get_recent_news(1)
# # Extract data for each entry
# extracted_data = [extract_data3(entry) for entry in recent_news_entries]
# print(extracted_data)


def run():
    # Create today's folder inside 'imgs/'
    folder_name = create_today_folder()

    # Set the output path to be within the created folder
    output_path = os.path.join(folder_name, "news.json")

    # Get recent news
    recent_news_entries = get_recent_news()
    # Extract data for each entry
    extracted_data = [extract_data(entry, "Recent") for entry in recent_news_entries]

    # Save the search results as a JSON file
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)

    # Run all Topics news
    # for topic in TOPICS:
    #     # Get recent news
    #     recent_news_entries = get_news_by_topic(topic)
    #
    #     # Extract data for each entry
    #     extracted_data = [extract_data(entry, topic) for entry in recent_news_entries]
    #
    #     # Set the output path to be within the created folder
    #     output_path = os.path.join(folder_name, f"{topic}.json")
    #
    #     # Save the search results as a JSON file
    #     with open(output_path, 'w', encoding='utf-8') as json_file:
    #         json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)

    # # run only some Topics news
    # indices = [0, 3, 5]
    # for i in indices:
    #     print(TOPICS[i])
    #
    #     # Get recent news
    #     recent_news_entries = get_news_by_topic(TOPICS[i])
    #
    #     # Extract data for each entry
    #     extracted_data = [extract_data(entry, TOPICS[i]) for entry in recent_news_entries]
    #
    #     # Set the output path to be within the created folder
    #     output_path = os.path.join(folder_name, f"{TOPICS[i]}.json")
    #
    #     # Save the search results as a JSON file
    #     with open(output_path, 'w', encoding='utf-8') as json_file:
    #         json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)


# run()
def run2(returned_records):
    # Get today's date in the format YYYYMMDD
    today_date = datetime.now().strftime("%Y%m%d")

    # Create the directory structure
    base_folder = "news_videos"
    date_folder = os.path.join(base_folder, today_date)
    os.makedirs(date_folder, exist_ok=True)

    # Set the output path to be within the created folder
    output_path = os.path.join(date_folder, "news.json")

    # Get recent news
    recent_news_entries = get_recent_news(returned_records)
    # Extract data for each entry
    extracted_data = [extract_data(entry, "Recent") for entry in recent_news_entries]

    # Save the search results as a JSON file
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)


# run2(returned_records=1)

def run_topics():
    # Get today's date in the format YYYYMMDD
    today_date = datetime.now().strftime("%Y%m%d")

    # Create the directory structure
    base_folder = "news_videos"
    date_folder = os.path.join(base_folder, today_date)

    # Set the output path to be within the created folder
    # output_path = os.path.join(date_folder, "news.json")

    # Run all Topics news
    for topic in TOPICS:
        folders_path = os.path.join(date_folder, topic)
        os.makedirs(folders_path, exist_ok=True)
        # Get recent news
        recent_news_entries = get_news_by_topic(topic, 3)

        # Extract data for each entry
        extracted_data = [extract_data(entry, topic) for entry in recent_news_entries]

        # Set the output path to be within the created folder
        output_path = os.path.join(folders_path, f"{topic}.json")

        # Save the search results as a JSON file
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)


# run_topics()


def run_save_to_sheets():
    # Create today's folder inside 'imgs/'
    folder_name = create_today_folder()

    # Set the output path to be within the created folder
    output_path = os.path.join(folder_name, "news.json")

    # Get recent news
    recent_news_entries = get_recent_news()
    # Extract data for each entry
    extracted_data = [extract_data(entry, "Recent") for entry in recent_news_entries]

    # Save the search results as a JSON file
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)

    # Run all Topics news
    for topic in TOPICS:
        # Get recent news
        recent_news_entries = get_news_by_topic(topic)

        # Extract data for each entry
        extracted_data = [extract_data(entry, topic) for entry in recent_news_entries]

        # Set the output path to be within the created folder
        output_path = os.path.join(folder_name, f"{topic}.json")

        # Save the search results as a JSON file
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)
