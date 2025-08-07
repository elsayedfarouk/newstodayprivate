from github import Github
import os
from pathlib import Path
from datetime import datetime
import time

# Get the secret from environment variable
github_token = os.getenv("token_github")

def upload_folder_to_github(token, repo_name, folder_path, owner, branch='main'):
    g = Github(token)
    user = g.get_user()
    repo = user.get_repo(repo_name)

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = Path(root) / file
            with open(file_path, 'rb') as file_content:
                content = file_content.read()

            # Prepend folder_path to place files within a directory named folder_path in the repo
            repo_file_path = os.path.join(folder_path, os.path.relpath(file_path, folder_path))
            # Convert Windows backslashes to forward slashes
            repo_file_path = repo_file_path.replace(os.sep, '/')

            retries = 3
            delay = 5
            for attempt in range(retries):
                try:
                    try:
                        contents = repo.get_contents(repo_file_path, ref=branch)
                        repo.update_file(contents.path, f"Update {repo_file_path}", content, contents.sha,
                                         branch=branch)
                        print(f"File '{repo_file_path}' updated successfully.")
                    except:
                        repo.create_file(repo_file_path, f"Add {repo_file_path}", content, branch=branch)
                        print(f"File '{repo_file_path}' uploaded successfully.")
                    break  # Exit loop if successful
                except Exception as e:
                    print(f"Error uploading '{repo_file_path}': {e}")
                    if attempt < retries - 1:
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        print(f"Failed to upload '{repo_file_path}' after {retries} attempts.")


def upload_specific_files_to_github(token, repo_name, file_paths, target_folder, owner, branch='main'):
    """
    Upload specific files to GitHub repository

    Args:
        token (str): GitHub access token
        repo_name (str): Name of the repository
        file_paths (list): List of file paths to upload
        target_folder (str): Target folder in GitHub repository
        owner (str): GitHub username
        branch (str, optional): Repository branch. Defaults to 'main'.
    """
    g = Github(token)
    user = g.get_user()
    repo = user.get_repo(repo_name)

    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"File '{file_path}' does not exist. Skipping.")
            continue

        with open(file_path, 'rb') as file_content:
            content = file_content.read()

        # Get just the filename from the path
        file_name = os.path.basename(file_path)

        # Combine with target folder to create the destination path
        repo_file_path = f"{target_folder}/{file_name}"

        retries = 3
        delay = 5
        for attempt in range(retries):
            try:
                try:
                    contents = repo.get_contents(repo_file_path, ref=branch)
                    repo.update_file(contents.path, f"Update {file_name}", content, contents.sha, branch=branch)
                    print(f"File '{file_name}' updated successfully in '{target_folder}'.")
                except:
                    repo.create_file(repo_file_path, f"Add {file_name}", content, branch=branch)
                    print(f"File '{file_name}' uploaded successfully to '{target_folder}'.")
                break  # Exit loop if successful
            except Exception as e:
                print(f"Error uploading '{file_name}': {e}")
                if attempt < retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    print(f"Failed to upload '{file_name}' after {retries} attempts.")


def run():
    # Example usage
    today_date = datetime.now().strftime("%Y%m%d")
    repo_name = 'public'
    folder_path = os.path.join('img', today_date)
    owner = 'elsayedfarouk'

    upload_folder_to_github(github_token, repo_name, folder_path, owner)


def run2():
    # Example usage
    today_date = datetime.now().strftime("%Y%m%d")
    repo_name = 'public'
    folder_path = os.path.join('news_videos', today_date)
    owner = 'elsayedfarouk'

    upload_folder_to_github(github_token, repo_name, folder_path, owner)


def run3(foldername):
    # Example usage
    repo_name = 'public'
    owner = 'elsayedfarouk'

    upload_folder_to_github(github_token, repo_name, foldername, owner)


def run4(file_paths, target_folder):
    # Upload specific files to GitHub
    repo_name = 'public'
    owner = 'elsayedfarouk'

    upload_specific_files_to_github(github_token, repo_name, file_paths, target_folder, owner)


# file_paths = ['thumbnail.png', 'news.json']
# target_folder = ''
# run4(file_paths, target_folder)
