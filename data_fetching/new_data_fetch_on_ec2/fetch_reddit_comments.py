import praw
import datetime
import os
import yaml
import time
import pandas as pd
from datetime import timezone  # Import the timezone class

def fetch_comments(subreddit_name='WallStreetBets', limit=300000):
    """Fetch comments from a specified subreddit using PRAW and returns a DataFrame."""

    with open('../config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    reddit = praw.Reddit(client_id=config['client_id'],
                         client_secret=config['client_secret'],
                         user_agent="my user agent")

    subreddit = reddit.subreddit(subreddit_name)
    data = []

    for comment in subreddit.comments(limit=limit):
        # Keep created_utc as original Unix timestamp
        created_utc = comment.created_utc
        # Convert created_utc to a readable datetime object and place it as the first column
        comment_datetime = datetime.datetime.fromtimestamp(created_utc, timezone.utc)
        data.append([
            comment_datetime,  # Human-readable datetime as the first column
            created_utc,  # Original Unix timestamp
            str(comment.author),  # Author
            comment.body,  # Body
            comment.distinguished,  # Distinguished
            comment.edited,  # Edited
            comment.id,  # ID
            comment.is_submitter,  # Is Submitter
            comment.link_id,  # Link ID
            comment.parent_id,  # Parent ID
            comment.permalink,  # Permalink
            comment.saved,  # Saved
            comment.score,  # Score
            comment.stickied,  # Stickied
            str(comment.submission),  # Submission ID
            str(comment.subreddit),  # Subreddit Name
            comment.subreddit_id,  # Subreddit ID
        ])

    columns = ['Datetime', 'Created UTC', 'Author', 'Body', 'Distinguished', 'Edited', 'ID', 
               'Is Submitter', 'Link ID', 'Parent ID', 'Permalink', 'Saved', 'Score', 'Stickied', 
               'Submission ID', 'Subreddit', 'Subreddit ID']
    return pd.DataFrame(data, columns=columns)

def read_csv_if_exists(filename):
    """Returns a DataFrame from a CSV file if it exists, or an empty DataFrame otherwise."""
    return pd.read_csv(filename) if os.path.exists(filename) else pd.DataFrame(columns = ['Datetime', 'Created UTC', 'Author', 'Body', 'Distinguished', 'Edited', 'ID', 
               'Is Submitter', 'Link ID', 'Parent ID', 'Permalink', 'Saved', 'Score', 'Stickied', 
               'Submission ID', 'Subreddit', 'Subreddit ID'])

def merge_and_deduplicate(original_df, new_df):
    """Merges two DataFrames, sorts by 'Datetime' and 'Body', and removes duplicate rows, keeping the last."""

    # Check if one of the DataFrames is empty
    if original_df.empty and not new_df.empty:
        combined_df = new_df.copy()
    elif new_df.empty and not original_df.empty:
        combined_df = original_df.copy()
    else:
        # Neither DataFrame is empty, proceed with concatenation
        combined_df = pd.concat([original_df, new_df], ignore_index=True)

    # It's critical to ensure that 'Datetime' is treated as actual datetime objects for sorting and dropping duplicates.
    combined_df['Datetime'] = pd.to_datetime(combined_df['Datetime'], utc=True, errors='coerce')

    # Sort before dropping duplicates to ensure the last entry is kept
    combined_df.sort_values(by=['Datetime', 'Body'], inplace=True)

    # Drop duplicates with the same 'Datetime' and 'Body', keeping the last occurrence
    combined_df.drop_duplicates(subset=['Datetime', 'Body'], keep='last', inplace=True)
    
    return combined_df

def update_csv():
    comments_dir = 'test_fetch'
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

def safe_update_csv(attempts=3, delay=10):
    """
    Attempts to update CSV files with a specified number of retries and delay between attempts.

    Parameters:
    - attempts: Maximum number of attempts to try the operation.
    - delay: Delay between attempts in seconds.
    """
    for attempt in range(1, attempts + 1):
        try:
            print(f"{datetime.datetime.now(timezone.utc)} - INFO - Attempt {attempt}: Fetching comments started")
            
            # Perform the update operation
            update_csv()

            print(f"{datetime.datetime.now(timezone.utc)} - INFO - Fetching comments finished successfully")
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
