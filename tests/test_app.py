"""A module for testing the app.py module."""
import os
import pandas as pd
from app import app

def test_single_page():
    DEVELOPER_KEY = os.environ['DEVELOPER_KEY']
    youtube_video_id = "wJhYWbEi6NQ"

    df = app(DEVELOPER_KEY, youtube_video_id)
    assert isinstance(df, pd.DataFrame)

def test_multi_page():
    DEVELOPER_KEY = os.environ['DEVELOPER_KEY']
    youtube_video_id = "bn_KRzohcAo"

    df = app(DEVELOPER_KEY, youtube_video_id)
    assert isinstance(df, pd.DataFrame)