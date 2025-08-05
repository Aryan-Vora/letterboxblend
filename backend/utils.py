"""
Utility functions for LetterboxBlend API
Contains common helper functions used across the application.
"""
import re
from typing import Set


def calculate_plot_similarity(movie_extract: str, user_plots: str) -> float:
    """Calculate similarity between movie extract and user plot preferences."""
    if not movie_extract or not user_plots:
        return 0

    common_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                       'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'will', 'would', 'could', 'should'])

    movie_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', movie_extract.lower()))
    movie_words -= common_words

    user_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', user_plots.lower()))
    user_words -= common_words

    if not movie_words or not user_words:
        return 0

    intersection = len(movie_words.intersection(user_words))
    union = len(movie_words.union(user_words))

    return intersection / union if union > 0 else 0


def convert_stars_to_decimal(star_string: str) -> float:
    """Convert star symbols to decimal rating."""
    if not star_string or star_string == "No rating":
        return None
    full_stars = star_string.count('★')
    half_stars = star_string.count('½')
    decimal_rating = full_stars + (half_stars * 0.5)
    return decimal_rating


def extract_meaningful_words(text: str, min_length: int = 3) -> Set[str]:
    """Extract meaningful words from text, excluding common words."""
    common_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                       'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'will', 'would', 'could', 'should'])

    words = set(re.findall(rf'\b[a-zA-Z]{{{min_length},}}\b', text.lower()))
    return words - common_words


def clean_movie_title(title: str) -> str:
    """Clean and format movie title for API calls."""
    cleaned = re.sub(r'[^\w\s-]', '', title)
    return cleaned.strip()


def format_title_for_url(title: str) -> str:
    """Format movie title for URL encoding."""
    return title.replace(' ', '+')


def parse_year_from_title(title: str) -> tuple:
    """Extract year from title if present, return (title_without_year, year)."""
    words = title.split()
    if len(words) > 1 and words[-1].isdigit() and len(words[-1]) == 4:
        return ' '.join(words[:-1]), words[-1]
    return title, None
