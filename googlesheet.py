# pip install gspread oauth2client
import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials


def add_row_to_sheet(new_row_data, spreadsheet_name, sheet_name):
    # Set up credentials
    # credentials_file = "testing-b9de3-50dac3c9a9f5.json"
    # spreadsheet_name = "videos"
    # sheet_name = "newsvideos"

    # Get the secret from environment variable
    credentials_file = os.getenv("Google_Sheets")

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)

    try:
        # Open the Google Spreadsheet by its title
        spreadsheet = client.open(spreadsheet_name)
        sheet = spreadsheet.worksheet(sheet_name)
        # Append the new row
        sheet.append_row(new_row_data)
        print("New row added successfully to sheet '{}'!".format(sheet_name))
    except Exception as e:
        print("An error occurred:", e)


def check_text_in_column_a(sheet_name: str, text: str, column_values) -> bool:
    """
    Checks if the specified text exists in column A of the Google Sheet.

    Parameters:
    sheet_name (str): The name of the Google Sheet.
    text (str): The text to search for in column A.

    Returns:
    bool: True if the text is found in column A, False otherwise.
    """
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Load credentials
    creds = ServiceAccountCredentials.from_json_keyfile_name('testing-b9de3-50dac3c9a9f5.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet by name
    sheet = client.open(sheet_name).sheet1

    # Get all values in column A
    column_a_values = sheet.col_values(column_values)

    # Check if the text is in column A
    return text in column_a_values


def get_column_text(sheet_name: str, column_id: int) -> list:
    """
    Retrieves all text from the specified column in the Google Sheet.

    Parameters:
    sheet_name (str): The name of the Google Sheet.
    column_id (int): The ID of the column to retrieve text from (e.g., 3 for column C).

    Returns:
    list: A list of tuples containing the row index and the text from the specified column.
    """
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Load credentials
    creds = ServiceAccountCredentials.from_json_keyfile_name('testing-b9de3-50dac3c9a9f5.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet by name
    sheet = client.open(sheet_name).sheet1

    # Get all values in the specified column
    column_values = sheet.col_values(column_id)

    # Create a list of tuples with the row index and the text
    result = [(idx + 1, value) for idx, value in enumerate(column_values)]

    return result



def update_cell_value(sheet_name: str, row_id: int, column_id: int, new_value: str) -> str:
    """
    Updates the value of a specific cell in a Google Sheet and returns the updated value.

    Parameters:
    sheet_name (str): The name of the Google Sheet.
    row_id (int): The row number of the cell to update.
    column_id (int): The column number of the cell to update.
    new_value (str): The new value to set in the cell.

    Returns:
    str: The updated value in the cell.
    """
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Load credentials
    creds = ServiceAccountCredentials.from_json_keyfile_name('testing-b9de3-50dac3c9a9f5.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet by name
    sheet = client.open(sheet_name).sheet1

    # Update the specified cell
    sheet.update_cell(row_id, column_id, new_value)

    # Return the updated value
    updated_value = sheet.cell(row_id, column_id).value
    return updated_value



# Example usage

date = {'tweet_id': '1818269133298950253', 'creation_date': 'Tue Jul 30 12:55:17 +0000 2024',
        'text': '😂 https://t.co/nlvLlqBeoj', 'name': 'Elon Musk',
        'language': 'qme', 'favorite_count': 49299, 'retweet_count': 7727, 'reply_count': 3411, 'quote_count': 613,
        'retweet': False,
        'views': 2323654, 'timestamp': 1722344117}
tweet_id = date["tweet_id"]
creation_date = date["creation_date"]
text = date["text"]
name = date["name"]
language = date["language"]
favorite_count = date["favorite_count"]
retweet_count = date["retweet_count"]
reply_count = date["reply_count"]
quote_count = date["quote_count"]
retweet = date["retweet"]
views = date["views"]
timestamp = date["timestamp"]

sheet_name = "tweets"
new_row_data = [tweet_id, creation_date, text, name, language, favorite_count, retweet_count, reply_count, quote_count,
                retweet, views, timestamp]
# add_row_to_sheet(new_row_data)

# desc = "Steve Rosenberg: Shock Kursk incursion won't turn Russians against the war " + '\n\n' + "article_url" + '\n\n' + "Vice President Kamala Harris is poised to announce her running mate on Tuesday morning. The announcement will be followed by a campaign video and a rally in Philadelphia.\n\nHarris' selection process has involved extensive preparation, including printing campaign signs with various potential running mates. She is reportedly seeking a governing partner with experience and qualifications to serve immediately, echoing the qualities President Biden valued when choosing her four years ago.\n\nThe announcement marks a timely development in the wake of President Biden's recent reeelection announcement, solidifying Harris's role as the Democratic Party's presumptive presidential candidate. The announcement follows in-person and virtual interviews with top contenders, including Pennsylvania Gov. Josh Shapiro, Minnesota Gov. Tim Walz, and Arizona Sen. Mark Kelly."
# new_row_data2 = ["videourl", "Steve Rosenberg: Shock Kursk incursion won't turn Russians against the war ", desc]
# add_row_to_sheet(new_row_data2, "youtube_videos", "youtube")