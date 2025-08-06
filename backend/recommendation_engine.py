"""
Recommendation engine for blending movie preferences
Contains the core algorithm for finding movie recommendations based on user preferences.
"""
from collections import defaultdict
from typing import List, Dict, Any
from utils import calculate_plot_similarity
from config import Config


class RecommendationEngine:
    """Engine for generating movie recommendations based on user preferences."""

    def __init__(self, movies_database: List[Dict[str, Any]]):
        self.movies_database = movies_database

    def calculate_genre_weights(self, user_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate genre preferences for a user based on their movie ratings."""
        genre_stats = defaultdict(lambda: {'count': 0, 'total_rating': 0})

        for movie in user_data:
            if 'Genre' in movie and movie['Genre']:
                try:
                    rating = 0
                    if 'letterboxRating' in movie and movie['letterboxRating']:
                        rating = float(movie['letterboxRating'])
                    elif 'imdbRating' in movie and movie['imdbRating'] and movie['imdbRating'] != 'N/A':
                        rating = float(movie['imdbRating'])
                    elif 'Rating' in movie and movie['Rating']:
                        rating = float(movie['Rating'])
                    elif 'Your Rating' in movie and movie['Your Rating']:
                        rating = float(movie['Your Rating'])
                    else:
                        rating = 5.0

                    # Split genres and process each one (handle comma-separated genres)
                    genres = [genre.strip()
                              for genre in movie['Genre'].split(',')]
                    for genre in genres:
                        if genre:
                            genre_stats[genre]['count'] += 1
                            genre_stats[genre]['total_rating'] += rating
                except (ValueError, TypeError):
                    continue

        # Calculate average ratings and weights for genres
        genre_weights = {}
        for genre, stats in genre_stats.items():
            if stats['count'] > 0:
                avg_rating = stats['total_rating'] / stats['count']
                genre_weights[genre] = avg_rating * (1 + stats['count'] / 10)

        return genre_weights

    def get_common_genres(self, user1_weights: Dict[str, float], user2_weights: Dict[str, float]) -> Dict[str, float]:
        """Find common genres between two users and calculate combined weights."""
        user1_genres = set(user1_weights.keys())
        user2_genres = set(user2_weights.keys())
        common_genres_set = user1_genres.intersection(user2_genres)

        genre_weights = {}
        for genre in common_genres_set:
            if user1_weights.get(genre, 0) > 0 and user2_weights.get(genre, 0) > 0:
                combined_weight = (
                    user1_weights[genre] + user2_weights[genre]) / 2
                genre_weights[genre] = combined_weight

        if not genre_weights:
            # print("No weighted genres found, using fallback logic...")
            for genre in common_genres_set:
                genre_weights[genre] = 5.0
        return genre_weights

    def get_watched_movies(self, user_data: List[Dict[str, Any]]) -> set:
        """Extract set of movie titles that a user has watched."""
        watched = set()
        for movie in user_data:
            if 'Title' in movie and movie['Title']:
                watched.add(movie['Title'].lower().strip())
        return watched

    def extract_user_plots(self, user_data: List[Dict[str, Any]]) -> str:
        """Extract and combine plot information from user's movies."""
        plots = []
        for movie in user_data:
            if 'Plot' in movie and movie['Plot'] and movie['Plot'] != 'N/A':
                plots.append(movie['Plot'])
        return ' '.join(plots)

    def _extract_movie_rating(self, movie: Dict[str, Any]) -> float:
        """Extract rating from a movie, trying different field names."""
        if 'letterboxRating' in movie and movie['letterboxRating']:
            return float(movie['letterboxRating'])
        elif 'imdbRating' in movie and movie['imdbRating'] and movie['imdbRating'] != 'N/A':
            return float(movie['imdbRating'])
        elif 'Rating' in movie and movie['Rating']:
            return float(movie['Rating'])
        else:
            return 0.0

    def _extract_movie_actors(self, movie: Dict[str, Any]) -> List[str]:
        """Extract and parse actors from a movie."""
        actors_field = None
        for field in ['Actors', 'actors', 'cast', 'Cast']:
            if field in movie and movie[field] and movie[field] != 'N/A':
                actors_field = movie[field]
                break

        if not actors_field:
            return []

        if isinstance(actors_field, list):
            return [actor.strip() for actor in actors_field if actor.strip()]
        else:
            return [actor.strip() for actor in actors_field.split(',') if actor.strip()]

    def get_top_actors_for_user(self, user_data: List[Dict[str, Any]], top_count: int = 10) -> Dict[str, float]:
        """
        Extract top actors for a user based on their movie preferences and ratings.

        Args:
            user_data: User's movie data
            top_count: Number of top actors to return

        Returns:
            Dictionary mapping actor names to their importance scores
        """
        actor_scores = defaultdict(
            lambda: {'count': 0, 'total_rating': 0, 'weight': 0})

        for movie in user_data:
            rating = self._extract_movie_rating(movie)
            if rating == 0.0:
                continue

            actors = self._extract_movie_actors(movie)
            if not actors:
                continue

            # Only consider first 5 actors (main cast)
            for i, actor in enumerate(actors[:5]):
                if actor:
                    # Position weight: first actor gets full weight, others get diminishing weight
                    # 1.0, 0.85, 0.7, 0.55, 0.4
                    position_weight = 1.0 - (i * 0.15)
                    weighted_rating = rating * position_weight

                    actor_scores[actor.lower()]['count'] += 1
                    actor_scores[actor.lower(
                    )]['total_rating'] += weighted_rating
                    actor_scores[actor.lower()]['weight'] += position_weight

        actor_final_scores = {}
        for actor_key, stats in actor_scores.items():
            if stats['count'] >= 2:
                avg_rating = stats['total_rating'] / \
                    stats['weight'] if stats['weight'] > 0 else 0
                frequency_bonus = min(stats['count'] / 5.0, 2.0)
                final_score = avg_rating * frequency_bonus
                actor_final_scores[actor_key] = final_score

        sorted_actors = sorted(actor_final_scores.items(),
                               key=lambda x: x[1], reverse=True)
        return dict(sorted_actors[:top_count])

    def get_actor_overlap_score(self, movie_actors: str, user1_data: List[Dict[str, Any]], user2_data: List[Dict[str, Any]]) -> float:
        """Calculate actor overlap score using top actors from both users, weighted by letterbox ratings."""
        if not movie_actors or movie_actors == 'N/A':
            return 0

        if isinstance(movie_actors, list):
            movie_actor_set = set(actor.strip().lower()
                                  for actor in movie_actors if actor.strip())
        else:
            movie_actor_set = set(actor.strip().lower()
                                  for actor in movie_actors.split(',') if actor.strip())

        if not movie_actor_set:
            return 0

        combined_actor_scores = {}

        for user_data in [user1_data, user2_data]:
            for movie in user_data:
                rating = self._extract_movie_rating(movie)
                if rating == 0.0:
                    continue

                actors = self._extract_movie_actors(movie)
                if not actors:
                    continue

                # Weight actors by position and rating
                for i, actor in enumerate(actors[:5]):
                    if actor:
                        actor_key = actor.lower()
                        position_weight = 1.0 - (i * 0.15)
                        rating_weight = rating / 5.0

                        final_weight = position_weight * rating_weight

                        if actor_key not in combined_actor_scores:
                            combined_actor_scores[actor_key] = {
                                'total_weight': 0, 'movie_count': 0}

                        combined_actor_scores[actor_key]['total_weight'] += final_weight
                        combined_actor_scores[actor_key]['movie_count'] += 1

        total_score = 0
        matches_found = 0

        for movie_actor in movie_actor_set:
            if movie_actor in combined_actor_scores:
                matches_found += 1
                actor_data = combined_actor_scores[movie_actor]

                avg_weight = actor_data['total_weight'] / \
                    actor_data['movie_count']

                frequency_bonus = min(
                    actor_data['movie_count'] / 3.0, 1.5)

                actor_importance = avg_weight * frequency_bonus

                if matches_found == 1:
                    base_score = 1.0
                elif matches_found <= 3:
                    base_score = 0.6
                else:
                    base_score = 0.3

                actor_score = base_score * actor_importance
                total_score += actor_score

        final_score = min(total_score, 3.0)

        return final_score

    def calculate_movie_score(self, movie: Dict[str, Any], common_genres: Dict[str, float],
                              user1_plots: str, user2_plots: str,
                              user1_data: List[Dict[str, Any]], user2_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate comprehensive score for a movie based on multiple factors."""
        scores = {
            'genre_score': 0.0,
            'plot_score': 0.0,
            'actor_score': 0.0,
            'imdb_bonus': 0.0,
            'recency_bonus': 0.0
        }

        # 1. Genre score
        if 'genres' in movie and movie['genres']:
            movie_genres = movie['genres']
            genre_score = 0
            matching_genres = []

            for genre in movie_genres:
                if genre in common_genres:
                    matching_genres.append(genre)
                    genre_score += common_genres[genre]

            if matching_genres:
                scores['genre_score'] = (
                    genre_score / len(matching_genres)) / 2

            genre_diversity_bonus = min(
                len(matching_genres) * 0.5, 2.0) / 2
            scores['genre_score'] += genre_diversity_bonus

        # 2. Plot similarity score
        if 'extract' in movie and movie['extract']:
            combined_user_plots = user1_plots + ' ' + user2_plots
            plot_similarity = calculate_plot_similarity(
                movie['extract'], combined_user_plots) * 100
            scores['plot_score'] = min(
                plot_similarity, Config.MAX_PLOT_SCORE)  # this is to prevent wacky outliers from becoming #1

        # 3. Actor overlap score
        movie_actors = movie.get('cast', []) or movie.get('Actors', '')
        if movie_actors:
            # Handle both list format (cast) and string format (Actors)
            if isinstance(movie_actors, list):
                actor_string = ', '.join(movie_actors)
            else:
                actor_string = movie_actors

            scores['actor_score'] = self.get_actor_overlap_score(
                actor_string, user1_data, user2_data)

        # 4. IMDB rating bonus
        if 'imdb_rating' in movie and movie['imdb_rating'] and movie['imdb_rating'] != 'N/A':
            try:
                imdb_rating = float(movie['imdb_rating'])
                scores['imdb_bonus'] = (
                    imdb_rating - Config.MIN_IMDB_RATING) * 0.5 if imdb_rating > Config.MIN_IMDB_RATING else 0
            except (ValueError, TypeError):
                pass

        # 5. Recency bonus
        if 'year' in movie and movie['year']:
            try:
                year = int(movie['year'])
                current_year = 2025  # Current year

                if year >= 2020:
                    years_old = current_year - year
                    scores['recency_bonus'] = max(3.0 - (years_old * 0.2), 2.0)
                elif year >= 2010:
                    years_since_2010 = year - 2010
                    scores['recency_bonus'] = 1.0 + \
                        (years_since_2010 * 0.1)  # 1.0 to 2.0 range
                elif year >= 2000:
                    years_since_2000 = year - 2000
                    scores['recency_bonus'] = 0.2 + \
                        (years_since_2000 * 0.08)  # 0.2 to 1.0 range
            except (ValueError, TypeError):
                pass

        return scores

    def apply_genre_diversity(self, candidate_movies: List[Dict[str, Any]], common_genres: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Apply genre diversity to ensure balanced recommendations with interleaved genres.
        This prevents the same genre from dominating consecutive positions.

        Args:
            candidate_movies: List of scored movies
            common_genres: Dictionary of common genres and their weights

        Returns:
            Balanced list of movies with genre diversity and interleaved ranking
        """
        if len(candidate_movies) <= 50:
            return candidate_movies

        top_genres = sorted(common_genres.items(),
                            key=lambda x: x[1], reverse=True)
        all_genre_names = [genre for genre, _ in top_genres]

        # print(f"Applying genre diversity across genres: {all_genre_names[:5]}")

        genre_groups = {}
        for genre_name in all_genre_names:
            genre_groups[genre_name] = []
        genre_groups['other'] = []

        for movie in candidate_movies:
            movie_genres = movie.get('genres', [])
            if not movie_genres:
                genre_groups['other'].append(movie)
                continue

            primary_genre = None
            highest_weight = 0

            for genre in movie_genres:
                if genre in common_genres and common_genres[genre] > highest_weight:
                    highest_weight = common_genres[genre]
                    primary_genre = genre

            if primary_genre:
                genre_groups[primary_genre].append(movie)
            else:
                genre_groups['other'].append(movie)

        for genre in genre_groups:
            genre_groups[genre].sort(key=lambda x: x.get(
                'combined_score', 0), reverse=True)

        balanced_movies = []
        genre_indices = {genre: 0 for genre in genre_groups}

        # interleave genres to we dont get 15 dramas in a row
        available_genres = [
            genre for genre in genre_groups if len(genre_groups[genre]) > 0]

        total_weight = sum(common_genres.get(g, 0)
                           for g in available_genres if g != 'other') + 1  # +1 for other
        genre_targets = {}
        for genre in available_genres:
            if genre == 'other':
                weight = 1.0
            else:
                weight = common_genres.get(genre, 0)

            target = int((weight / total_weight) * Config.MAX_RECOMMENDATIONS)
            target = min(target, len(genre_groups[genre]))
            genre_targets[genre] = max(target, 1) if len(
                genre_groups[genre]) > 0 else 0

        # print(f"Genre targets: {genre_targets}")

        sorted_genres = sorted(
            available_genres, key=lambda g: genre_targets.get(g, 0), reverse=True)

        last_genre = None
        consecutive_count = 0

        while len(balanced_movies) < Config.MAX_RECOMMENDATIONS:
            added_movie = False

            for genre in sorted_genres:
                if (genre_indices[genre] < len(genre_groups[genre]) and
                        genre_indices[genre] < genre_targets[genre]):

                    if genre != last_genre or consecutive_count < 2:
                        movie = genre_groups[genre][genre_indices[genre]]
                        balanced_movies.append(movie)
                        genre_indices[genre] += 1

                        if genre == last_genre:
                            consecutive_count += 1
                        else:
                            consecutive_count = 1
                            last_genre = genre

                        # print(f"Added '{movie.get('title', 'Unknown')}' from genre '{genre}' "
                        #       f"(pos: {len(balanced_movies)}, score: {movie.get('combined_score', 0):.2f})")
                        added_movie = True
                        break

            if not added_movie:
                for genre in available_genres:
                    if genre_indices[genre] < len(genre_groups[genre]):
                        movie = genre_groups[genre][genre_indices[genre]]
                        balanced_movies.append(movie)
                        genre_indices[genre] += 1
                        last_genre = genre
                        consecutive_count = 1
                        added_movie = True
                        break

            if not added_movie:
                break

        # print(
        #     f"Generated {len(balanced_movies)} recommendations with genre diversity")

        final_genre_count = {}
        for movie in balanced_movies:
            primary_genre = movie.get('genres', ['Unknown'])[
                0] if movie.get('genres') else 'Unknown'
            final_genre_count[primary_genre] = final_genre_count.get(
                primary_genre, 0) + 1

        # print("Final genre distribution:", dict(
        #     sorted(final_genre_count.items(), key=lambda x: x[1], reverse=True)))

        return balanced_movies[:Config.MAX_RECOMMENDATIONS]

    def blend_movies(self, user1_data: List[Dict[str, Any]], user2_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Main blending algorithm that combines two users' movie preferences.

        Args:
            user1_data: First user's movie data
            user2_data: Second user's movie data

        Returns:
            List of recommended movies with scores, sorted by combined score
        """
        # print(
        #     f"Starting blend with {len(user1_data)} + {len(user2_data)} user movies (limited to top 100 rated movies per user for OMDB processing)")
        # print(f"Database contains {len(self.movies_database)} movies")

        user1_watched = self.get_watched_movies(user1_data)
        user2_watched = self.get_watched_movies(user2_data)

        user1_genre_weights = self.calculate_genre_weights(user1_data)
        user2_genre_weights = self.calculate_genre_weights(user2_data)

        # print(f"User1 genres: {sorted(list(user1_genre_weights.keys()))[:10]}")
        # print(f"User2 genres: {sorted(list(user2_genre_weights.keys()))[:10]}")

        common_genres = self.get_common_genres(
            user1_genre_weights, user2_genre_weights)

        # print(f"Found {len(common_genres)} common genres")
        # print(f"Top common genres by weight: {sorted_genres[:5]}")

        if len(common_genres) == 0:
            # print("Warning: No common genres found! Check genre format consistency.")
            pass
        else:
            # print(
            #     f"Balancing recommendations across top genres: {list(common_genres.keys())[:10]}")
            pass

        user1_plots = self.extract_user_plots(user1_data)
        user2_plots = self.extract_user_plots(user2_data)

        candidate_movies = []

        for movie in self.movies_database:
            movie_title = movie.get('title', '').lower().strip()
            if movie_title in user1_watched or movie_title in user2_watched:
                continue

            movie_genres = movie.get('genres', [])
            if not movie_genres:
                continue

            normalized_movie_genres = [g.strip() for g in movie_genres]
            normalized_common_genres = [g.strip()
                                        for g in common_genres.keys()]

            genre_match = any(
                genre in normalized_common_genres for genre in normalized_movie_genres)
            if not genre_match:
                continue

            try:
                imdb_rating = float(movie.get('imdb_rating', 0))
                if imdb_rating < Config.MIN_IMDB_RATING:
                    continue

                movie_votes = movie.get('imdb_votes', 0)
                if movie_votes < 1000:
                    continue
            except (ValueError, TypeError):
                continue

            scores = self.calculate_movie_score(
                movie, common_genres, user1_plots, user2_plots, user1_data, user2_data
            )

            combined_score = (
                scores['genre_score'] * Config.GENRE_WEIGHT +
                scores['plot_score'] * Config.PLOT_WEIGHT +
                scores['actor_score'] * Config.ACTOR_WEIGHT +
                scores['imdb_bonus'] * Config.IMDB_BONUS_WEIGHT +
                scores['recency_bonus']
            )

            if combined_score > 0:
                movie_result = movie.copy()
                movie_result.update(scores)
                movie_result['combined_score'] = combined_score

                # Create unique key for frontend to prevent duplicate key issues
                title = movie_result.get('title', 'Unknown')
                year = movie_result.get('year', '')
                imdb_id = movie_result.get('imdb_id', '')
                if year:
                    unique_key = f"{title}_{year}"
                elif imdb_id:
                    unique_key = f"{title}_{imdb_id}"
                else:
                    unique_key = f"{title}_{len(candidate_movies)}"

                movie_result['unique_key'] = unique_key
                candidate_movies.append(movie_result)

        # Sort by combined score (descending), then by IMDB rating, then by vote count
        candidate_movies.sort(key=lambda x: (
            x['combined_score'],
            float(x.get('imdb_rating', 0)) if x.get(
                'imdb_rating', 'N/A') != 'N/A' else 0,
            int(x.get('imdb_votes', 0)) if x.get('imdb_votes') else 0
        ), reverse=True)

        balanced_movies = self.apply_genre_diversity(
            candidate_movies, common_genres)

        # print(
        #     f"Generated {len(candidate_movies)} recommendations, balanced to {len(balanced_movies)}")

        # Save results to file for mock endpoint
        # try:
        #     with open('mock_recommendations.json', 'w') as f:
        #         json.dump(balanced_movies, f, indent=2, default=str)
        #     # print(
        #     #     f"Saved {len(balanced_movies)} recommendations to mock_recommendations.json")
        # except Exception as e:
        #     # print(f"Error saving mock recommendations: {e}")
        #     pass

        return balanced_movies


def blend_movies(user1_data: List[Dict[str, Any]], user2_data: List[Dict[str, Any]],
                 movies_database: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convenience function for blending movies using the recommendation engine.

    Args:
        user1_data: First user's movie data
        user2_data: Second user's movie data  
        movies_database: Database of movies to recommend from

    Returns:
        List of recommended movies with scores
    """
    engine = RecommendationEngine(movies_database)
    return engine.blend_movies(user1_data, user2_data)
