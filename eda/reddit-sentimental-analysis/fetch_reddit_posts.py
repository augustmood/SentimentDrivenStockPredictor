import praw
import datetime
import os
import yaml
import time
import pandas as pd
from datetime import timezone  # Necessary for handling time zones

def fetch_posts(subreddit_name='WallStreetBets', limit=3000):
    """Fetch posts from a specified subreddit using PRAW and returns a DataFrame."""

    # Load Reddit app config from a YAML file
    with open('../config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Initialize the Reddit instance with credentials from the config file
    reddit = praw.Reddit(client_id=config['client_id'],
                         client_secret=config['client_secret'],
                         user_agent="my user agent")

    subreddit = reddit.subreddit(subreddit_name)
    data = []

    # Fetch the latest posts based on the limit
    for post in subreddit.new(limit=limit):
        post_datetime = datetime.datetime.fromtimestamp(post.created_utc, timezone.utc)
        readable_timestamp = post_datetime.strftime('%Y-%m-%d %H:%M:%S')
        data.append([
            post.title, post.score, post.id, post.url, post.num_comments,
            post.created_utc, post.selftext, readable_timestamp
        ])

    # Return a DataFrame with the fetched post data
    return pd.DataFrame(data, columns=['Title', 'Score', 'ID', 'URL', 'Comms_Num', 'Created', 'Body', 'Timestamp'])

def read_csv_if_exists(filename):
    """Returns a DataFrame from a CSV file if it exists, or an empty DataFrame otherwise."""
    return pd.read_csv(filename) if os.path.exists(filename) else pd.DataFrame()

def merge_and_deduplicate(original_df, new_df):
    """Merges two DataFrames, sorts by 'Datetime' and 'Body', and removes duplicate rows, keeping the last."""
    if original_df.empty:
        original_df = pd.DataFrame(columns=new_df.columns)
    elif new_df.empty:
        new_df = pd.DataFrame(columns=original_df.columns)

    combined_df = pd.concat([original_df, new_df])
    combined_df['Datetime'] = pd.to_datetime(combined_df['Timestamp'], utc=True)
    combined_df.sort_values(by=['Datetime', 'Body'], inplace=True)
    combined_df.drop_duplicates(subset=['Datetime', 'Body'], keep='last', inplace=True)
    
    return combined_df

def update_csv(subreddit_name='WallStreetBets', limit=3000):
    comments_dir = 'posts'
    os.makedirs(comments_dir, exist_ok=True)
    
    today = datetime.datetime.now(timezone.utc).date()
    yesterday = today - datetime.timedelta(days=1)

    current_csv_filename = os.path.join(comments_dir, f'{today}-wsb-posts.csv')
    previous_csv_filename = os.path.join(comments_dir, f'{yesterday}-wsb-posts.csv')

    new_posts_df = fetch_posts(subreddit_name, limit)

    current_df = new_posts_df[pd.to_datetime(new_posts_df['Timestamp'], utc=True).dt.date == today]
    previous_df_new = new_posts_df[pd.to_datetime(new_posts_df['Timestamp'], utc=True).dt.date == yesterday]

    if not current_df.empty:
        existing_df = read_csv_if_exists(current_csv_filename)
        updated_current_df = merge_and_deduplicate(existing_df, current_df)
        updated_current_df.to_csv(current_csv_filename, index=False)

    if not previous_df_new.empty:
        previous_df = read_csv_if_exists(previous_csv_filename)
        updated_previous_df = merge_and_deduplicate(previous_df, previous_df_new)
        updated_previous_df.to_csv(previous_csv_filename, index=False)

def safe_update_csv(attempts=3, delay=10):
    """
    Attempts to update CSV files with a specified number of retries and delay between attempts.

    Parameters:
    - attempts: Maximum number of attempts to try the operation.
    - delay: Delay between attempts in seconds.
    """
    for attempt in range(1, attempts + 1):
        try:
            print(f"{datetime.datetime.now(timezone.utc)} - INFO - Attempt {attempt}: Fetching posts started")
            
            # Perform the update operation
            update_csv()

            print(f"{datetime.datetime.now(timezone.utc)} - INFO - Fetching posts finished successfully")
            return  # Exit the function upon success
        except Exception as e:
            print(f"{datetime.datetime.now(timezone.utc)} - ERROR - Attempt {attempt}: failed with error: {e}")
            
            if attempt == attempts:
                print(f"{datetime.datetime.now(timezone.utc)} - INFO - Maximum attempts reached. Exiting.")
                break  # Exit the loop after the last attempt

            print(f"{datetime.datetime.now(timezone.utc)} - INFO - Retrying in {delay} seconds...")
            time.sleep(delay)

if __name__ == "__main__":
    print('-' * 100)
    
    # Change the working directory to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Encapsulate the retry logic in a function call for clarity and reusability
    safe_update_csv(attempts=3, delay=10)