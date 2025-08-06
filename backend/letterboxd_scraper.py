"""
Letterboxd scraper module
Handles web scraping of Letterboxd user profiles and movie data.
"""
import re
import aiohttp
from typing import List, Dict, Any, Tuple
from fastapi import HTTPException
from utils import convert_stars_to_decimal
from config import Config


async def fetch_html_from_url(url: str) -> str:
    """Fetch HTML content from a given URL."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(str(url)) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Error fetching HTML from {url}: {e}")


def extract_movies_with_ratings(html_content: str) -> List[Tuple[str, float]]:
    """
    Extract movie titles and their corresponding star ratings from HTML content.
    Returns only the top-rated movies (limited by Config.MAX_MOVIES_PER_USER) to reduce OMDB API calls.
    """
    movie_pattern = r'<li class="poster-container">(.*?)</li>'
    movie_containers = re.findall(movie_pattern, html_content, re.DOTALL)

    movies_with_ratings = []

    for container in movie_containers:
        title_match = re.search(r'data-film-slug="([^"]+)"', container)
        rating_match = re.search(
            r'<span class="rating[^"]*"[^>]*>(.*?)</span>', container)

        if title_match:
            title = title_match.group(1)
            if rating_match:
                rating_text = rating_match.group(1).strip()
                decimal_rating = convert_stars_to_decimal(rating_text)
                if decimal_rating is not None:
                    movies_with_ratings.append((title, decimal_rating))

    movies_with_ratings.sort(key=lambda x: x[1], reverse=True)
    limited_movies = movies_with_ratings[:Config.MAX_MOVIES_PER_USER]

    print(
        f"Extracted {len(movies_with_ratings)} total movies, limiting to top {len(limited_movies)} for OMDB processing")

    return limited_movies


async def scrape_user_preferences(url: str) -> Dict[str, Any]:
    """
    Scrape a user's Letterboxd profile for movie preferences.
    Returns a dictionary with movies, ratings, and preference data.
    """
    html_content = await fetch_html_from_url(url)
    movies_with_ratings = extract_movies_with_ratings(html_content)

    user_data = {
        'movies': movies_with_ratings,
        'total_movies': len(movies_with_ratings),
        'avg_rating': sum(rating for _, rating in movies_with_ratings) / len(movies_with_ratings) if movies_with_ratings else 0
    }

    return user_data


def extract_user_plots(user_movies: List[Dict[str, Any]]) -> str:
    """Extract and combine plot information from user's movie data."""
    plots = []
    for movie in user_movies:
        if isinstance(movie, dict) and movie.get('Plot') and movie['Plot'] != 'N/A':
            plots.append(movie['Plot'])
    return ' '.join(plots)


def get_user_genre_preferences(user_movies: List[Dict[str, Any]]) -> Dict[str, float]:
    """Analyze user's genre preferences based on their rated movies."""
    genre_scores = {}
    genre_counts = {}

    for movie in user_movies:
        if isinstance(movie, dict) and movie.get('letterboxRating') and movie.get('Genre'):
            rating = movie['letterboxRating']
            genres = movie['Genre'].split(
                ', ') if movie['Genre'] != 'N/A' else []

            for genre in genres:
                genre = genre.strip()
                if genre not in genre_scores:
                    genre_scores[genre] = 0
                    genre_counts[genre] = 0

                genre_scores[genre] += rating
                genre_counts[genre] += 1

    # Calculate average scores for each genre
    for genre in genre_scores:
        if genre_counts[genre] > 0:
            genre_scores[genre] = genre_scores[genre] / genre_counts[genre]

    return genre_scores
