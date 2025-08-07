"""
OMDB API client for fetching movie data
Handles all interactions with the OMDB API with key rotation and failure tracking
"""
import aiohttp
import re
from typing import Dict, Any, List, Tuple, Optional
from utils import parse_year_from_title, clean_movie_title
from config import Config


class APIBudgetExhausted(Exception):
    """Raised when all API keys have been exhausted."""
    pass


class OMDBClient:
    """Client for interacting with the OMDB API with key rotation."""

    def __init__(self):
        self.api_keys = Config.get_api_keys()
        self.current_key_index = 0
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.base_url = Config.OMDB_BASE_URL
        self.timeout = Config.REQUEST_TIMEOUT
        self.max_retries = Config.MAX_RETRIES

    def get_current_api_key(self) -> Optional[str]:
        """Get the current API key."""
        if not self.api_keys:
            return None
        return self.api_keys[self.current_key_index]

    def rotate_api_key(self):
        """Rotate to the next API key."""
        if not self.api_keys:
            return

        self.current_key_index = (
            self.current_key_index + 1) % len(self.api_keys)
        print(f"Rotated to API key {self.current_key_index + 1}")

    def _is_rate_limit_error(self, response_data: Dict[str, Any]) -> bool:
        """Check if the response indicates a rate limit or quota error."""
        if response_data.get('Response') == 'False':
            error_msg = response_data.get('Error', '').lower()
            return any(phrase in error_msg for phrase in [
                'daily limit',
                'quota',
                'rate limit',
                'too many requests',
                'request limit',
                'api limit'
            ])
        return False

    async def _make_api_request_with_rotation(self, session: aiohttp.ClientSession, title: str, year: str = None) -> Dict[str, Any]:
        """Make a request to the OMDB API with key rotation on failure."""
        if not self.api_keys:
            raise APIBudgetExhausted("No API keys available")

        if self.consecutive_failures >= self.max_consecutive_failures:
            raise APIBudgetExhausted(
                "All API keys exhausted - please try again tomorrow")

        params = {
            't': title,
            'apikey': self.get_current_api_key()
        }
        if year:
            params['y'] = year

        timeout = aiohttp.ClientTimeout(total=self.timeout)

        try:
            async with session.get(self.base_url, params=params, timeout=timeout) as response:
                if response.status == 401:
                    print(
                        f"API key {self.current_key_index + 1} unauthorized, rotating...")
                    self.rotate_api_key()
                    self.consecutive_failures += 1

                    if self.consecutive_failures >= self.max_consecutive_failures:
                        raise APIBudgetExhausted(
                            "All API keys exhausted - please try again tomorrow")

                    return await self._make_api_request_with_rotation(session, title, year)

                response_data = await response.json()

                if self._is_rate_limit_error(response_data):
                    print(
                        f"API key {self.current_key_index + 1} hit rate limit, rotating...")
                    self.rotate_api_key()
                    self.consecutive_failures += 1

                    if self.consecutive_failures >= self.max_consecutive_failures:
                        raise APIBudgetExhausted(
                            "All API keys exhausted - please try again tomorrow")

                    return await self._make_api_request_with_rotation(session, title, year)

                if response_data.get('Response') == 'True':
                    self.consecutive_failures = 0

                return response_data

        except aiohttp.ClientError as e:
            print(
                f"Network error with API key {self.current_key_index + 1}: {e}")
            self.rotate_api_key()
            self.consecutive_failures += 1

            if self.consecutive_failures >= self.max_consecutive_failures:
                raise APIBudgetExhausted(
                    "All API keys exhausted - please try again tomorrow")

            return await self._make_api_request_with_rotation(session, title, year)

    def _format_movie_title(self, movie_slug: str) -> str:
        """Convert movie slug to proper title format for OMDB API."""
        return movie_slug.replace('-', ' ').title()

    async def get_movie_data(self, movie_slug: str, letterbox_rating: float) -> Dict[str, Any]:
        """
        Get enriched movie data from OMDB API.

        Args:
            movie_slug: The movie slug from Letterboxd
            letterbox_rating: The user's rating on Letterboxd

        Returns:
            Dictionary with enriched movie data
        """
        if not self.api_keys:
            return self._create_minimal_movie_data(movie_slug, letterbox_rating)

        movie_title = self._format_movie_title(movie_slug)
        cleaned_title = clean_movie_title(movie_title)

        async with aiohttp.ClientSession() as session:
            try:
                omdb_data = await self._make_api_request_with_rotation(session, cleaned_title)

                if omdb_data.get('Response') == 'True':
                    return self._create_movie_data(omdb_data, letterbox_rating, movie_slug)

                title_without_year, extracted_year = parse_year_from_title(
                    cleaned_title)
                if extracted_year:
                    omdb_data = await self._make_api_request_with_rotation(session, title_without_year)

                    if omdb_data.get('Response') == 'True':
                        return self._create_movie_data(omdb_data, letterbox_rating, movie_slug)

                return self._create_minimal_movie_data(movie_slug, letterbox_rating)

            except APIBudgetExhausted:
                raise
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

        Raises:
            APIBudgetExhausted: When all API keys are exhausted
        """
        enriched_movies = []

        for movie_slug, letterbox_rating in movies_with_ratings:
            try:
                movie_data = await self.get_movie_data(movie_slug, letterbox_rating)
                enriched_movies.append(movie_data)
            except APIBudgetExhausted:
                print(
                    f"API budget exhausted while processing movie: {movie_slug}")
                raise

        return enriched_movies
