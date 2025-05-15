# Movie Recommendation System 🎥

[![Streamlit App](https://img.shields.io/badge/Streamlit-Deployed-brightgreen)](https://cinesuggests.streamlit.app/)

## Overview
This is a content-based movie recommendation system that suggests movies similar to the one selected by the user. The recommendations are based on movie metadata such as genres, keywords, and cast. The project uses The Movie Database (TMDB) API to fetch movie posters and metadata, providing a visually appealing and interactive experience.

## Features
- **Movie Recommendations**: Get personalized movie suggestions based on your favorite movie.
- **Movie Posters**: Displays high-quality posters fetched from TMDB API.
- **Interactive UI**: Built with Streamlit for a seamless user experience.
- **Caching**: Uses a local cache to reduce API calls and improve performance.

## Live Demo
Check out the live version of the project here:  
👉 [CineSuggests](https://cinesuggests.streamlit.app/)

## How It Works
1. Select a movie from the dropdown menu.
2. The system calculates similarity scores using precomputed data.
3. Fetches movie posters and metadata from TMDB API.
4. Displays the top 5 recommended movies with their posters.

## Project Structure
```
Movie-Recommendation-Project_(Content-based)/
├── app.py                  # Main application file for Streamlit
├── notebook86c26b4f17.ipynb # Jupyter Notebook for data exploration and preprocessing
├── sample.ipynb            # Additional notebook (if applicable)
├── tmdb_movie_metadata/    # Folder containing raw TMDB dataset
│   ├── tmdb_5000_credits.csv
│   └── tmdb_5000_movies.csv
├── similarity.pkl          # Precomputed similarity matrix (pickle file)
├── movie_list.pkl          # Preprocessed movie metadata (pickle file)
├── poster_cache.json       # Cached movie poster URLs
├── requirements.txt        # Python dependencies
├── Procfile                # Configuration for deployment on Heroku
├── setup.sh                # Deployment setup script
├── .gitignore              # Git ignore file to exclude unnecessary files
├── .gitattributes          # Git attributes file for line-ending normalization
├── README.md               # Project documentation
├── LICENSE                 # License file (optional)
└── venv/                   # Virtual environment (not included in the repo)
```


## Dataset
The project uses the TMDB dataset:
* tmdb_5000_movies.csv
* tmdb_5000_credits.csv
These files are preprocessed to create a similarity matrix for recommendations.

## API Usage
The project uses the TMDB API to fetch:
- Movie posters
- Metadata (e.g., genres, cast, crew)

## Technologies Used
- **Python**: Core programming language
- **Streamlit**: For building the interactive UI
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations
- **TMDB API**: Fetching movie metadata and posters
- **Asyncio & Aiohttp**: For asynchronous API calls

## Future Improvements
* Add user ratings and reviews for better recommendations.
* Include collaborative filtering for personalized suggestions.
* Improve error handling and logging.

## Acknowledgments
* The Movie Database (TMDB) for the dataset and API.
* Streamlit for the amazing framework.
