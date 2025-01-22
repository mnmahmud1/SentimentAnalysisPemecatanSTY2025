pip install google-api-python-client

import googleapiclient.discovery
import csv
import os

# Konfigurasi API
API_KEY = "YOUR-GOOGLE-API"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Variabel yang dapat diubah
MAX_VIDEOS = 10  # Jumlah maksimum video yang diambil
MAX_COMMENTS = 100  # Jumlah maksimum komentar per video

def search_videos(query, max_results=MAX_VIDEOS, published_after="2025-01-05T00:00:00Z", region_code="ID"):
    youtube = googleapiclient.discovery.build(
        YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY
    )

    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=max_results,
        type="video",
        publishedAfter=published_after,
        regionCode=region_code
    ).execute()

    videos = []
    for item in search_response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        published_at = item["snippet"]["publishedAt"]
        videos.append({"video_id": video_id, "title": title, "published_at": published_at})

    return videos

def get_video_comments(video_id, max_comments=MAX_COMMENTS):
    youtube = googleapiclient.discovery.build(
        YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY
    )

    comments = []
    next_page_token = None

    try:
        while len(comments) < max_comments:
            comment_response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(100, max_comments - len(comments)),
                pageToken=next_page_token
            ).execute()

            for item in comment_response.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                username = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
                comments.append({"comment": comment, "username": username})

            next_page_token = comment_response.get("nextPageToken")
            if not next_page_token:
                break
    except googleapiclient.errors.HttpError as e:
        if e.resp.status == 403:
            print(f"Komentar dinonaktifkan untuk video ID {video_id}.")
        else:
            print(f"Terjadi kesalahan saat mengambil komentar untuk video ID {video_id}: {e}")

    return comments

if __name__ == "__main__":
    # Keyword pencarian
    query = "Copot Shin Tae-Yong, Copot STY"

    # Cari video
    videos = search_videos(query)

    print("Ditemukan video:")
    for idx, video in enumerate(videos):
        print(f"{idx + 1}. {video['title']} (ID: {video['video_id']})")

    total_comments = 0

    # Simpan komentar ke file CSV
    csv_file_path = "youtube_comments.csv"
    with open(csv_file_path, "w", encoding="utf-8", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        # Tulis header CSV
        csvwriter.writerow(["Video Title", "Video ID", "Video Link", "Published Date", "Username", "Comment"])

        # Ambil komentar dari setiap video
        for video in videos:
            print(f"\nMengambil komentar untuk video: {video['title']}")
            comments = get_video_comments(video["video_id"])
            total_comments += len(comments)

            # Tulis komentar ke CSV
            for comment_data in comments:
                csvwriter.writerow([
                    video["title"],
                    video["video_id"],
                    f"https://www.youtube.com/watch?v={video['video_id']}",
                    video["published_at"],
                    comment_data["username"],
                    comment_data["comment"]
                ])

    print(f"\nSemua komentar disimpan ke {csv_file_path}")
    print(f"Total komentar yang diambil: {total_comments}")

    # Auto-download file CSV
    if os.path.exists(csv_file_path):
        print(f"File {csv_file_path} siap untuk diunduh.")
