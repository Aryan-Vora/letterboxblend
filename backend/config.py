"""
Configuration settings for LetterboxBlend API
Centralized configuration management.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 8000

    OMDB_API_KEY = os.getenv('OMDB_API_KEY')
    OMDB_BASE_URL = "https://www.omdbapi.com/"

    MOVIES_DATABASE = "movies_with_ratings.json"
    IMDB_RATINGS_FILE = "extradata/title.ratings.tsv"
    IMDB_TITLES_FILE = "extradata/title.akas.tsv"
    IMDB_US_TITLES_FILE = "extradata/title.akas.us.tsv"
    IMDB_MOVIES_FILE = "extradata/title.akas.movies.tsv"

    MIN_IMDB_RATING = 5.0
    MAX_RECOMMENDATIONS = 50
    MAX_MOVIES_PER_USER = 100

    GENRE_WEIGHT = 0.2
    PLOT_WEIGHT = 0.4
    ACTOR_WEIGHT = 0.4
    IMDB_BONUS_WEIGHT = 0.4
    MAX_PLOT_SCORE = 5.0

    REQUEST_TIMEOUT = 60
    MAX_RETRIES = 3

    @classmethod
    def validate(cls):
        """Validate configuration settings."""
        if not cls.OMDB_API_KEY:
            print("Warning: OMDB_API_KEY not set. API functionality will be limited.")

        if not os.path.exists(cls.MOVIES_DATABASE):
            print(f"Warning: Movies database {cls.MOVIES_DATABASE} not found.")

        return True


Config.validate()
