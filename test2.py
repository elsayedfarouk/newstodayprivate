import os

import googlesheet
from newspaper import Article
import google.generativeai as genai
import traceback
import get_final_url_with_selenium
from gnews import GNews


class NewsProcessor:
    def __init__(self, country='US', language='en', max_results=10):
        self.google_news = GNews(language=language, country=country, max_results=max_results)
        self.country = country
        self._configure_gemini()

    def _configure_gemini(self):
        # Get the secret from environment variable
        gemini_api_key = os.getenv("gemini_api_key")
        """Configure Gemini AI for content generation"""
        api_key = gemini_api_key
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
        print(f"Extracting article content from: {news_url}")

        # Return empty content if URL is None or empty
        if not news_url:
            print("No URL provided")
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
            print(f"Error extracting article: {e}")
            return {'text': '', 'top_image': '', 'html': '', 'canonical_link': ''}

    def generate_summary(self, content):
        """Generate AI summary of article content"""
        print("Generating summary...")
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
            print(f"Error generating summary: {e}")
            traceback.print_exc()
            return ""

    def process_news_entry(self, entry):
        """Process a single news entry into structured data"""
        print("Processing news entry...")

        # Validate entry
        if not entry:
            print("No entry provided")
            return None

        try:
            # Get URLs safely
            original_url = entry.get("url")
            if not original_url:
                print("No URL found in entry")
                return None

            print(f"Original URL: {original_url}")

            # Get final URL with error handling
            try:
                final_url = get_final_url_with_selenium.get_final_url_with_selenium(original_url)
                if not final_url:
                    print("Failed to get final URL, using original")
                    final_url = original_url
            except Exception as e:
                print(f"Error getting final URL: {e}, using original")
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
                "link": original_url
            }

        except Exception as e:
            print(f"Error processing entry: {e}")
            import traceback
            traceback.print_exc()
            return None

    def save_to_sheet(self, news_data, category, test_mode=False):
        """Save news data to Google Sheet"""
        if not news_data:
            return

        row_data = [
            "pending",  # status
            category,
            self.country,
            news_data["title"],
            news_data["date"],
            news_data["summary"],
            news_data["image"],
            news_data["website"],
            news_data["link"]
        ]

        if test_mode:
            print("📋 TEST MODE - Would save to sheet:")
            print(f"   Status: {row_data[0]}")
            print(f"   Category: {row_data[1]}")
            print(f"   Country: {row_data[2]}")
            print(f"   Title: {row_data[3]}")
            print(f"   Date: {row_data[4]}")
            print(f"   Summary: {row_data[5][:100]}...")
            print(f"   Image: {row_data[6]}")
            print(f"   Website: {row_data[7]}")
            print(f"   Link: {row_data[8]}")
            return

        try:
            googlesheet.add_row_to_sheet(row_data, "NewsToday", "News")
        except Exception as e:
            print(f"❌ Error saving to Google Sheet: {e}")
            print("💡 Tip: Check your Google Sheets credentials configuration")

    def process_latest_news(self):
        """Process and save latest news"""
        print("Processing latest news...")
        latest_entries = self.fetch_latest_news()

        for entry in latest_entries[:1]:  # Process only first entry
            try:
                news_data = self.process_news_entry(entry)
                if news_data:
                    self.save_to_sheet(news_data, "Latest")
            except Exception as e:
                print(f"Error processing latest news: {e}")

    def process_topic_news(self):
        """Process and save news by topics"""
        print("Processing topic news...")
        topics = ["WORLD", "NATION", "BUSINESS", "TECHNOLOGY", "ENTERTAINMENT", "SPORTS", "SCIENCE", "HEALTH"]

        for topic in topics:
            print(f"Processing {topic} news...")
            topic_entries = self.fetch_news_by_topic(topic)

            for entry in topic_entries[:3]:  # Process first 3 entries per topic
                try:
                    news_data = self.process_news_entry(entry)
                    if news_data:
                        self.save_to_sheet(news_data, topic)
                except Exception as e:
                    print(f"Error processing {topic} news: {e}")


def main():
    """Main execution function"""
    processor = NewsProcessor(country='US')

    print("=== TESTING WITH 1 NEWS ARTICLE ===")

    # Get latest news entries
    latest_entries = processor.fetch_latest_news()

    if not latest_entries:
        print("No news entries found")
        return

    print(f"Found {len(latest_entries)} news entries")
    print("Processing first entry only for testing...")

    # Process only the first entry for testing
    first_entry = latest_entries[0]
    print(f"Entry data: {first_entry}")

    try:
        news_data = processor.process_news_entry(first_entry)
        if news_data:
            print("✅ Successfully processed news entry:")
            print(f"Title: {news_data['title']}")
            print(f"Date: {news_data['date']}")
            print(f"Summary length: {len(news_data['summary'])} characters")
            print(f"Image: {news_data['image']}")
            print(f"Website: {news_data['website']}")

            # Save to sheet in TEST MODE (won't actually save due to credentials issue)
            processor.save_to_sheet(news_data, "Latest", test_mode=True)
            print("✅ Test completed successfully")
        else:
            print("❌ Failed to process news entry")
    except Exception as e:
        print(f"❌ Error in main processing: {e}")
        import traceback
        traceback.print_exc()


def main_production():
    """Production function - use this when Google Sheets credentials are fixed"""
    processor = NewsProcessor(country='US')

    # Process latest news
    processor.process_latest_news()

    # Uncomment to process topic news
    # processor.process_topic_news()


if __name__ == "__main__":
    main()