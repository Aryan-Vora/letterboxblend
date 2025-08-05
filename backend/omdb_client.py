"""
OMDB API client for fetching movie data
Handles all interactions with the OMDB API

"""
import aiohttp
from typing import Dict, Any, List, Tuple, Optional
from utils import parse_year_from_title, clean_movie_title
from config import Config


class OMDBClient:
    """Client for interacting with the OMDB API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.OMDB_API_KEY
        self.base_url = Config.OMDB_BASE_URL
        self.timeout = Config.REQUEST_TIMEOUT
        self.max_retries = Config.MAX_RETRIES

    def _format_movie_title(self, movie_slug: str) -> str:
        """Convert movie slug to proper title format for OMDB API."""
        return movie_slug.replace('-', ' ').title()

    async def _make_api_request(self, session: aiohttp.ClientSession, title: str, year: str = None) -> Dict[str, Any]:
        """Make a request to the OMDB API."""
        params = {
            't': title,
            'apikey': self.api_key
        }
        if year:
            params['y'] = year

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with session.get(self.base_url, params=params, timeout=timeout) as response:
            return await response.json()

    async def get_movie_data(self, movie_slug: str, letterbox_rating: float) -> Dict[str, Any]:
        """
        Get enriched movie data from OMDB API.

        Args:
            movie_slug: The movie slug from Letterboxd
            letterbox_rating: The user's rating on Letterboxd

        Returns:
            Dictionary with enriched movie data
        """
        if not self.api_key:
            return self._create_minimal_movie_data(movie_slug, letterbox_rating)

        movie_title = self._format_movie_title(movie_slug)
        cleaned_title = clean_movie_title(movie_title)

        async with aiohttp.ClientSession() as session:
            try:
                omdb_data = await self._make_api_request(session, cleaned_title)

                if omdb_data.get('Response') == 'True':
                    return self._create_movie_data(omdb_data, letterbox_rating, movie_slug)

                title_without_year, extracted_year = parse_year_from_title(
                    cleaned_title)
                if extracted_year:
                    omdb_data = await self._make_api_request(session, title_without_year)

                    if omdb_data.get('Response') == 'True':
                        return self._create_movie_data(omdb_data, letterbox_rating, movie_slug)

                return self._create_minimal_movie_data(movie_slug, letterbox_rating)

            except Exception as e:
                print(f"Error fetching OMDB data for {movie_title}: {e}")
                return self._create_minimal_movie_data(movie_slug, letterbox_rating)

    def _create_movie_data(self, omdb_data: Dict[str, Any], letterbox_rating: float, movie_slug: str) -> Dict[str, Any]:
        """Create a standardized movie data dictionary from OMDB response."""
        return {
            "Title": omdb_data.get("Title", "N/A"),
            "Year": omdb_data.get("Year", "N/A"),
            "Rated": omdb_data.get("Rated", "N/A"),
            "Runtime": omdb_data.get("Runtime", "N/A"),
            "Genre": omdb_data.get("Genre", "N/A"),
            "Director": omdb_data.get("Director", "N/A"),
            "Actors": omdb_data.get("Actors", "N/A"),
            "Plot": omdb_data.get("Plot", "N/A"),
            "Country": omdb_data.get("Country", "N/A"),
            "imdbRating": omdb_data.get("imdbRating", "N/A"),
            "BoxOffice": omdb_data.get("BoxOffice", "N/A"),
            "letterboxRating": letterbox_rating,
            "movieSlug": movie_slug
        }

    def _create_minimal_movie_data(self, movie_slug: str, letterbox_rating: float) -> Dict[str, Any]:
        """Create minimal movie data when OMDB API is unavailable or movie not found."""
        movie_title = self._format_movie_title(movie_slug)
        return {
            "Title": movie_title,
            "Year": "N/A",
            "Rated": "N/A",
            "Runtime": "N/A",
            "Genre": "N/A",
            "Director": "N/A",
            "Actors": "N/A",
            "Plot": "N/A",
            "Country": "N/A",
            "imdbRating": "N/A",
            "BoxOffice": "N/A",
            "letterboxRating": letterbox_rating,
            "movieSlug": movie_slug
        }

    async def enrich_movies_batch(self, movies_with_ratings: List[Tuple[str, float]]) -> List[Dict[str, Any]]:
        """
        Enrich a batch of movies with OMDB data.

        Args:
            movies_with_ratings: List of tuples (movie_slug, letterbox_rating)

        Returns:
            List of enriched movie dictionaries
        """
        enriched_movies = []

        for movie_slug, letterbox_rating in movies_with_ratings:
            movie_data = await self.get_movie_data(movie_slug, letterbox_rating)
            enriched_movies.append(movie_data)

        return enriched_movies
