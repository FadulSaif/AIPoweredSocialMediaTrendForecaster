import tweepy 
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(
level = logging.INFO,
format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
datefmt = "%Y-%m-%d %H:%M:%S"
)

# Load the environment variables
load_dotenv()

# Now we go for twitter api authentication 
USE_FAKE_DATA = True #for testing purpose, i use true for now


if not USE_FAKE_DATA:
    try:
        auth = tweepy.OAuth1UserHandler(
            os.getenv("TWITTER_API_KEY"),
            os.getenv("TWITTER_API_SECRET"),
            os.getenv("TWITTER_ACCESS_TOKEN"),
            os.getenv("TWITTER_ACCESS_SECRET")
        )
        api = tweepy.API(auth, wait_on_rate_limit=True)
        logging.info("Twitter API authentication successful.")
    except Exception as e:
        logging.error(f"Twitter API authentication failed: {e}")
        raise SystemExit(1)


#---------------------------- 
#---Fetch Trending topics ---
#---------------------------- 
def get_trending():
    if USE_FAKE_DATA:
        logging.info("Using FAKE trending data for testing.")
        trends = [{
            "trends": [
                {"name": "#AI", "tweet_volume": 120000},
                {"name": "#OpenAI", "tweet_volume": 95000},
                {"name": "#Python", "tweet_volume": 78000},
                {"name": "#DataScience", "tweet_volume": 50000},
                {"name": "#MachineLearning", "tweet_volume": 45000},
            ]
        }]
    else:
        try:
            trends = api.get_place_trends(1)  # WOEID 1 is for worldwide
        except Exception as e:
            logging.exception("Failed to fetch trending topics")
            return []
    
    if not trends or "trends" not in trends[0]:
        logging.warning("No trend data received.")
        return []

    #Extract needed fields
    return [
        {"name": t.get("name"), "tweet_volume": t.get("tweet_volume") or 0}
        for t in trends[0]["trends"]
    ]


def save_trends(data):
    if not data:
        logging.warning("No data to save.")
        return

    #dataframe creation using pandas
    df = pd.DataFrame(data)


    # prepare the output directory
    out_dir = Path(__file__).resolve().parents[1] /"Data"/ "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    #File path with timestamp 
    file_path = out_dir / f"trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    try:
        df.to_csv(file_path, index=False)
        logging.info(f"Trending topics saved to {file_path}")
    except Exception as e:
        logging.exception("Failed to save trends in csv")

#--------------------------------------
# --- entry point---
#--------------------------------------
if __name__ == "__main__":
    data = get_trending()
    save_trends(data)