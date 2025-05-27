from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def get_final_url_with_selenium(url):
    """
    Follow redirects including JavaScript redirects to get the final URL

    Args:
        url (str): The Google News redirect URL

    Returns:
        str: The final destination URL after all redirects
    """
    # Configure Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    try:
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)

        # Load the URL
        driver.get(url)

        # Wait for redirects to complete (adjust time if needed)
        time.sleep(5)

        # Get the final URL
        final_url = driver.current_url

        # Close the browser
        driver.quit()

        return final_url

    except Exception as e:
        return f"Error: {e}"


# # Google News URL
# google_news_url = "https://news.google.com/rss/articles/CBMimAFBVV95cUxNV044Z1BhVFJJa1J3dWFWUU5tN3l2a1NQZFJQbjBzLXYxZGpsbXBVem9EaFlGc2ZYTkJ3VDFMZ1dGd3JYaUZDWjdEZG1sSFpYYWE0Y0h3V1hucm1oc2NSd1N5Tng3SDlJZDltTE1UOFpTdE51dFFQNE9admdYZ25GanJrSUhsRmdlYmhYYmlna09ncnpjS2hjaA?oc=5"
#
# # Get and print the final URL
# final_url = get_final_url_with_selenium(google_news_url)
# print(f"Original URL: {google_news_url}")
# print(f"Final URL: {final_url}")