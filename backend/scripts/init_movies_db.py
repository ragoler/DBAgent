import os
import sys
import httpx
import json
import yaml
import sqlite3
import random
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

VEGA_MOVIES_URL = "https://raw.githubusercontent.com/vega/vega-datasets/master/data/movies.json"
WIKI_MOVIES_URL = "https://raw.githubusercontent.com/prust/wikipedia-movie-data/master/movies.json"

DATA_DIR = os.path.join("data")
DB_PATH = os.path.join(DATA_DIR, "movies.db")
SCHEMA_PATH = os.path.join(DATA_DIR, "movies_schema.yaml")

def download_data(url, name):
    print(f"Downloading {name} from {url}...")
    try:
        response = httpx.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"Downloaded {len(data)} records for {name}.")
        return data
    except Exception as e:
        print(f"Error downloading {name}: {e}")
        return None

def normalize_title(title):
    if not title: return ""
    return str(title).lower().strip()

def extract_year(date_str):
    # Vega date format: "Dec 15 1993" or sometimes just year?
    # Or ISO? Let's check. Vega movies.json usually has "Mon DD YYYY"
    if not date_str: return None
    try:
        # Try parse "MMM DD YYYY"
        dt = datetime.strptime(date_str, "%b %d %Y")
        return dt.year
    except ValueError:
        pass
    
    # Try just 4 digits
    if len(date_str) == 4 and date_str.isdigit():
        return int(date_str)
        
    return None

def create_database(vega_movies, wiki_movies):
    print(f"Creating SQLite database at {DB_PATH}...")
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Create Tables
    cursor.execute("""
        CREATE TABLE directors (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE actors (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    """)
    
    # Prepare Vega movies for insertion
    if not vega_movies:
        print("No Vega movie data found.")
        return {}, {}

    first_record = vega_movies[0]
    sanitized_keys = {}
    create_cols = ["id INTEGER PRIMARY KEY"]
    skip_keys = ["Director"] 
    
    # Infer types from first non-null value for each column
    column_types = {}
    
    # Analyze all records to find types
    for key in first_record.keys():
        if key in skip_keys: continue
        sanitized = key.lower().replace(" ", "_").replace("-", "_")
        sanitized_keys[key] = sanitized
        
        # Check first 100 records for a non-null value to infer type
        col_type = "TEXT" # Default
        for m in vega_movies[:100]:
            val = m.get(key)
            if val is not None:
                if isinstance(val, int):
                    col_type = "INTEGER"
                elif isinstance(val, float):
                    col_type = "INTEGER" # Treat as number for simplicity in schema
                else:
                    col_type = "TEXT"
                break
        
        create_cols.append(f"{sanitized} {col_type}")
        column_types[sanitized] = "VARCHAR" if col_type == "TEXT" else "INTEGER"

    create_cols.append("director_id INTEGER")
    create_cols.append("FOREIGN KEY(director_id) REFERENCES directors(id)")
    
    cursor.execute(f"CREATE TABLE movies ({', '.join(create_cols)})")
    
    cursor.execute("""
        CREATE TABLE movie_actors (
            movie_id INTEGER,
            actor_id INTEGER,
            PRIMARY KEY (movie_id, actor_id),
            FOREIGN KEY(movie_id) REFERENCES movies(id),
            FOREIGN KEY(actor_id) REFERENCES actors(id)
        )
    """)
    
    # 2. Build Lookup for Wiki Movies (Title + Year -> Cast)
    print("Building Wikipedia movie lookup...")
    wiki_map = {}
    for wm in wiki_movies:
        t = normalize_title(wm.get("title"))
        y = wm.get("year")
        cast = wm.get("cast", [])
        if t:
            if (t, y) not in wiki_map:
                wiki_map[(t, y)] = cast
            # Also store just by title as fallback
            if t not in wiki_map:
                wiki_map[t] = cast

    # 3. Insert Data
    print("Inserting data...")
    
    # Maps for normalized DB
    director_map = {} # Name -> ID
    actor_map = {} # Name -> ID
    
    dir_id_counter = 1
    act_id_counter = 1
    movie_id_counter = 1
    
    movie_insert_sql = f"INSERT INTO movies (id, {', '.join(sanitized_keys.values())}, director_id) VALUES (?, {', '.join(['?']*len(sanitized_keys))}, ?)"
    
    for movie in vega_movies:
        # Handle Director
        d_name = movie.get("Director")
        d_id = None
        if d_name:
            if d_name not in director_map:
                cursor.execute("INSERT INTO directors (id, name) VALUES (?, ?)", (dir_id_counter, d_name))
                director_map[d_name] = dir_id_counter
                dir_id_counter += 1
            d_id = director_map[d_name]
            
        # Insert Movie
        values = [movie_id_counter]
        for original_key in sanitized_keys.keys():
            values.append(movie.get(original_key))
        values.append(d_id)
        
        cursor.execute(movie_insert_sql, values)
        
        # Handle Actors via Wiki Match
        title = normalize_title(movie.get("Title"))
        year = extract_year(movie.get("Release_Date"))
        
        cast = []
        # Try match with year
        if (title, year) in wiki_map:
            cast = wiki_map[(title, year)]
        elif title in wiki_map:
            cast = wiki_map[title]
            
        # Insert Actors and Links
        for actor_name in set(cast):
            if not actor_name: continue
            
            if actor_name not in actor_map:
                cursor.execute("INSERT INTO actors (id, name) VALUES (?, ?)", (act_id_counter, actor_name))
                actor_map[actor_name] = act_id_counter
                act_id_counter += 1
            
            a_id = actor_map[actor_name]
            cursor.execute("INSERT INTO movie_actors (movie_id, actor_id) VALUES (?, ?)", (movie_id_counter, a_id))
            
        movie_id_counter += 1
        
    conn.commit()
    conn.close()
    print(f"Database populated. Directors: {len(director_map)}, Actors: {len(actor_map)}, Movies: {movie_id_counter-1}")
    return sanitized_keys, column_types

def generate_schema_yaml(sanitized_keys, column_types):
    print(f"Generating schema YAML at {SCHEMA_PATH}...")
    
    tables = [
        {
            "name": "directors",
            "description": "Information about movie directors.",
            "columns": [
                {"name": "id", "type": "INTEGER", "primary_key": True, "description": "Unique identifier."},
                {"name": "name", "type": "VARCHAR", "description": "Full name of the director."}
            ]
        },
        {
            "name": "actors",
            "description": "Information about movie actors.",
            "columns": [
                {"name": "id", "type": "INTEGER", "primary_key": True, "description": "Unique identifier."},
                {"name": "name", "type": "VARCHAR", "description": "Full name of the actor."}
            ]
        }
    ]
    
    movie_cols = [
        {"name": "id", "type": "INTEGER", "primary_key": True, "description": "Unique movie identifier."}
    ]
    for key, sanitized in sanitized_keys.items():
        ctype = column_types.get(sanitized, "VARCHAR")
        movie_cols.append({
            "name": sanitized,
            "type": ctype,
            "description": f"Movie attribute: {key}"
        })
    movie_cols.append({
        "name": "director_id",
        "type": "INTEGER",
        "foreign_key": "directors.id",
        "description": "ID of the director."
    })
    
    tables.append({
        "name": "movies",
        "description": "Contains a dataset of movies with financial and rating information.",
        "columns": movie_cols
    })
    
    tables.append({
        "name": "movie_actors",
        "description": "Join table linking movies to actors.",
        "columns": [
            {"name": "movie_id", "type": "INTEGER", "foreign_key": "movies.id", "description": "ID of the movie."},
            {"name": "actor_id", "type": "INTEGER", "foreign_key": "actors.id", "description": "ID of the actor."}
        ]
    })
        
    schema_data = {"tables": tables}
    
    with open(SCHEMA_PATH, "w") as f:
        yaml.dump(schema_data, f, sort_keys=False)
    print("Schema YAML generated.")

if __name__ == "__main__":
    vega_data = download_data(VEGA_MOVIES_URL, "Vega Movies")
    wiki_data = download_data(WIKI_MOVIES_URL, "Wikipedia Movies")
    
    if vega_data and wiki_data:
        keys, types = create_database(vega_data, wiki_data)
        generate_schema_yaml(keys, types)
    else:
        print("Failed to download necessary data.")
