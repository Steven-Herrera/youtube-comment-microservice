"""A module for testing the app.py module.

Functions:
    test_single_page: Test the app function with a video that has a single page of comments.
    test_multi_page: Test the app function with a video that has multiple pages of comments.
    test_bad_key: Test the app function with an invalid developer key.
    test_bad_video_id: Test the app function with an invalid video id.
    test_get_youtube_video_id: Test the get_youtube_video_id function on a valid URL
    test_get_youtube_video_id_short_url: Test the get_youtube_video_id function on a short URL
    test_get_youtube_video_id_bad_url: Test the get_youtube_video_id function on an invalid URL
"""
import os
import pandas as pd
import app

def test_single_page():
    """Test the app function with a video that has a single page of comments."""
    DEVELOPER_KEY = os.environ['DEVELOPER_KEY']
    youtube_video_id = "URmeTqglS58"

    df, comments_scraped, num_comments = app.app(DEVELOPER_KEY, youtube_video_id)
    assert isinstance(df, pd.DataFrame)
    assert isinstance(comments_scraped, int)
    assert isinstance(num_comments, int)

def test_multi_page():
    """Test the app function with a video that has multiple pages of comments."""
    DEVELOPER_KEY = os.environ['DEVELOPER_KEY']
    youtube_video_id = "s_o8dwzRlu4"

    df, comments_scraped, num_comments = app.app(DEVELOPER_KEY, youtube_video_id)
    assert isinstance(df, pd.DataFrame)
    assert isinstance(comments_scraped, int)
    assert isinstance(num_comments, int)

def test_bad_key():
    """Test the app function with a bad key."""
    DEVELOPER_KEY = "bad_key"
    youtube_video_id = "wJhYWbEi6NQ"

    df = app.app(DEVELOPER_KEY, youtube_video_id)
    assert df == 'API key not valid. Please pass a valid API key.'

def test_bad_video_id():
    """Test the app function with a bad video id."""
    DEVELOPER_KEY = os.environ['DEVELOPER_KEY']
    youtube_video_id = "bad_video_id"

    df = app.app(DEVELOPER_KEY, youtube_video_id)
    assert df == "No video found. Are you sure the URL is correct?"

def test_get_youtube_video_id():
    """Test the get_youtube_video_id function."""
    url = "https://www.youtube.com/watch?v=s_o8dwzRlu4"
    youtube_video_id = app.get_youtube_video_id(url)
    assert youtube_video_id == "s_o8dwzRlu4"

def test_get_youtube_video_id_short_url():
    """Test the get_youtube_video_id function with a short URL."""
    url = "https://youtu.be/HlGErt9s26Q"
    youtube_video_id = app.get_youtube_video_id(url)
    assert youtube_video_id == "HlGErt9s26Q"

def test_get_youtube_video_id_bad_url():
    """Test the get_youtube_video_id function with a bad URL."""
    url = "bad_url"
    youtube_video_id = app.get_youtube_video_id(url)
    assert youtube_video_id == "Invalid URL. Please enter a valid YouTube video URL."