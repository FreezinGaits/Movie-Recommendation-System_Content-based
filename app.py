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

# Custom CSS for consistent alignment, spacing, selectbox, and button styling
st.markdown("""
    <style>
    .header {
        font-size: 36px !important;
        font-weight: 600 !important;
        color: #FFD700 !important;
        text-align: center;
        margin-bottom: 30px !important;
        padding-bottom: 15px;
        border-bottom: 2px solid #f0f2f6;
    }
    .movie-title {
        font-size: 16px;
        font-weight: bold;
        margin-top: 10px;
        text-align: center;
        word-wrap: break-word;
    }
    .movie-poster {
        width: 100%;
        height: auto;
        object-fit: cover;
        padding: 10px;  /* Add padding around images */
        box-sizing: border-box;
    }
    .movie-column {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        min-width: 140px;  /* Ensure columns are wide enough */
    }
    .stColumn > div {
        display: flex;
        justify-content: center;  /* Center content in columns */
    }
    .new {
        font-size: 20px !important;
        font-weight: 500 !important;
        color: #00FFFF !important; /* Cyan for a vibrant, techy contrast */
        text-align: center !important;
        margin-top: 10px !important;
        margin-bottom: 15px !important;
        font-family: 'Arial', sans-serif !important;
        letter-spacing: 0.5px !important;
        text-shadow: 0 0 5px rgba(0, 255, 255, 0.5) !important; /* Subtle glow for cinematic effect */
        transition: color 0.3s ease !important; /* Smooth color transition for hover */
    }
    .new:hover {
        color: #00CED1 !important; /* Slightly darker cyan on hover */
    }
    .stButton>button {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 20px auto !important;
        padding: 12px 24px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        font-family: 'Arial', sans-serif !important;
        color: #FFFFFF !important;
        background: linear-gradient(45deg, #FF1493, #00BFFF) !important;
        border: none !important;
        border-radius: 25px !important;
        box-shadow: 0 4px 15px rgba(0, 191, 255, 0.3) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        cursor: pointer !important;
        width: fit-content !important;
    }
    .stButton>button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 20px rgba(0, 191, 255, 0.7) !important;
    }
    .stButton>button:active {
        transform: scale(0.95) !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header">
        🎬 Movie Magic Recommender
    </div>
""", unsafe_allow_html=True)
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values
# Apply custom CSS to selectbox label using markdown
st.markdown('<div class="new">Let\'s find your movie match!</div>', unsafe_allow_html=True)
selected_movie = st.selectbox(
    "",
    movie_list,
    label_visibility="collapsed"  # Hide default label to use custom markdown
)

# Use Streamlit's native button with custom CSS
if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    
    if not recommended_movie_names:
        st.markdown('<div class="movie-title">No recommendations with images available.</div>', unsafe_allow_html=True)
    else:
        # Use fixed 5 columns with medium gap
        cols = st.columns(5, gap="medium")
        for i, col in enumerate(cols):
            with col:
                if i < len(recommended_movie_names):  # Display only available recommendations
                    try:
                        print(f"Attempting to display image {i+1}: {recommended_movie_posters[i]}")
                        st.image(
                            recommended_movie_posters[i],
                            width=120,  # Smaller width to prevent overlap
                            caption=None,
                            clamp=True,
                            output_format='auto'
                        )
                        st.markdown(
                            f'<div class="movie-title">{recommended_movie_names[i]}</div>',
                            unsafe_allow_html=True
                        )
                    except Exception as e:
                        print(f"Failed to display image {i+1}: {e}")
                        st.markdown(
                            '<div class="movie-title">Image display failed</div>',
                            unsafe_allow_html=True
                        )
                else:
                    st.empty()  # Placeholder for empty columns