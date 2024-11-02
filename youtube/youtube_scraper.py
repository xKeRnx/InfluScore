import sys
import os
import time
from datetime import datetime, timedelta

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import shelve
from googleapiclient.discovery import build
from common.db import get_db_connection
from common.config import YOUTUBE_API_KEY

CACHE_FILE = 'youtube_cache'
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def fetch_youtube_data(channel_id, cache_duration=timedelta(days=3)):
    """Fetch and cache YouTube channel and video data."""
    with shelve.open(CACHE_FILE) as cache:
        if channel_id in cache:
            cached_data, last_update = cache[channel_id]
            if datetime.now() - last_update < cache_duration:
                return cached_data  # Return cached data if within cache duration

        channel_request = youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        )
        channel_response = channel_request.execute()
        item = channel_response['items'][0]
        
        profile_data = {
            "channel_id": item['id'],
            "channel_name": item['snippet']['title'],
            "subscribers_count": int(item['statistics'].get('subscriberCount', 0)),
            "view_count": int(item['statistics'].get('viewCount', 0)),
            "video_count": int(item['statistics'].get('videoCount', 0)),
        }

        video_ids = fetch_videos(channel_id)
        post_data = fetch_video_details(video_ids, channel_id)  # channel_id übergeben
        cache[channel_id] = ((profile_data, post_data), datetime.now())  # Update cache
        return profile_data, post_data


def fetch_videos(channel_id):
    video_ids = []
    request = youtube.search().list(
        part='id',
        channelId=channel_id,
        maxResults=10,
        order='date'
    )
    response = request.execute()
    for item in response['items']:
        if item['id']['kind'] == 'youtube#video':
            video_ids.append(item['id']['videoId'])
    return video_ids

def fetch_video_details(video_ids, channel_id):
    """Fetch detailed information for each video ID."""
    video_details = []
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids[i:i + 50])
        )
        response = request.execute()
        for item in response['items']:
            video_details.append({
                "video_id": item['id'],
                "channel_id": channel_id,  # Hinzufügen von channel_id zu jedem Video-Eintrag
                "title": item['snippet']['title'],
                "view_count": int(item['statistics'].get('viewCount', 0)),
                "like_count": int(item['statistics'].get('likeCount', 0)),
                "comment_count": int(item['statistics'].get('commentCount', 0)),
            })
    return video_details


def calculate_metrics(post_data, subscribers_count):
    """Calculate metrics like avg_likes, avg_comments, total_likes, total_comments, engagement_rate."""
    total_likes = sum(post['like_count'] for post in post_data)
    total_comments = sum(post['comment_count'] for post in post_data)
    avg_likes = total_likes // len(post_data) if post_data else 0
    avg_comments = total_comments // len(post_data) if post_data else 0
    engagement_rate = (total_likes + total_comments) / subscribers_count * 100 if subscribers_count > 0 else 0
    return avg_likes, avg_comments, total_likes, total_comments, engagement_rate

def save_channel_data(cursor, channel_data, avg_likes, avg_comments, engagement_rate, growth_rate, total_likes, total_comments, bot_flag):
    cursor.execute("""
        INSERT INTO youtube_channels (channel_id, channel_name, subscriber_count, view_count, video_count)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            subscriber_count = VALUES(subscriber_count),
            view_count = VALUES(view_count),
            video_count = VALUES(video_count),
            last_updated = CURRENT_TIMESTAMP
    """, (
        channel_data['channel_id'],
        channel_data['channel_name'],
        channel_data['subscribers_count'],
        channel_data['view_count'],
        channel_data['video_count']
    ))

    cursor.execute("""
        INSERT INTO youtube_channel_history (channel_id, subscriber_count, view_count, video_count, avg_likes, avg_comments, 
                                             engagement_rate, growth_rate, total_likes, total_comments, bot_flag)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        channel_data['channel_id'],
        channel_data['subscribers_count'],
        channel_data['view_count'],
        channel_data['video_count'],
        avg_likes,
        avg_comments,
        engagement_rate,
        growth_rate,
        total_likes,
        total_comments,
        bot_flag
    ))

def save_video_data(cursor, video_data):
    cursor.execute("""
        INSERT INTO youtube_videos (video_id, channel_id, title, view_count, like_count, comment_count)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            view_count = VALUES(view_count),
            like_count = VALUES(like_count),
            comment_count = VALUES(comment_count),
            last_updated = CURRENT_TIMESTAMP
    """, (
        video_data['video_id'],
        video_data['channel_id'],
        video_data['title'],
        video_data['view_count'],
        video_data['like_count'],
        video_data['comment_count']
    ))

    cursor.execute("""
        INSERT INTO youtube_video_history (video_id, view_count, like_count, comment_count)
        VALUES (%s, %s, %s, %s)
    """, (
        video_data['video_id'],
        video_data['view_count'],
        video_data['like_count'],
        video_data['comment_count']
    ))

def detect_bot_activity(cursor, channel_id, current_subscribers_count, total_views, total_likes, total_comments):
    """Detect bot activity based on unusual spikes in subscribers, views, likes, and comments."""
    follower_spike = detect_follower_spike(cursor, channel_id, current_subscribers_count)
    engagement_spike = detect_engagement_spike(cursor, channel_id, total_likes, total_comments, total_views)
    return follower_spike or engagement_spike

def detect_follower_spike(cursor, channel_id, current_subscribers_count):
    """Erkennt einen plötzlichen Anstieg der Abonnentenzahl im Vergleich zu historischen Daten."""
    # Holen Sie die letzten 5 Abonnentenzahlen aus der Historientabelle
    cursor.execute("""
        SELECT subscriber_count FROM youtube_channel_history 
        WHERE channel_id = %s ORDER BY last_updated DESC LIMIT 5
    """, (channel_id,))
    history = cursor.fetchall()
    
    # Wenn es weniger als 2 Datenpunkte gibt, ist keine Erkennung möglich
    if len(history) < 2:
        return False  # Nicht genügend Daten für die Spike-Erkennung

    # Berechnen Sie den durchschnittlichen Abonnentenzuwachs der letzten Datenpunkte
    avg_subscribers = sum(row[0] for row in history[1:]) / (len(history) - 1)
    
    # Überprüfen Sie, ob die aktuelle Abonnentenzahl 50% über dem Durchschnitt liegt
    return current_subscribers_count > avg_subscribers * 1.5  # Spike-Erkennung bei 50% Anstieg

def detect_engagement_spike(cursor, channel_id, total_likes, total_comments, total_views):
    """Erkennt plötzliche Engagement-Spikes bei Likes, Kommentaren und Views im Vergleich zu historischen Daten."""
    cursor.execute("""
        SELECT total_likes, total_comments, view_count FROM youtube_channel_history
        WHERE channel_id = %s ORDER BY last_updated DESC LIMIT 10
    """, (channel_id,))
    history = cursor.fetchall()
    
    # Wenn es weniger als 2 Datenpunkte gibt, ist keine Erkennung möglich
    if len(history) < 2:
        return False  # Nicht genügend Daten für die Spike-Erkennung

    # Überprüfen der letzten Werte auf Spikes im Vergleich zu früheren Daten
    for i in range(1, len(history)):
        like_diff = history[i-1][0] - history[i][0]
        comment_diff = history[i-1][1] - history[i][1]
        view_diff = history[i-1][2] - history[i][2]
        
        # Definieren Sie die Spike-Schwellenwerte für einen Anstieg in kurzer Zeit
        if like_diff > 100 or comment_diff > 50 or view_diff > 1000:
            return True  # Spike erkannt
    return False


def monitor_and_update_data():
    db_connection = get_db_connection()
    cursor = db_connection.cursor()

    while True:
        # Hole alle YouTube-Kanäle aus der `influencers`-Tabelle
        cursor.execute("SELECT influencer_id, YouTube_ChannelID FROM influencers WHERE YouTube_ChannelID IS NOT NULL")
        influencers = cursor.fetchall()

        for influencer in influencers:
            influencer_id, channel_id = influencer

            # Überprüfen, wann zuletzt aktualisiert wurde
            cursor.execute("""
                SELECT last_updated FROM youtube_channel_history 
                WHERE channel_id = %s 
                ORDER BY last_updated DESC 
                LIMIT 1
            """, (channel_id,))
            last_update = cursor.fetchone()

            if not last_update or (datetime.now() - last_update[0]) >= timedelta(hours=24):
                channel_data, post_data = fetch_youtube_data(channel_id)
                if channel_data:
                    avg_likes, avg_comments, total_likes, total_comments, engagement_rate = calculate_metrics(
                        post_data, channel_data['subscribers_count']
                    )
                    
                    cursor.execute("SELECT subscriber_count FROM youtube_channel_history WHERE channel_id = %s ORDER BY last_updated DESC LIMIT 1", (channel_id,))
                    previous_data = cursor.fetchone()
                    previous_subscribers_count = previous_data[0] if previous_data else 0
                    growth_rate = ((channel_data["subscribers_count"] - previous_subscribers_count) / previous_subscribers_count * 100
                                   if previous_subscribers_count > 0 else 0)

                    bot_flag = detect_bot_activity(cursor, channel_id, channel_data['subscribers_count'], 
                                                   total_likes, total_comments, engagement_rate)
                    save_channel_data(cursor, channel_data, avg_likes, avg_comments, engagement_rate, growth_rate, total_likes, total_comments, bot_flag)
                    
                    for video in post_data:
                        save_video_data(cursor, video)

        db_connection.commit()
        time.sleep(3600)  # Prüfen jede Stunde, ob ein Kanal aktualisiert werden muss

    cursor.close()
    db_connection.close()

if __name__ == "__main__":
    monitor_and_update_data()
