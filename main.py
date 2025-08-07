import os
import tts
import googlesheet
from newspaper import Article
import google.generativeai as genai
import genvideos
import get_final_url_with_selenium
from gnews import GNews
import random
import string
from datetime import datetime
import requests

import upload_folder_to_github

def download_image(image_path_url, output_image_path):
    # Define the output file path
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    # Download the image
    response = requests.get(image_path_url, headers=headers, stream=True)
    response.raise_for_status()  # Check if the request was successful

    with open(output_image_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    return output_image_path

def generate_unique_string(length=10):
    # Create a list of all possible characters (uppercase, lowercase, digits)
    characters = string.ascii_letters + string.digits

    # Ensure that the length requested does not exceed the number of available unique characters
    if length > len(characters):
        raise ValueError("Length exceeds the number of unique characters available.")

    # Randomly sample the characters without replacement
    unique_string = ''.join(random.sample(characters, length))

    return unique_string


class NewsProcessor:
    def __init__(self, country='US', language='en', max_results=10):
        self.google_news = GNews(language=language, country=country, max_results=max_results)
        self.country = country
        self._configure_gemini()

    def _configure_gemini(self):
        """Configure Gemini AI for content generation"""
        api_key = "AIzaSyCWexOEMVgiIViLc8oLnZ3HLcBmrt2-g9w"
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-8b",
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
        )

    def fetch_latest_news(self):
        """Fetch latest top news"""
        return self.google_news.get_top_news()

    def fetch_news_by_topic(self, topic):
        """Fetch news by specific topic"""
        return self.google_news.get_news(topic)

    def fetch_news_by_country(self, country_code):
        """Fetch news by country"""
        self.google_news.country = country_code.upper()
        return self.google_news.get_top_news()

    def extract_article_content(self, news_url):
        """Extract full article content from URL"""
        if not news_url:
            return {'text': '', 'top_image': '', 'html': '', 'canonical_link': ''}

        try:
            article = Article(url=news_url, fetch_images=True, keep_article_html=True)
            article.download()
            article.parse()

            return {
                'text': article.text or '',
                'top_image': article.top_image or '',
                'html': article.article_html or '',
                'canonical_link': article.canonical_link or ''
            }
        except Exception as e:
            return {'text': '', 'top_image': '', 'html': '', 'canonical_link': ''}

    def generate_summary(self, content):
        """Generate AI summary of article content"""
        try:
            prompt = (
                f"Summarize this news article in the style of a professional news anchor "
                f"delivering a report. The summary should be exactly 1000 characters long, "
                f"ensuring a natural flow suitable for text-to-speech conversion. {content}"
            )

            response = self.model.generate_content(prompt)

            # Extract generated text with fallback methods
            if response.parts:
                return response.parts[0].text
            elif hasattr(response, 'text'):
                return response.text
            elif response.candidates:
                return response.candidates[0].content.parts[0].text
            else:
                return ""

        except Exception as e:
            return ""

    def process_news_entry(self, entry):
        """Process a single news entry into structured data"""
        if not entry:
            return None

        try:
            # Get URLs safely
            original_url = entry.get("url")
            if not original_url:
                return None

            # Get final URL with error handling
            try:
                final_url = get_final_url_with_selenium.get_final_url_with_selenium(original_url)
                if not final_url:
                    final_url = original_url
            except Exception as e:
                final_url = original_url

            # Extract article content
            article_content = self.extract_article_content(final_url)

            # Clean title (remove source suffix)
            title = entry.get("title", "Untitled")
            clean_title = title.rsplit('-', 1)[0].strip() if '-' in title else title

            # Generate summary with safe content handling
            title_part = title if title else ""
            description_part = entry.get('description', "")
            text_part = article_content.get('text', "") if article_content else ""

            content_for_summary = f"{title_part} {description_part} {text_part}".strip()

            if content_for_summary:
                summary = self.generate_summary(content_for_summary)
            else:
                summary = "No content available for summary"

            summary_with_cta = f"{summary} If you like our content, don't forget to like and subscribe to our channel, NEWS TODAY."

            return {
                "title": clean_title,
                "date": entry.get("published date", ""),
                "summary": summary_with_cta,
                "image": article_content.get('top_image', '') if article_content else '',
                "website": entry.get("publisher", {}).get("href", "") if entry.get("publisher") else "",
                "link": final_url
            }

        except Exception as e:
            print(f"Error processing entry: {e}")
            return None

    def save_to_sheet(self, news_data, category):

        print(news_data)
        """Save news data to Google Sheet"""
        if not news_data:
            return

        row_data = [
            str(value) if value is not None else ""
            for value in [
                "pending",
                category,
                self.country,
                news_data.get("title"),
                news_data.get("date"),
                news_data.get("summary"),
                news_data.get("image"),
                news_data.get("website"),
                news_data.get("link")
            ]
        ]

        try:
            googlesheet.add_row_to_sheet(row_data, "NewsToday", "News")
        except Exception as e:
            print(f"Error saving to Google Sheet: {e}")

    def process_latest_news(self):
        """Process and save latest news"""
        latest_entries = self.fetch_latest_news()

        for entry in latest_entries[:3]:  # Process only first entry
            try:
                news_data = self.process_news_entry(entry)
                if news_data:

                    # Get today's date in the format YYYYMMDD
                    today_date = datetime.now().strftime("%Y%m%d")

                    # Create the directory structure
                    base_folder = "news_videos"
                    date_folder = os.path.join(base_folder, today_date)
                    os.makedirs(date_folder, exist_ok=True)

                    filename = generate_unique_string()

                    image_path_url = news_data["image"]
                    title = news_data["title"]
                    summary = news_data["summary"]
                    website = news_data["website"]
                    title = news_data["title"]

                    output_image_path = f"news_videos/{today_date}/{filename}.png"
                    image_path = download_image(image_path_url, output_image_path)


                    generate_speech_output_path = f"news_videos/{today_date}/{filename}.wav"
                    generate_speech = tts.process_text(summary, generate_speech_output_path, speed=1.0)

                    genvideos.main(output_image_path, title, generate_speech, website, filename)

                    self.save_to_sheet(news_data, "Latest")
                    output_video_path = f"news_videos/{today_date}"

                    upload_folder_to_github.run3(output_video_path)
            except Exception as e:
                print(f"Error processing latest news: {e}")

    def process_topic_news(self):
        """Process and save news by topics"""
        topics = ["WORLD", "NATION", "BUSINESS", "TECHNOLOGY", "ENTERTAINMENT", "SPORTS", "SCIENCE", "HEALTH"]

        for topic in topics:
            topic_entries = self.fetch_news_by_topic(topic)

            for entry in topic_entries[:3]:  # Process first 3 entries per topic
                try:
                    news_data = self.process_news_entry(entry)
                    if news_data:
                        # Get today's date in the format YYYYMMDD
                        today_date = datetime.now().strftime("%Y%m%d")

                        # Create the directory structure
                        base_folder = "news_videos"
                        date_folder = os.path.join(base_folder, today_date)
                        os.makedirs(date_folder, exist_ok=True)

                        self.save_to_sheet(news_data, topic)
                        filename = generate_unique_string()

                        image_path = news_data["image"]
                        title = news_data["title"]
                        summary = news_data["summary"]
                        website = news_data["website"]
                        title = news_data["title"]

                        generate_speech_output_path = f"news_videos/{today_date}/{filename}.wav"
                        generate_speech = tts.process_text(summary, generate_speech_output_path, speed=1.0)

                        genvideos.main(image_path, title, generate_speech, website, filename)

                except Exception as e:
                    print(f"Error processing {topic} news: {e}")


def main():
    """Main execution function"""
    processor = NewsProcessor(country='US')

    # Process latest news
    processor.process_latest_news()

    # Uncomment to process topic news
    # processor.process_topic_news()


if __name__ == "__main__":
    main()
