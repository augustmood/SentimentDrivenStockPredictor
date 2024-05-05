import praw
import datetime
import os
import yaml
import pandas as pd
from datetime import timezone  # Import the timezone class

def fetch_comments(subreddit_name='WallStreetBets', limit=3000):
    """Fetch comments from a specified subreddit using PRAW and returns a DataFrame."""

    with open('../config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    reddit = praw.Reddit(client_id=config['client_id'],
                         client_secret=config['client_secret'],
                         user_agent="my user agent")

    subreddit = reddit.subreddit(subreddit_name)
    data = []

    for comment in subreddit.comments(limit=limit):
        # Use datetime.fromtimestamp with timezone.utc for UTC datetime objects
        comment_datetime = datetime.datetime.fromtimestamp(comment.created_utc, timezone.utc)
        data.append([comment_datetime, comment.body, comment.score])

    return pd.DataFrame(data, columns=['Datetime', 'Body', 'Score'])

def read_csv_if_exists(filename):
    """Returns a DataFrame from a CSV file if it exists, or an empty DataFrame otherwise."""
    return pd.read_csv(filename) if os.path.exists(filename) else pd.DataFrame(columns=['Datetime', 'Body', 'Score'])

def merge_and_deduplicate(original_df, new_df):
    """Merges two DataFrames, sorts by 'Datetime' and 'Body', and removes duplicate rows, keeping the last."""

    # Ensure both DataFrames have the same structure, especially if one might be empty
    if original_df.empty:
        original_df = pd.DataFrame(columns=new_df.columns)
    elif new_df.empty:
        new_df = pd.DataFrame(columns=original_df.columns)
    combined_df = pd.concat([original_df, new_df])

    # It's critical to ensure that 'Datetime' is treated as actual datetime objects for sorting and dropping duplicates.
    combined_df['Datetime'] = pd.to_datetime(combined_df['Datetime'], utc=True)

    # Sort before dropping duplicates to ensure the last entry is kept
    combined_df.sort_values(by=['Datetime', 'Body'], inplace=True)

    # Drop duplicates with the same 'Datetime' and 'Body', keeping the last occurrence
    combined_df.drop_duplicates(subset=['Datetime', 'Body'], keep='last', inplace=True)
    
    return combined_df

def update_csv():
    comments_dir = 'comments'
    os.makedirs(comments_dir, exist_ok=True)
    
    today = datetime.datetime.now(timezone.utc).date()
    yesterday = today - datetime.timedelta(days=1)

    current_csv_filename = os.path.join(comments_dir, f'{today}-wsb-comments.csv')
    previous_csv_filename = os.path.join(comments_dir, f'{yesterday}-wsb-comments.csv')

    new_comments_df = fetch_comments()

    # Directly extract and use the 'date' part for filtering without adding it as a separate column
    current_df = new_comments_df[pd.to_datetime(new_comments_df['Datetime'], utc=True).dt.date == today]
    previous_df_new = new_comments_df[pd.to_datetime(new_comments_df['Datetime'], utc=True).dt.date == yesterday]

    if not current_df.empty:
        existing_df = read_csv_if_exists(current_csv_filename)
        updated_current_df = merge_and_deduplicate(existing_df, current_df)
        # Ensure the 'date' column is not included in the saved CSV
        updated_current_df.to_csv(current_csv_filename, index=False)

    if not previous_df_new.empty:
        previous_df = read_csv_if_exists(previous_csv_filename)
        updated_previous_df = merge_and_deduplicate(previous_df, previous_df_new)
        # Ensure the 'date' column is not included in the saved CSV
        updated_previous_df.to_csv(previous_csv_filename, index=False)

if __name__ == "__main__":
    # Print a line for visual separation and indicate the action at the beginning
    print('-' * 100)
    print(f"{datetime.datetime.now(timezone.utc)} - INFO - Fetching comments started")

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Change the current working directory to the script directory
    os.chdir(script_dir)
    update_csv()

    # Indicate the action has finished, use UTC time, and print another line for separation at the end
    print(f"{datetime.datetime.now(timezone.utc)} - INFO - Fetching comments finished")
