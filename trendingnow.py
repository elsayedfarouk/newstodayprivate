import os
import html
import random
import string
from datetime import datetime
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import requests
from newspaper import Article
import google.generativeai as genai
from moviepy.editor import AudioFileClip
import tts
import googlesheet
import genvideos
from publish_tiktok_video import publish_tiktok_video, TIKTOK_ACCOUNT_ID


def download_image(image_path_url, output_image_path):
    print(f"[Image Download] Starting download from: {image_path_url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    response = requests.get(image_path_url, headers=headers, stream=True)
    response.raise_for_status()

    with open(output_image_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print(f"[Image Download] Successfully saved image to: {output_image_path}")
    return output_image_path


def generate_unique_string(length=10):
    characters = string.ascii_letters + string.digits
    if length > len(characters):
        raise ValueError("Length exceeds the number of unique characters available.")
    unique_string = ''.join(random.sample(characters, length))
    return unique_string


class TrendingNewsProcessor:
    def __init__(self, country='US', language='en'):
        print(f"[Init] Initializing TrendingNewsProcessor (Country: {country}, Language: {language})")
        self.country = country
        self.language = language
        self.ht_ns = "https://trends.google.com/trending/rss"
        self.ns = {'ht': self.ht_ns}
        self._configure_gemini()

    def _configure_gemini(self):
        """Configure Gemini AI for content generation"""
        print("[Gemini AI] Configuring Gemini API client (model: gemma-3-27b-it)...")
        api_key = os.getenv("gemini_api_key")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-3.5-flash-lite",
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
        )
        print("[Gemini AI] Gemini model configured successfully.")

    def fetch_trending_items(self):
        """Fetch trending items from Google Trends RSS feed"""
        rss_url = f"https://trends.google.com/trending/rss?geo={self.country}"
        print(f"[Trends Feed] Fetching Google Trends RSS from: {rss_url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        response = requests.get(rss_url, headers=headers, timeout=30)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        items = root.findall(".//item")
        print(f"[Trends Feed] Successfully retrieved {len(items)} trending items.")
        return items

    def extract_article_content(self, news_url):
        """Extract full article content from URL"""
        if not news_url:
            print("[Article Extraction] Empty URL provided. Skipping extraction.")
            return {'text': '', 'top_image': '', 'html': '', 'canonical_link': '', 'title': '', 'publish_date': ''}

        print(f"[Article Extraction] Downloading & parsing article: {news_url}")
        try:
            article = Article(url=news_url, fetch_images=True, keep_article_html=True)
            article.download()
            article.parse()

            text_len = len(article.text) if article.text else 0
            has_image = bool(article.top_image)
            print(f"[Article Extraction] Success! Parsed {text_len} text characters. Top image found: {has_image}")

            return {
                'text': article.text or '',
                'top_image': article.top_image or '',
                'html': article.article_html or '',
                'canonical_link': article.canonical_link or '',
                'title': article.title or '',
                'publish_date': str(article.publish_date) if article.publish_date else ''
            }
        except Exception as e:
            print(f"[Article Extraction Error] Failed to extract from {news_url}: {e}")
            return {'text': '', 'top_image': '', 'html': '', 'canonical_link': '', 'title': '', 'publish_date': ''}

    def generate_summary(self, content):
        """Generate AI summary of article content"""
        print(f"[Gemini AI] Sending content to Gemini for anchor-style summary ({len(content)} characters)...")
        try:
            prompt = f"""
            You are a professional news anchor.

            TASK:
            Summarize the following news article as a broadcast-ready news report.

            STRICT RULES:
            - Output ONLY the summary text.
            - Do NOT include introductions, conclusions, explanations, or meta comments.
            - Do NOT say phrases like:
              "Here’s a news report"
              "This article discusses"
              "In summary"
              "Good evening" or "Good morning"
            - Do NOT address the audience.
            - Do NOT mention liking, subscribing, or the channel.
            - Write in a neutral, professional news anchor tone.
            - Ensure smooth flow suitable for text-to-speech.
            - Length must be approximately 1000 characters.

            OUTPUT FORMAT:
            - Plain text only.
            - No quotes.
            - No headings.
            - No extra lines before or after the summary.

            NEWS ARTICLE:
            {content}
            """

            response = self.model.generate_content(prompt)

            summary = None
            # Extract generated text with fallback methods
            if response.parts:
                summary = response.parts[0].text
            elif hasattr(response, 'text'):
                summary = response.text
            elif response.candidates:
                summary = response.candidates[0].content.parts[0].text

            if summary:
                print(f"[Gemini AI] Summary successfully generated ({len(summary)} characters).")
            else:
                print("[Gemini AI Error] Response received but text could not be extracted.")
            return summary

        except Exception as e:
            print(f"[Gemini AI Error] Error calling Gemini API: {e}")
            return None

    def generate_tiktok_caption(self, title: str, summary: str, trend_keyword: str = "") -> str:
        """Generate an SEO-optimized TikTok video caption using Gemini (targeting 1,980 - 2,180 characters, max 2,200)."""
        print(f"[Gemini AI] Generating SEO-optimized TikTok caption for '{title}'...")
        try:
            prompt = f"""
            You are a top social media strategist and SEO expert for a viral TikTok news channel named "NEWS TODAY".

            TASK:
            Create a highly engaging, SEO-optimized, and visually formatted TikTok video caption based on the following news story.

            REQUIREMENTS & GUIDELINES:
            1. LENGTH REQUIREMENT (STRICT):
               - Total caption length MUST be between 1,980 and 2,150 characters (at least 90% of TikTok's 2,200 character limit).
               - DO NOT exceed 2,200 characters under any circumstances.

            2. STRUCTURE & CONTENT:
               - 💥 Catchy Headline & Hook: Start with a powerful hook, news headline, and relevant emojis to stop the scroll.
               - 📰 Detailed News Story Breakdown: Provide an in-depth breakdown covering key details, background context, quotes/facts, and implications using bullet points and readable paragraphs.
               - 💬 High-Engagement Call to Action (CTA): Ask thought-provoking questions, invite viewers to share their opinion in the comments, and follow @NewsToday for daily breaking news.
               - 🏷️ Comprehensive SEO Hashtag Block: Include a dense, highly relevant list of trending and niche hashtags (e.g. #NewsToday, #BreakingNews, #Trending, topic-specific tags, names, organizations, and viral tags).

            3. TONE & STYLE:
               - Professional yet conversational, viral, and easily readable on mobile.
               - Rich with formatting (bullet points, emojis, clean line breaks).

            NEWS TITLE:
            {title}

            TREND / TOPIC:
            {trend_keyword}

            NEWS SUMMARY / CONTEXT:
            {summary}

            OUTPUT FORMAT:
            - Output ONLY the ready-to-post caption text.
            - Do NOT include any intro/outro explanations, character count notes, or markdown fences (no ```).
            """

            response = self.model.generate_content(prompt)

            caption = None
            if response.parts:
                caption = response.parts[0].text
            elif hasattr(response, 'text'):
                caption = response.text
            elif response.candidates:
                caption = response.candidates[0].content.parts[0].text

            if caption:
                caption = caption.strip()
                if caption.startswith("```") and caption.endswith("```"):
                    lines = caption.splitlines()
                    caption = "\n".join(lines[1:-1]).strip()

                # Strictly enforce TikTok's 2,200 character ceiling
                if len(caption) > 2200:
                    print(f"[Gemini AI Warning] Caption exceeded 2200 chars ({len(caption)} chars). Safely truncating.")
                    caption = caption[:2195].rsplit(" ", 1)[0]

                print(f"[Gemini AI] TikTok caption successfully generated ({len(caption)} characters).")
                return caption
            else:
                print("[Gemini AI Error] Response received but caption text could not be extracted.")
                return title

        except Exception as e:
            print(f"[Gemini AI Error] Error generating TikTok caption: {e}")
            return title


    def process_trend_item(self, item):
        """Process a single Google Trends item into structured news data"""
        if item is None:
            return None

        try:
            trend_keyword = item.findtext("title") or "Unknown Trend"
            approx_traffic = item.findtext("ht:approx_traffic", namespaces=self.ns) or "N/A"
            rss_picture = item.findtext("ht:picture", namespaces=self.ns) or ""
            pub_date = item.findtext("pubDate") or ""
            news_items = item.findall("ht:news_item", namespaces=self.ns)

            print(f"\n" + "-" * 50)
            print(f"[Trend Item] Processing Trend: '{trend_keyword}' (Approx Traffic: {approx_traffic})")
            print(f"[Trend Item] Related news articles found: {len(news_items)}")

            for idx, news_item in enumerate(news_items, 1):
                try:
                    news_url = news_item.findtext("ht:news_item_url", namespaces=self.ns)
                    if not news_url:
                        print(f"[Trend Item] News item #{idx} has no URL. Skipping.")
                        continue

                    news_title = news_item.findtext("ht:news_item_title", namespaces=self.ns) or ""
                    news_title = html.unescape(news_title)

                    news_snippet = news_item.findtext("ht:news_item_snippet", namespaces=self.ns) or ""
                    news_snippet = html.unescape(news_snippet)

                    news_source = news_item.findtext("ht:news_item_source", namespaces=self.ns) or ""

                    print(f"[Trend Item] News item #{idx}: '{news_title}' (Source: {news_source})")
                    print(f"[Trend Item] News URL: {news_url}")

                    # Extract article content directly from news_url
                    article_content = self.extract_article_content(news_url)

                    # Determine title
                    title = news_title or article_content.get('title') or trend_keyword
                    clean_title = title.rsplit('-', 1)[0].strip() if '-' in title else title

                    # Prepare content for summary
                    title_part = title if title else ""
                    snippet_part = news_snippet if news_snippet else ""
                    text_part = article_content.get('text', "") if article_content else ""

                    content_for_summary = f"{title_part} {snippet_part} {text_part}".strip()

                    if not content_for_summary:
                        print(f"[Trend Item] No text content available to summarize for news item #{idx}.")
                        continue

                    summary = self.generate_summary(content_for_summary)
                    if not summary:
                        print(f"[Trend Item] Failed to generate summary for news item #{idx}. Trying next item.")
                        continue

                    summary_with_cta = (
                        f"{summary} If you like our content, don't forget to like and subscribe to our channel, NEWS TODAY."
                    )

                    image_url = article_content.get('top_image', '') or rss_picture
                    parsed_url = urlparse(news_url)
                    website = parsed_url.netloc or news_source

                    print(f"[Trend Item] Successfully structured news data for '{clean_title}'.")
                    return {
                        "title": clean_title,
                        "date": pub_date or article_content.get('publish_date', ''),
                        "summary": summary_with_cta,
                        "image": image_url,
                        "website": website,
                        "link": news_url,
                        "trend": trend_keyword,
                        "traffic": approx_traffic
                    }

                except Exception as inner_e:
                    print(f"[Trend Item Error] Error processing news item #{idx} in trend '{trend_keyword}': {inner_e}")
                    continue

            print(f"[Trend Item] No usable news items found for trend: '{trend_keyword}'")
            return None

        except Exception as e:
            print(f"[Trend Item Error] Error processing trend item: {e}")
            return None

    def save_to_sheet(self, news_data, category, videourl, spreadsheet_name, sheet_name):
        """Save news data to Google Sheet"""
        print(f"\n[Google Sheet] Preparing to save record to Google Sheets...")
        print(f"[Google Sheet] Target Spreadsheet: '{spreadsheet_name}', Sheet: '{sheet_name}'")
        print(f"[Google Sheet] Data Summary: Title='{news_data.get('title')}', Video='{videourl}'")

        if not news_data:
            print("[Google Sheet Error] news_data is empty. Skipping save.")
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
                news_data.get("link"),
                videourl
            ]
        ]

        try:
            googlesheet.add_row_to_sheet(row_data, spreadsheet_name, sheet_name)
            print(f"[Google Sheet] Successfully added new row to '{sheet_name}'.")
        except Exception as e:
            print(f"[Google Sheet Error] Failed saving to Google Sheet: {e}")

    def process_trending_news(self, spreadsheet_name='TrendingNewsToday', sheet_name='Trending', voice='am_adam', videooption=2, limit=10):
        """Process trending news and generate videos using the same workflow as mainfile.py"""
        print("\n" + "=" * 60)
        print("[Trending Pipeline] Starting Trending News Video Generation")
        print(f"[Trending Pipeline] Config: Spreadsheet='{spreadsheet_name}', Sheet='{sheet_name}', Voice='{voice}', Limit={limit}")
        print("=" * 60)

        trend_items = self.fetch_trending_items()

        for idx, item in enumerate(trend_items[:limit], 1):
            print(f"\n>>> Checking Candidate Trend {idx}/{min(len(trend_items), limit)} <<<")
            try:
                news_data = self.process_trend_item(item)
                if news_data:
                    image_path_url = news_data.get("image")
                    title = news_data.get("title")
                    summary = news_data.get("summary")
                    website = news_data.get("website")

                    # Check if any of the required fields are empty
                    if not title or not summary or not image_path_url:
                        print("[Pipeline Validation Error] Missing required title, summary, or image.")
                        print(f"  Title: {bool(title)} | Summary: {bool(summary)} | Image URL: {bool(image_path_url)}")
                    else:
                        summary = summary.strip()
                        if len(summary) < 150:
                            print(f"[Pipeline Validation] Summary is too short ({len(summary)} chars < 150 chars minimum). Skipping.")
                        else:
                            link = news_data.get("link", "")
                            print(f"[Duplicate Check] Checking if story or link already exists in spreadsheet '{spreadsheet_name}'...")
                            already_exists = False
                            try:
                                title_exists = googlesheet.check_text_in_column_a(spreadsheet_name, title, 4)
                                link_exists = googlesheet.check_text_in_column_a(spreadsheet_name, link, 9) if link else False
                                already_exists = title_exists or link_exists
                            except Exception as check_err:
                                print(f"[Duplicate Check Warning] Could not verify duplicate in sheet '{spreadsheet_name}': {check_err}")
                                already_exists = False

                            if already_exists:
                                print(f"[Duplicate Found] Story or link already exists in Google Sheet. Skipping:\n  Title: '{title}'\n  Link: '{link}'")
                            else:
                                print(f"[New Story Confirmed] Story is unique. Starting video creation for: '{title}'")

                                # Get today's date in format YYYYMMDD
                                today_date = datetime.now().strftime("%Y%m%d")
                                base_folder = "news_videos"
                                date_folder = os.path.join(base_folder, today_date)
                                os.makedirs(date_folder, exist_ok=True)
                                print(f"[Directory] Output folder ready: {date_folder}")

                                filename = generate_unique_string()
                                print(f"[ID Generation] Unique asset filename: {filename}")

                                # Download Image
                                output_image_path = f"news_videos/{today_date}/{filename}.png"
                                image_path = download_image(image_path_url, output_image_path)

                                # Synthesize Voice
                                generate_speech_output_path = f"news_videos/{today_date}/{filename}.wav"
                                print(f"[TTS Synthesis] Generating speech audio using voice '{voice}'...")
                                generate_speech = tts.process_text(summary, voice, generate_speech_output_path, speed=1.0)
                                print(f"[TTS Synthesis] Audio file created: {generate_speech}")

                                # Load audio and check duration
                                audio_clip = AudioFileClip(generate_speech)
                                duration_sec = audio_clip.duration
                                print(f"[Audio Analysis] Audio length: {duration_sec:.2f} seconds")

                                # Render Video (Short/Vertical format)
                                print(f"[Video Rendering] Beginning video generation (Short/Vertical format)...")
                                genvideos.main(output_image_path, title, generate_speech, website, filename)
                                print(f"[Video Rendering] Video generation completed for '{filename}.mp4'.")

                                # Video file path
                                videourl = f"news_videos/{today_date}/{filename}.mp4"

                                # Save to Sheet
                                self.save_to_sheet(news_data, "Trending", videourl, spreadsheet_name, sheet_name)

                                # Publish to TikTok
                                print(f"\n[TikTok Publishing] Generating SEO-optimized caption & publishing video to TikTok...")
                                try:
                                    tiktok_caption = self.generate_tiktok_caption(
                                        title=title,
                                        summary=summary,
                                        trend_keyword=news_data.get("trend", "")
                                    )
                                    publish_tiktok_video(
                                        video_path=videourl,
                                        caption=tiktok_caption,
                                        tiktok_account_id=TIKTOK_ACCOUNT_ID,
                                    )
                                    print(f"[TikTok Publishing] Video published to TikTok successfully.")
                                except Exception as tt_err:
                                    print(f"[TikTok Publishing Error] Failed to publish video to TikTok: {tt_err}")

                                print("\n" + "=" * 60)
                                print(f"[Pipeline Success] Video successfully generated and recorded for trend: '{title}'!")
                                print("=" * 60 + "\n")
                                break

            except Exception as e:
                print(f"[Pipeline Error] Error occurred during processing of item {idx}: {e}")


# Aliases for flexibility and compatibility with other runners
NewsProcessor = TrendingNewsProcessor
TrendingProcessor = TrendingNewsProcessor


def main():
    """Main execution function"""
    voice = "am_adam"  # Change voice if needed (e.g. am_adam, bm_george)
    processor = TrendingNewsProcessor(country='US')
    processor.process_trending_news(
        spreadsheet_name='TrendingNewsToday',
        sheet_name='Trending',
        voice=voice,
        videooption=2
    )


if __name__ == "__main__":
    main()
