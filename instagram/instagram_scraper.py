import sys
import os
import time
from datetime import datetime, timedelta

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from instagrapi import Client
from common.db import get_db_connection
from common.config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD

def login_instagram():
    cl = Client()
    cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    return cl

def fetch_instagram_data(username):
    cl = login_instagram()
    try:
        user_id = cl.user_id_from_username(username)
        user_info = cl.user_info(user_id)
        
        profile_data = {
            "followers_count": user_info.follower_count,
            "following_count": user_info.following_count,
            "media_count": user_info.media_count,
            "profile_pic_url": str(user_info.profile_pic_url),
            "bio": user_info.biography,
            "website_url": str(user_info.external_url),
            "is_verified": user_info.is_verified,
            "account_type": user_info.account_type,
        }
        
        recent_media = cl.user_medias(user_id, 10)
        post_data = [{
            "post_id": media.pk,
            "timestamp": media.taken_at,
            "caption": media.caption_text,
            "media_type": media.media_type,
            "likes_count": media.like_count,
            "comments_count": media.comment_count
        } for media in recent_media]
        
        return profile_data, post_data
    except Exception as e:
        print(f"Error fetching data for {username}: {e}")
        return None, None

def detect_bot_activity(cursor, influencer_id, current_followers_count, total_likes, total_comments):
    follower_spike = detect_follower_spike(cursor, influencer_id, current_followers_count)
    engagement_spike = detect_sudden_engagement_spike(cursor, influencer_id)
    return follower_spike or engagement_spike

def detect_follower_spike(cursor, influencer_id, current_followers_count):
    cursor.execute("""
        SELECT followers_count FROM instagram_influencer_data_history 
        WHERE influencer_id = %s ORDER BY timestamp DESC LIMIT 5
    """, (influencer_id,))
    history = cursor.fetchall()
    if len(history) < 2:
        return False

    avg_followers = sum(row[0] for row in history[1:]) / (len(history) - 1)
    return current_followers_count > avg_followers * 1.5

def detect_sudden_engagement_spike(cursor, influencer_id):
    cursor.execute("""
        SELECT timestamp, likes_count, comments_count FROM instagram_post_data_history
        WHERE influencer_id = %s ORDER BY timestamp DESC LIMIT 10
    """, (influencer_id,))
    history = cursor.fetchall()
    if len(history) < 2:
        return False

    for i in range(1, len(history)):
        time_diff = history[i-1][0] - history[i][0]
        like_diff = history[i-1][1] - history[i][1]
        comment_diff = history[i-1][2] - history[i][2]
        if time_diff < timedelta(minutes=10) and (like_diff > 100 or comment_diff > 50):
            return True
    return False

def update_influencer_data(cursor, influencer_id, username):
    profile_data, post_data = fetch_instagram_data(username)
    if profile_data:
        if post_data:
            last_post_timestamp = post_data[0]["timestamp"]
            total_likes = sum(post["likes_count"] for post in post_data)
            total_comments = sum(post["comments_count"] for post in post_data)
            avg_likes = total_likes // len(post_data)
            avg_comments = total_comments // len(post_data)
            engagement_rate = (total_likes + total_comments) / profile_data["followers_count"] * 100 if profile_data["followers_count"] > 0 else 0
        else:
            last_post_timestamp, total_likes, total_comments, avg_likes, avg_comments, engagement_rate = None, 0, 0, 0, 0, 0

        cursor.execute("SELECT followers_count FROM instagram_influencer_data_history WHERE influencer_id = %s ORDER BY timestamp DESC LIMIT 1", (influencer_id,))
        previous_data = cursor.fetchone()
        previous_followers_count = previous_data[0] if previous_data else 0
        growth_rate = ((profile_data["followers_count"] - previous_followers_count) / previous_followers_count * 100
                       if previous_followers_count > 0 else 0)

        # Check for bot activity
        bot_flag = detect_bot_activity(cursor, influencer_id, profile_data["followers_count"], total_likes, total_comments)

        # Insert a new record into the historical data table
        cursor.execute("""
            INSERT INTO instagram_influencer_data_history (
                influencer_id, followers_count, following_count, media_count, profile_pic_url,
                bio, website_url, is_verified, account_type, last_post_timestamp,
                avg_likes, avg_comments, engagement_rate, growth_rate, total_likes, total_comments, bot_flag
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (influencer_id, profile_data["followers_count"], profile_data["following_count"], 
              profile_data["media_count"], profile_data["profile_pic_url"], profile_data["bio"], 
              profile_data["website_url"], profile_data["is_verified"], profile_data["account_type"], 
              last_post_timestamp, avg_likes, avg_comments, engagement_rate, growth_rate, 
              total_likes, total_comments, bot_flag))

        # Insert each post data into instagram_post_data and its history
        for post in post_data:
            cursor.execute("""
                INSERT INTO instagram_post_data (
                    post_id, influencer_id, timestamp, caption, media_type, likes_count, comments_count
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    likes_count = %s, comments_count = %s
            """, (post["post_id"], influencer_id, post["timestamp"], post["caption"], 
                  post["media_type"], post["likes_count"], post["comments_count"],
                  post["likes_count"], post["comments_count"]))
            
            # Insert historical data for each post
            cursor.execute("""
                INSERT INTO instagram_post_data_history (
                    post_id, influencer_id, timestamp, likes_count, comments_count
                ) VALUES (%s, %s, %s, %s, %s)
            """, (post["post_id"], influencer_id, datetime.now(), post["likes_count"], post["comments_count"]))

        print(f"Inserted historical data for Instagram user {username} with bot_flag={bot_flag}")

def monitor_and_update_data():
    db_connection = get_db_connection()
    cursor = db_connection.cursor()

    while True:
        # Hole alle Influencer mit einem Instagram-Benutzernamen aus der `influencers`-Tabelle
        cursor.execute("SELECT influencer_id, Instagram_Username FROM influencers WHERE Instagram_Username IS NOT NULL")
        influencers = cursor.fetchall()

        for influencer in influencers:
            influencer_id, username = influencer

            # Check the last update time in the history table
            cursor.execute("""
                SELECT timestamp FROM instagram_influencer_data_history 
                WHERE influencer_id = %s 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (influencer_id,))
            last_update = cursor.fetchone()

            # Update data if 24 hours have passed since last update
            if not last_update or (datetime.now() - last_update[0]) >= timedelta(hours=24):
                update_influencer_data(cursor, influencer_id, username)

        db_connection.commit()
        time.sleep(600)  # Check every hour if any influencer needs updating

    cursor.close()
    db_connection.close()

if __name__ == "__main__":
    monitor_and_update_data()
