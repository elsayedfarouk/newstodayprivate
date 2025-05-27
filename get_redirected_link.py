from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import traceback
import inspect


def get_redirected_link(url):
    try:
        # Set up the Chrome WebDriver
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        driver = webdriver.Chrome(service=service, options=options)

        # Open the URL
        driver.get(url)

        # Wait for the redirect to complete
        # time.sleep(5)  # Adjust the sleep time as necessary

        # Get the current URL after redirect
        redirected_url = driver.current_url

        # Close the WebDriver
        driver.quit()

        return redirected_url
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Current line number: {inspect.currentframe().f_lineno}")
        traceback.print_exc()
        return None


# Example usage
url = "https://news.google.com/rss/articles/CBMifkFVX3lxTE1pbjl2bkJRUG56cEZNN19uSzlySnFMMHJEY2ZDZVZmVnJJcjk1ZGxyNF82RWJxREMwclVwNmlySlFtTnJpdGtWWHlDZmhMYzRnbFNoZEJSekxhZGs0Yk9EY21iekVfci1jNE9YRG4wcXkydW9LVURRV0swb3ZfZw?oc=5"
redirected_link = get_redirected_link(url)
print(f"Redirected link: {redirected_link}")
