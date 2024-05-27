"""A microservice for scraping YouTube comments using the YouTube API from the googleapiclient library.

Functions:
    load_comments: Extracts comments from a YouTube API response
    get_comment_threads: Retrieves comment threads from a YouTube video
    get_num_comments: Retrieves the number of comments on a YouTube video
    get_youtube_video_id: Extracts the YouTube video ID from a URL
    app: Collects YouTube comments and returns them as a DataFrame
    main: Runs the Streamlit app

TODO:
    - Fix the get_youtube_video_id to adhere to GitHub Code Scanning recommendations
    - Test the get_youtube_video_id function for bad URLs 
"""

import googleapiclient.discovery
from googleapiclient.errors import HttpError
import pandas as pd
import streamlit as st
from urllib.parse import urlparse
import streamlit.components.v1 as components

def load_comments(
    response, youtube, comments_scraped, num_comments, streamlit_progress_bar
):
    """Extracts comments and replies to a comment from a YouTube API response and returns them as a dictionary.

    Args:
        response (dict): A json response from the YouTube API
        youtube (googleapiclient.discovery.Resource): A YouTube API resource
        comments_scraped (int): The number of comments scraped
        num_comments (int): The total number of comments on the YouTube video
        streamlit_progress_bar (streamlit.delta_generator.DeltaGenerator): A Streamlit progress bar

    Returns:
        payload (dict): A dictionary containing the author, text, like count, id, and publish date of each comment and reply
        comments_scraped (int): The number of comments scraped
    """
    payload = {
        "author": [],
        "text": [],
        "likeCount": [],
        "id": [],
        "publishDate": [],
        "authorChannelUrl": [],
        "channelId": [],
        "canRate": [],
        "viewerRating": [],
        "updatedAt": [],
    }

    for item in response["items"]:
        parent_id = item["id"]
        comment = item["snippet"]["topLevelComment"]
        author = comment["snippet"]["authorDisplayName"]
        text = comment["snippet"]["textDisplay"]
        like_count = comment["snippet"]["likeCount"]
        publish_date = comment["snippet"]["publishedAt"]

        author_channel_url = comment["snippet"]["authorChannelUrl"]
        channel_id = comment["snippet"]["channelId"]
        can_rate = comment["snippet"]["canRate"]
        viewer_rating = comment["snippet"]["viewerRating"]
        updated_at = comment["snippet"]["updatedAt"]

        payload["author"].append(author)
        payload["text"].append(text)
        payload["likeCount"].append(like_count)
        payload["id"].append(parent_id)
        payload["publishDate"].append(publish_date)
        payload["authorChannelUrl"].append(author_channel_url)
        payload["channelId"].append(channel_id)
        payload["canRate"].append(can_rate)
        payload["viewerRating"].append(viewer_rating)
        payload["updatedAt"].append(updated_at)

        comments_scraped += 1
        percent_complete = round(comments_scraped / num_comments, 2)
        streamlit_progress_bar.progress(
            percent_complete, text="Scraping in progress. Please wait."
        )

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

                reply_author_channel_url = comment["snippet"]["authorChannelUrl"]
                reply_channel_id = comment["snippet"]["channelId"]
                reply_can_rate = comment["snippet"]["canRate"]
                reply_viewer_rating = comment["snippet"]["viewerRating"]
                reply_updated_at = comment["snippet"]["updatedAt"]

                payload["author"].append(reply_author)
                payload["text"].append(reply_text)
                payload["likeCount"].append(reply_like_count)
                payload["id"].append(reply_id)
                payload["publishDate"].append(reply_date)

                payload["authorChannelUrl"].append(reply_author_channel_url)
                payload["channelId"].append(reply_channel_id)
                payload["canRate"].append(reply_can_rate)
                payload["viewerRating"].append(reply_viewer_rating)
                payload["updatedAt"].append(reply_updated_at)

                comments_scraped += 1
                percent_complete = round(comments_scraped / num_comments, 2)
                streamlit_progress_bar.progress(
                    percent_complete, text="Scraping in progress. Please wait."
                )

    return (payload, comments_scraped)


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


def get_num_comments(youtube_api, youtube_video_id):
    """Retrieves the number of comments on a YouTube video.

    Args:
        youtube_api (googleapiclient.discovery.Resource): A YouTube API resource
        youtube_video_id (str): The ID of the YouTube video

    Returns:
        num_comments (int | str): The number of comments on the YouTube video or in the event of an error, a string
    """
    try:
        video_response = (
            youtube_api.videos().list(part="statistics", id=youtube_video_id).execute()
        )
        # This error likely occurs because the user passed an invalid API key
    except HttpError as e:
        return e.reason

    if not video_response["items"]:
        # This error likely occurs because the user passed an invalid video ID
        return "No video found. Are you sure the URL is correct?"

    num_comments = int(video_response["items"][0]["statistics"]["commentCount"])
    return num_comments


def app(developer_key, youtube_video_id):
    """Downloads YouTube comments as a CSV file using the YouTube API and the googleapiclient library.

    Args:
      developer_key (str): A YouTube API developer key
      youtube_video_id (str): The ID of the YouTube video
      checkmark_boxes (Dict[str, bool]): A dictionary containing the columns to include in the CSV file

    Returns:
      df (pandas.core.frame.DataFrame): A DataFrame containing comments
      comments_scraped (int): The number of comments scraped
      num_comments (int | str): The total number of comments on the YouTube video or an error message
    """
    api_service_name = "youtube"
    api_version = "v3"

    youtube_api = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=developer_key
    )
    num_comments = get_num_comments(youtube_api, youtube_video_id)
    if type(num_comments) == str:
        # If num_comments is a string, then an error occurred
        return num_comments
    youtube_response = get_comment_threads(youtube_api, youtube_video_id, "")

    progress_text = "Scraping in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)

    youtube_payload, comments_scraped = load_comments(
        youtube_response, youtube_api, 0, num_comments, my_bar
    )

    if "nextPageToken" in youtube_response.keys():
        youtube_next_page_token = youtube_response["nextPageToken"]
        try:
            while youtube_next_page_token:
                youtube_response = get_comment_threads(
                    youtube_api, youtube_video_id, youtube_next_page_token
                )
                youtube_next_page_token = youtube_response["nextPageToken"]
                page_payload, comments_scraped = load_comments(
                    youtube_response,
                    youtube_api,
                    comments_scraped,
                    num_comments,
                    my_bar,
                )

                youtube_payload["author"].extend(page_payload["author"])
                youtube_payload["text"].extend(page_payload["text"])
                youtube_payload["likeCount"].extend(page_payload["likeCount"])
                youtube_payload["id"].extend(page_payload["id"])
                youtube_payload["publishDate"].extend(page_payload["publishDate"])
                youtube_payload["authorChannelUrl"].extend(
                    page_payload["authorChannelUrl"]
                )
                youtube_payload["channelId"].extend(page_payload["channelId"])
                youtube_payload["canRate"].extend(page_payload["canRate"])
                youtube_payload["viewerRating"].extend(page_payload["viewerRating"])
                youtube_payload["updatedAt"].extend(page_payload["updatedAt"])

        except KeyError:
            df = pd.DataFrame.from_dict(youtube_payload)
            my_bar.progress(100, text="Scraping complete!")
    else:
        df = pd.DataFrame.from_dict(youtube_payload)
        my_bar.progress(100, text="Scraping complete!")

    return (df, comments_scraped, num_comments)


def get_youtube_video_id(user_video_url_input):
    """Extracts the YouTube video ID from a URL.

    Args:
        user_video_url_input (str): The URL of a YouTube video

    Returns:
        video_id (str): The ID of the YouTube video
    """
    allow_list = [
        "www.youtube.com",
        "youtu.be",
    ]
    parsed_url = urlparse(user_video_url_input)
    if parsed_url.netloc in allow_list:
        if "youtube.com" in parsed_url.netloc:
            video_id = user_video_url_input.split("v=")[1]

        elif "youtu.be" in parsed_url.netloc:
            video_id = user_video_url_input.split("/")[-1]

    else:
        video_id = "Invalid URL. Please enter a valid YouTube video URL."

    return video_id


def main():
    """Runs the Streamlit app for the YouTube Comment Scraper."""

    st.set_page_config(
        page_title="YouTube Comment Scraper",
        page_icon="resources/video_library_favicon.png",
    )

    st.markdown("""# Welcome to the YouTube Comment Scraper App!""")

    st.markdown(
        "If you have not done so already, create a Google API Key. Watch this [YouTube video](https://www.youtube.com/watch?v=brCkpzAD0gc) to see how you can create a Google API Key."
    )
    st.markdown("### Instructions")
    st.markdown(
        """Just input your Google API Developer Key, the URL of a YouTube video, and a name for your CSV file then click submit.
                You will be able to download your CSV file once the scraping is complete."""
    )
    st.markdown(
        """This scraper was built using the [YouTube API](https://developers.google.com/youtube/v3)."""
    )
    st.markdown("### Limitations")
    st.markdown(
        """Scraping comments with the official YouTube Data API does come with its limitations. According to the [docs](https://googleapis.github.io/google-api-python-client/docs/dyn/youtube_v3.comments.html#list):"""
    )
    st.markdown(
        """> Note, currently YouTube features only one level of replies (ie replies to top level comments). However replies to replies may be supported in the future.
        """
    )
    st.markdown("### GitHub and Docker Hub")
    st.markdown(
        "Have an issue or feature request? Submit an issue on the [GitHub repository](https://github.com/Steven-Herrera/youtube-comment-microservice/tree/main)."
    )
    st.markdown(
        "Want to run this app locally? Pull the image from the [Docker Hub repository](https://hub.docker.com/repository/docker/stevenherrera/youtube-comment-microservice/general)."
    )

    with st.form(key="my_form_to_submit"):
        st.title("YouTube Comment Scraper")
        user_dev_key_input = st.text_input(
            "Enter Your Google API Developer Key", type="password"
        )
        user_video_url_input = st.text_input(
            "Enter the URL of a YouTube video",
            "https://www.youtube.com/watch?v=URmeTqglS58",
        )
        user_file_name_input = st.text_input(
            "Enter a name for your CSV file", "file.csv"
        )

        n = 0.14
        c1, c2 = st.columns([n, 1.0 - n], gap="small")
        with c1:
            submit_button = st.form_submit_button(
                label="Submit", help="Starts the scrape"
            )
        with c2:
            st.form_submit_button(
                "Cancel", on_click=st.session_state.clear(), help="Stops the scrape"
            )

    if submit_button:

        video_id = get_youtube_video_id(user_video_url_input)
        if video_id == "Invalid URL. Please enter a valid YouTube video URL.":
            st.write(f"{video_id}")
            return None

        _youtube_df_ = app(user_dev_key_input, video_id)
        if type(_youtube_df_) == str:
            # If youtube_df is a string, then an error occurred and a message is displayed
            st.write(f"{_youtube_df_}")
            return None

        youtube_df, comments_scraped, num_comments = _youtube_df_
        percent_scraped = f"{comments_scraped/num_comments:.0%}"
        youtube_csv = youtube_df.to_csv(index=False).encode("utf-8")
        st.write(
            f"{percent_scraped} of comments scraped. ({comments_scraped:,} out of {num_comments:,})"
        )
        st.dataframe(youtube_df)

        st.download_button(
            label="Press to Download",
            data=youtube_csv,
            file_name=user_file_name_input,
            mime="text/csv",
            key="download-csv",
        )

    return None


if __name__ == "__main__":
    main()
