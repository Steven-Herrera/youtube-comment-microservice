"""A microservice for scraping YouTube comments using the YouTube API and the googleapiclient library.

Functions:
    load_comments: Extracts comments from a YouTube API response
    get_comment_threads: Retrieves comment threads from a YouTube video
    app: Collects YouTube comments and returns them as a DataFrame
"""

import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd


def load_comments(response, youtube):
    """Extracts comments and replies to a comment from a YouTube API response and returns them as a dictionary.

    Args:
        response (dict): A json response from the YouTube API
        youtube (googleapiclient.discovery.Resource): A YouTube API resource

    Returns:
        payload (dict): A dictionary containing the author, text, like count, id, and publish date of each comment and reply
    """
    payload = {"author": [], "text": [], "likeCount": [], "id": [], "publishDate": []}
    for item in response["items"]:
        parent_id = item["id"]
        comment = item["snippet"]["topLevelComment"]
        author = comment["snippet"]["authorDisplayName"]
        text = comment["snippet"]["textDisplay"]
        like_count = comment["snippet"]["likeCount"]
        publish_date = comment["snippet"]["publishedAt"]

        payload["author"].append(author)
        payload["text"].append(text)
        payload["likeCount"].append(like_count)
        payload["id"].append(parent_id)
        payload["publishDate"].append(publish_date)

        if "replies" in item.keys():
            reply_request = youtube.comments().list(part="snippet", parentId=parent_id)
            reply_response = reply_request.execute()
            for reply_item in reply_response["items"]:
                reply_comment = reply_item["snippet"]
                reply_id = reply_item["id"]
                reply_author = reply_comment["authorDisplayName"]
                reply_text = reply_comment["textDisplay"]
                reply_like_count = reply_comment["likeCount"]
                reply_date = reply_comment["publishedAt"]

                payload["author"].append(reply_author)
                payload["text"].append(reply_text)
                payload["likeCount"].append(reply_like_count)
                payload["id"].append(reply_id)
                payload["publishDate"].append(reply_date)

    return payload


def get_comment_threads(youtube, video_id, next_page_token):
    """Invokes the YouTube API to retrieve comment threads from a video.

    Args:
        youtube (googleapiclient.discovery.Resource): A YouTube API resource
        video_id (str): The ID of the YouTube video
        next_page_token (str): A token for retrieving the next page of comments

    Returns:
        results (dict): A json response from the YouTube API containing comment threads
    """
    results = (
        youtube.commentThreads()
        .list(
            part="snippet,replies",
            maxResults=10_000,
            videoId=video_id,
            textFormat="plainText",
            pageToken=next_page_token,
        )
        .execute()
    )
    return results


def app(developer_key, youtube_video_id):
    """Downloads YouTube comments as a CSV file using the YouTube API and the googleapiclient library.

    Args:
      developer_key (str): A YouTube API developer key
      youtube_video_id (str): The ID of the YouTube video

    Returns:
      df (pandas.core.frame.DataFrame): A DataFrame containing the author, text, like count, id, and publish date of each comment and reply
    """
    api_service_name = "youtube"
    api_version = "v3"
    youtube_api = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=developer_key
    )
    youtube_response = get_comment_threads(youtube_api, youtube_video_id, "")
    youtube_payload = load_comments(youtube_response, youtube_api)

    if "nextPageToken" in youtube_response.keys():
        youtube_next_page_token = youtube_response["nextPageToken"]
        try:
            while youtube_next_page_token:
                youtube_response = get_comment_threads(
                    youtube_api, youtube_video_id, youtube_next_page_token
                )
                youtube_next_page_token = youtube_response["nextPageToken"]
                page_payload = load_comments(youtube_response, youtube_api)

                youtube_payload["author"].extend(page_payload["author"])
                youtube_payload["text"].extend(page_payload["text"])
                youtube_payload["likeCount"].extend(page_payload["likeCount"])
                youtube_payload["id"].extend(page_payload["id"])
                youtube_payload["publishDate"].extend(page_payload["publishDate"])

        except KeyError:
            df = pd.DataFrame.from_dict(youtube_payload)
    else:
        df = pd.DataFrame.from_dict(youtube_payload)

    return df

if __name__ == "__main__":
    import os
    import io
    csv_buffer = io.StringIO()
    DEVELOPER_KEY = os.environ["DEVELOPER_KEY"]
    YOUTUBE_VIDEO_ID = os.environ["VIDEO_ID"] if "VIDEO_ID" in os.environ else "wJhYWbEi6NQ"
    youtube_df = app(DEVELOPER_KEY, YOUTUBE_VIDEO_ID)
    youtube_df.to_csv(csv_buffer, index=False)
    print(csv_buffer.getvalue())