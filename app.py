import pickle
import streamlit as st
import aiohttp
import asyncio
import nest_asyncio
import json
import os

# Apply nest_asyncio for Streamlit
nest_asyncio.apply()

CACHE_FILE = "poster_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

async def fetch_poster_async(movie_id, session, semaphore):
    cache = load_cache()
    if str(movie_id) in cache:
        print(f"Using cached poster for movie_id {movie_id}: {cache[str(movie_id)]}")
        return cache[str(movie_id)]
    
    async with semaphore:
        try:
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=5d7471b6184a5674e22db14fa26b8bd6&language=en-US"
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                print(f"API response for movie_id {movie_id}: {data}")
                poster_path = data.get('poster_path', '')
                if poster_path:
                    full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
                    print(f"Poster URL: {full_path}")
                    cache[str(movie_id)] = full_path
                    save_cache(cache)
                    return full_path
                else:
                    print(f"No poster path found for movie_id {movie_id}")
                    return None
        except Exception as e:
            print(f"Error fetching poster for movie_id {movie_id}: {e}")
            return None
        finally:
            await asyncio.sleep(0.1)

async def fetch_all_posters(movie_ids):
    semaphore = asyncio.Semaphore(2)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_poster_async(movie_id, session, semaphore) for movie_id in movie_ids]
        return await asyncio.gather(*tasks)

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    movie_ids = []
    
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        movie_ids.append(movie_id)
        recommended_movie_names.append(movies.iloc[i[0]].title)
    
    posters = asyncio.run(fetch_all_posters(movie_ids))
    
    valid_names = []
    valid_posters = []
    for name, poster, movie_id in zip(recommended_movie_names, posters, movie_ids):
        if poster and poster.startswith('https://image.tmdb.org/'):
            valid_names.append(name)
            valid_posters.append(poster)
        else:
            print(f"Excluding movie '{name}' (movie_id {movie_id}) due to invalid poster: {poster}")
    
    return valid_names, valid_posters

# Custom CSS for consistent alignment
st.markdown("""
    <style>
    .movie-title {
        font-size: 16px;
        font-weight: bold;
        margin-top: 10px;  /* Space above title */
        text-align: center;
        word-wrap: break-word;  /* Allow long titles to wrap */
    }
    .movie-poster {
        width: 100%;
        height: auto;
        object-fit: cover;
    }
    .movie-column {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
    }
    </style>
""", unsafe_allow_html=True)

st.header('Movie Recommender System')
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    
    if not recommended_movie_names:
        st.markdown('<div class="movie-title">No recommendations with images available.</div>', unsafe_allow_html=True)
    else:
        cols = st.columns(len(recommended_movie_names))
        for i, (name, poster) in enumerate(zip(recommended_movie_names, recommended_movie_posters)):
            with cols[i]:
                try:
                    print(f"Attempting to display image {i+1}: {poster}")
                    st.image(
                        poster,
                        use_container_width=True,
                        caption=None,
                        clamp=True,
                        output_format='auto'
                    )
                except Exception as e:
                    print(f"Failed to display image {i+1}: {e}")
                    st.markdown(
                        '<div class="movie-title">Image display failed</div>',
                        unsafe_allow_html=True
                    )
                st.markdown(
                    f'<div class="movie-title">{name}</div>',
                    unsafe_allow_html=True
                )