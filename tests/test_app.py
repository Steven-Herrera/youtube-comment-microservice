"""A module for testing the app.py module."""
import os
import pandas as pd
from app import app

def test_app():
    DEVELOPER_KEY = os.environ['DEVELOPER_KEY']
    youtube_video_id = "o-YBDTqX_ZU"

    df = app(DEVELOPER_KEY, youtube_video_id)
    assert isinstance(df, pd.DataFrame)