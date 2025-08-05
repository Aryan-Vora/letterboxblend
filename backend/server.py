"""
LetterboxBlend FastAPI Server
Clean, modular implementation of the movie recommendation API.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, field_validator
import json
import re
from typing import List

from config import Config
from letterboxd_scraper import extract_movies_with_ratings, fetch_html_from_url
from omdb_client import OMDBClient
from recommendation_engine import blend_movies


def validate_letterboxd_url(url: str) -> bool:
    """
    Validate that a URL is a proper Letterboxd films URL.

    Args:
        url: The URL to validate

    Returns:
        bool: True if valid Letterboxd films URL, False otherwise
    """
    if not url:
        return False

    # Remove trailing slash for consistent checking
    clean_url = url.rstrip('/')

    # Check if it's a valid Letterboxd films URL
    pattern = r'^https://letterboxd\.com/[a-zA-Z0-9_-]+/films$'
    return bool(re.match(pattern, clean_url))


def convert_saved_data_format(saved_data):
    """
    Convert saved data format to the format expected by the recommendation engine.

    Args:
        saved_data: List of movie dictionaries from saved JSON files

    Returns:
        List of movie dictionaries in the expected format
    """
    converted_data = []
    for movie in saved_data:
        converted_movie = {
            'Title': movie.get('Title', ''),
            'title': movie.get('Title', ''),
            'year': movie.get('Year', ''),
            'rated': movie.get('Rated', ''),
            'runtime': movie.get('Runtime', ''),
            'Genre': movie.get('Genre', ''),
            'genre': movie.get('Genre', ''),
            'director': movie.get('Director', ''),
            'Actors': movie.get('Actors', ''),
            'actors': movie.get('Actors', ''),
            'Plot': movie.get('Plot', ''),
            'plot': movie.get('Plot', ''),
            'country': movie.get('Country', ''),
            'imdbRating': movie.get('imdbRating', 'N/A'),
            'imdb_rating': movie.get('imdbRating', 'N/A'),
            'box_office': movie.get('BoxOffice', 'N/A'),
            'letterboxRating': movie.get('letterboxRating', 0),
            'letterbox_rating': movie.get('letterboxRating', 0),
            'movie_slug': movie.get('movieSlug', '')
        }
        converted_data.append(converted_movie)
    return converted_data


app = FastAPI(
    title="LetterboxBlend API",
    description="Blend two users' movie preferences from Letterboxd",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Custom handler for validation errors to provide user-friendly messages."""
    errors = []
    for error in exc.errors():
        if 'letterboxd' in str(error.get('msg', '')).lower():
            errors.append({
                "field": error.get('loc', ['unknown'])[-1],
                "message": error.get('msg', 'Invalid URL format')
            })
        else:
            errors.append({
                "field": error.get('loc', ['unknown'])[-1],
                "message": error.get('msg', 'Validation error')
            })

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation failed",
            "errors": errors
        }
    )


class BlendRequest(BaseModel):
    """Request model for the blend endpoint."""
    user1_url: HttpUrl
    user2_url: HttpUrl

    @field_validator('user1_url', 'user2_url')
    @classmethod
    def validate_letterboxd_urls(cls, v):
        """Validate that URLs are proper Letterboxd films URLs."""
        url_str = str(v)
        if not validate_letterboxd_url(url_str):
            raise ValueError(
                'URL must be a valid Letterboxd films URL (e.g., https://letterboxd.com/username/films/)'
            )
        return v

    @field_validator('user2_url')
    @classmethod
    def validate_different_users(cls, v, info):
        """Ensure the two URLs are for different users."""
        if info.data and 'user1_url' in info.data and str(v) == str(info.data['user1_url']):
            raise ValueError('The two profile URLs must be different')
        return v


class BlendTestRequest(BaseModel):
    """Request model for the test blend endpoint using saved data."""
    user1_name: str = "rbaveje"
    user2_name: str = "vihaanbinges"


class MovieRecommendation(BaseModel):
    """Response model for movie recommendations."""
    title: str
    year: int
    rating: float
    votes: int
    genres: List[str]
    cast: List[str] = []
    extract: str = ""
    thumbnail: str = ""
    thumbnail_width: int = 0
    thumbnail_height: int = 0
    href: str = ""
    genre_score: float
    plot_score: float
    actor_score: float
    imdb_bonus: float
    recency_bonus: float
    combined_score: float


@app.post("/blend", response_model=List[MovieRecommendation])
async def blend_preferences(request: BlendRequest):
    """
    Blend two users' movie preferences and return recommendations.
    This endpoint performs the full pipeline: scraping, API calls, and blending.

    Args:
        request: Contains the two Letterboxd profile URLs

    Returns:
        List of movie recommendations with scores (up to Config.MAX_RECOMMENDATIONS)
    """
    try:
        omdb_client = OMDBClient()

        print(f"Fetching data for user 1: {request.user1_url}")
        try:
            user1_html = await fetch_html_from_url(str(request.user1_url))
            user1_movies_ratings = extract_movies_with_ratings(user1_html)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch data from first Letterboxd profile. Please check the URL is correct and accessible: {str(e)}"
            )

        try:
            user1_data = await omdb_client.enrich_movies_batch(user1_movies_ratings)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to enrich movie data for first user: {str(e)}"
            )

        print(f"Fetching data for user 2: {request.user2_url}")
        try:
            user2_html = await fetch_html_from_url(str(request.user2_url))
            user2_movies_ratings = extract_movies_with_ratings(user2_html)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch data from second Letterboxd profile. Please check the URL is correct and accessible: {str(e)}"
            )

        try:
            user2_data = await omdb_client.enrich_movies_batch(user2_movies_ratings)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to enrich movie data for second user: {str(e)}"
            )

        print(
            f"Processed {len(user1_data)} movies for user 1, {len(user2_data)} movies for user 2")

        if len(user1_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="No movies found for first user. Please ensure the profile has public movie ratings."
            )

        if len(user2_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="No movies found for second user. Please ensure the profile has public movie ratings."
            )

        try:
            with open(Config.MOVIES_DATABASE, 'r') as f:
                movies_database = json.load(f)
        except FileNotFoundError:
            raise HTTPException(
                status_code=500,
                detail=f"Movies database not found. Please ensure {Config.MOVIES_DATABASE} exists."
            )

        blended_movies = blend_movies(user1_data, user2_data, movies_database)

        recommendations = []
        for movie in blended_movies[:Config.MAX_RECOMMENDATIONS]:
            try:
                recommendations.append(MovieRecommendation(
                    title=movie.get('title', ''),
                    year=int(movie.get('year', 0)) if movie.get('year') else 0,
                    rating=float(movie.get('imdb_rating', 0.0)) if movie.get(
                        'imdb_rating', 'N/A') != 'N/A' else 0.0,
                    votes=int(movie.get('imdb_votes', 0)) if movie.get(
                        'imdb_votes') else 0,
                    genres=movie.get('genres', []),
                    cast=movie.get('cast', []),
                    extract=movie.get('extract', ''),
                    thumbnail=movie.get('thumbnail', ''),
                    thumbnail_width=int(movie.get('thumbnail_width', 0)) if movie.get(
                        'thumbnail_width') else 0,
                    thumbnail_height=int(movie.get('thumbnail_height', 0)) if movie.get(
                        'thumbnail_height') else 0,
                    href=movie.get('href', ''),
                    genre_score=float(movie.get('genre_score', 0.0)),
                    plot_score=float(movie.get('plot_score', 0.0)),
                    actor_score=float(movie.get('actor_score', 0.0)),
                    imdb_bonus=float(movie.get('imdb_bonus', 0.0)),
                    recency_bonus=float(movie.get('recency_bonus', 0.0)),
                    combined_score=float(movie.get('combined_score', 0.0))
                ))
            except (ValueError, TypeError) as e:
                print(f"Error converting movie data: {e}")
                continue

        print(f"Returning {len(recommendations)} recommendations")
        return recommendations

    except Exception as e:
        print(f"Error in blend_preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing blend request: {str(e)}"
        )


@app.post("/blend/test", response_model=List[MovieRecommendation])
async def blend_preferences_test(request: BlendTestRequest):
    """
    Blend two users' movie preferences using pre-saved data.
    This endpoint is for testing purposes and doesn't make API calls.

    Args:
        request: Contains user names (defaults to 'raj' and 'vihaan')

    Returns:
        List of movie recommendations with scores (up to Config.MAX_RECOMMENDATIONS)
    """
    try:
        user1_file = f"{request.user1_name}data.json"
        user2_file = f"{request.user2_name}data.json"

        try:
            with open(user1_file, 'r') as f:
                user1_data = json.load(f)
            print(f"Loaded {len(user1_data)} movies for {request.user1_name}")
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"User data file not found: {user1_file}"
            )

        try:
            with open(user2_file, 'r') as f:
                user2_data = json.load(f)
            print(f"Loaded {len(user2_data)} movies for {request.user2_name}")
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"User data file not found: {user2_file}"
            )

        user1_converted = convert_saved_data_format(user1_data)
        user2_converted = convert_saved_data_format(user2_data)

        try:
            with open(Config.MOVIES_DATABASE, 'r') as f:
                movies_database = json.load(f)
        except FileNotFoundError:
            raise HTTPException(
                status_code=500,
                detail=f"Movies database not found. Please ensure {Config.MOVIES_DATABASE} exists."
            )

        blended_movies = blend_movies(
            user1_converted, user2_converted, movies_database)

        recommendations = []
        for movie in blended_movies[:Config.MAX_RECOMMENDATIONS]:
            try:
                recommendations.append(MovieRecommendation(
                    title=movie.get('title', ''),
                    year=int(movie.get('year', 0)) if movie.get('year') else 0,
                    rating=float(movie.get('imdb_rating', 0.0)) if movie.get(
                        'imdb_rating', 'N/A') != 'N/A' else 0.0,
                    votes=int(movie.get('imdb_votes', 0)) if movie.get(
                        'imdb_votes') else 0,
                    genres=movie.get('genres', []),
                    cast=movie.get('cast', []),
                    extract=movie.get('extract', ''),
                    thumbnail=movie.get('thumbnail', ''),
                    thumbnail_width=int(movie.get('thumbnail_width', 0)) if movie.get(
                        'thumbnail_width') else 0,
                    thumbnail_height=int(movie.get('thumbnail_height', 0)) if movie.get(
                        'thumbnail_height') else 0,
                    href=movie.get('href', ''),
                    genre_score=float(movie.get('genre_score', 0.0)),
                    plot_score=float(movie.get('plot_score', 0.0)),
                    actor_score=float(movie.get('actor_score', 0.0)),
                    imdb_bonus=float(movie.get('imdb_bonus', 0.0)),
                    recency_bonus=float(movie.get('recency_bonus', 0.0)),
                    combined_score=float(movie.get('combined_score', 0.0))
                ))
            except (ValueError, TypeError) as e:
                print(f"Error converting movie data: {e}")
                continue

        print(f"Returning {len(recommendations)} recommendations")
        return recommendations

    except Exception as e:
        print(f"Error in blend_preferences_test: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing test blend request: {str(e)}"
        )


@app.get("/mock", response_model=List[MovieRecommendation])
async def get_mock_recommendations():
    """
    Get mock recommendations from the last generated blend.
    This endpoint serves pre-generated recommendations for faster testing.

    Returns:
        List of movie recommendations from the last blend operation
    """
    try:
        with open('mock_recommendations.json', 'r') as f:
            mock_data = json.load(f)

        recommendations = []
        for movie in mock_data[:Config.MAX_RECOMMENDATIONS]:
            try:
                recommendations.append(MovieRecommendation(
                    title=movie.get('title', ''),
                    year=int(movie.get('year', 0)) if movie.get('year') else 0,
                    rating=float(movie.get('imdb_rating', 0.0)) if movie.get(
                        'imdb_rating', 'N/A') != 'N/A' else 0.0,
                    votes=int(movie.get('imdb_votes', 0)) if movie.get(
                        'imdb_votes') else 0,
                    genres=movie.get('genres', []),
                    cast=movie.get('cast', []),
                    extract=movie.get('extract', ''),
                    thumbnail=movie.get('thumbnail', ''),
                    thumbnail_width=int(movie.get('thumbnail_width', 0)) if movie.get(
                        'thumbnail_width') else 0,
                    thumbnail_height=int(movie.get('thumbnail_height', 0)) if movie.get(
                        'thumbnail_height') else 0,
                    href=movie.get('href', ''),
                    genre_score=float(movie.get('genre_score', 0.0)),
                    plot_score=float(movie.get('plot_score', 0.0)),
                    actor_score=float(movie.get('actor_score', 0.0)),
                    imdb_bonus=float(movie.get('imdb_bonus', 0.0)),
                    recency_bonus=float(movie.get('recency_bonus', 0.0)),
                    combined_score=float(movie.get('combined_score', 0.0))
                ))
            except (ValueError, TypeError) as e:
                print(f"Error converting mock movie data: {e}")
                continue

        print(f"Returning {len(recommendations)} mock recommendations")
        return recommendations

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Mock recommendations file not found. Run a blend operation first to generate mock data."
        )
    except Exception as e:
        print(f"Error loading mock recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading mock recommendations: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "LetterboxBlend API v2.0",
        "description": "Blend two users' movie preferences from Letterboxd",
        "features": [
            "Modular architecture",
            "OMDB API integration",
            "Advanced recommendation algorithm",
            "Genre weight analysis",
            "Plot similarity matching",
            "Actor overlap detection"
        ],
        "endpoints": {
            "POST /blend": "Blend two users' movie preferences (full pipeline with API calls)",
            "POST /blend/test": "Blend using pre-saved data (for testing without API calls)",
            "GET /mock": "Get mock recommendations from the last generated blend (for fast testing)",
        },
        "example_request": {
            "full_pipeline": {
                "user1_url": "https://letterboxd.com/username1/films/",
                "user2_url": "https://letterboxd.com/username2/films/"
            },
            "test_endpoint": {
                "user1_name": "raj",
                "user2_name": "vihaan"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.SERVER_HOST, port=Config.SERVER_PORT)
