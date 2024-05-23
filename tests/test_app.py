"""A module for testing the app.py module.

Functions:
    test_single_page: Test the app function with a video that has a single page of comments.
    test_multi_page: Test the app function with a video that has multiple pages of comments.
    test_bad_key: Test the app function with an invalid developer key.
    test_bad_video_id: Test the app function with an invalid video id.
"""
import os
import pandas as pd
import app

def test_single_page():
    """Test the app function with a video that has a single page of comments."""
    DEVELOPER_KEY = os.environ['DEVELOPER_KEY']
    youtube_video_id = "wJhYWbEi6NQ"

    df, comments_scraped, num_comments = app.app(DEVELOPER_KEY, youtube_video_id)
    assert isinstance(df, pd.DataFrame)
    assert isinstance(comments_scraped, int)
    assert isinstance(num_comments, int)

def test_multi_page():
    """Test the app function with a video that has multiple pages of comments."""
    DEVELOPER_KEY = os.environ['DEVELOPER_KEY']
    youtube_video_id = "bn_KRzohcAo"

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