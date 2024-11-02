import sys
import os
import time
import asyncio
from datetime import datetime, timedelta

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TikTokApi import TikTokApi
from common.db import get_db_connection
from common.config import TIKTOK_MSTOKEN

# ms_token aus den Umgebungsvariablen lesen
ms_token = os.environ.get(TIKTOK_MSTOKEN, None)

async def fetch_tiktok_profile(api, username):
    """Abrufen von Profilinformationen und Videos für einen TikTok-Benutzer."""
    user = api.user(username=username)
    profile_data = await user.info()
    print(profile_data)

    user_id = profile_data.user_id
    nickname = profile_data.nickname
    follower_count = profile_data.stats.follower_count
    video_count = profile_data.stats.video_count

    return {
        "user_id": user_id,
        "nickname": nickname,
        "follower_count": follower_count,
        "video_count": video_count,
    }

async def fetch_tiktok_videos(api, user_id, count=5):
    """Abrufen von Video-Informationen für einen bestimmten TikTok-Benutzer."""
    videos = []
    async for video in api.user(user_id=user_id).videos(count=count):
        videos.append({
            "video_id": video.id,
            "description": video.desc,
            "create_time": datetime.fromtimestamp(video.create_time),
            "view_count": video.stats.play_count,
            "like_count": video.stats.digg_count,
            "comment_count": video.stats.comment_count,
        })
    return videos

def calculate_metrics(videos, followers_count):
    """Berechnet die Metriken avg_likes, avg_comments, total_likes, total_comments, engagement_rate."""
    total_likes = sum(video['like_count'] for video in videos)
    total_comments = sum(video['comment_count'] for video in videos)
    avg_likes = total_likes // len(videos) if videos else 0
    avg_comments = total_comments // len(videos) if videos else 0
    engagement_rate = (total_likes + total_comments) / followers_count * 100 if followers_count > 0 else 0
    return avg_likes, avg_comments, total_likes, total_comments, engagement_rate

async def monitor_and_update_tiktok_data():
    db_connection = get_db_connection()
    cursor = db_connection.cursor()

    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)

        while True:
            cursor.execute("SELECT influencer_id, TikTok_Username FROM influencers WHERE TikTok_Username IS NOT NULL")
            influencers = cursor.fetchall()

            for influencer in influencers:
                influencer_id, tiktok_username = influencer

                cursor.execute("""
                    SELECT last_updated FROM tiktok_profile_history 
                    WHERE user_id = %s 
                    ORDER BY last_updated DESC 
                    LIMIT 1
                """, (tiktok_username,))
                last_update = cursor.fetchone()

                if not last_update or (datetime.now() - last_update[0]) >= timedelta(hours=24):
                    profile_data = await fetch_tiktok_profile(api, tiktok_username)
                    video_data = await fetch_tiktok_videos(api, profile_data['user_id'])
                    avg_likes, avg_comments, total_likes, total_comments, engagement_rate = calculate_metrics(
                        video_data, profile_data['follower_count']
                    )

                    cursor.execute("SELECT follower_count FROM tiktok_profile_history WHERE user_id = %s ORDER BY last_updated DESC LIMIT 1", (profile_data['user_id'],))
                    previous_data = cursor.fetchone()
                    previous_followers_count = previous_data[0] if previous_data else 0
                    growth_rate = ((profile_data["follower_count"] - previous_followers_count) / previous_followers_count * 100
                                   if previous_followers_count > 0 else 0)

                    bot_flag = False  # Hier könnte eine Bot-Erkennungslogik eingefügt werden

                    save_tiktok_profile(cursor, profile_data, avg_likes, avg_comments, engagement_rate, growth_rate, total_likes, total_comments, bot_flag)
                    save_tiktok_videos(cursor, video_data)

            db_connection.commit()
            await asyncio.sleep(3600)  # Stündliche Überprüfung

    cursor.close()
    db_connection.close()

# Startet die asynchrone Überwachungsfunktion
if __name__ == "__main__":
    asyncio.run(monitor_and_update_tiktok_data())
