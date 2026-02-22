import os
import sys
import httpx
import json
import yaml
import sqlite3
import random
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.getcwd())

MOVIES_URL = "https://raw.githubusercontent.com/vega/vega-datasets/master/data/movies.json"
DATA_DIR = os.path.join("data")
DB_PATH = os.path.join(DATA_DIR, "movies.db")
SCHEMA_PATH = os.path.join(DATA_DIR, "movies_schema.yaml")
CONFIG_PATH = os.path.join(DATA_DIR, "databases.yaml")

# Mock data for actors since source JSON doesn't have them
FAMOUS_ACTORS = [
    "Tom Hanks", "Meryl Streep", "Leonardo DiCaprio", "Denzel Washington", 
    "Robert De Niro", "Al Pacino", "Jack Nicholson", "Marlon Brando", 
    "Johnny Depp", "Brad Pitt", "Angelina Jolie", "Scarlett Johansson", 
    "Jennifer Lawrence", "Emma Stone", "Viola Davis", "Cate Blanchett",
    "Kate Winslet", "Julia Roberts", "Sandra Bullock", "Nicole Kidman",
    "Harrison Ford", "Samuel L. Jackson", "Morgan Freeman", "Tom Cruise",
    "Will Smith", "Matt Damon", "Ben Affleck", "George Clooney",
    "Robert Downey Jr.", "Chris Evans", "Chris Hemsworth", "Mark Ruffalo"
]

def download_movies():
    print(f"Downloading movies dataset from {MOVIES_URL}...")
    try:
        response = httpx.get(MOVIES_URL)
        response.raise_for_status()
        movies = response.json()
        print(f"Downloaded {len(movies)} movie records.")
        return movies
    except Exception as e:
        print(f"Error downloading movies: {e}")
        sys.exit(1)

def create_database(movies):
    print(f"Creating SQLite database at {DB_PATH}...")
    
    # Remove existing DB
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
    
    # Analyze columns for movies table
    if not movies:
        print("No movie data found.")
        return

    first_record = movies[0]
    sanitized_keys = {}
    create_cols = ["id INTEGER PRIMARY KEY"] # Add explicit ID
    
    # Director will be FK
    skip_keys = ["Director"] 
    
    for key in first_record.keys():
        if key in skip_keys:
            continue
            
        sanitized = key.lower().replace(" ", "_").replace("-", "_")
        sanitized_keys[key] = sanitized
        
        # Simple type inference
        val = first_record[key]
        col_type = "TEXT"
        if isinstance(val, int):
            col_type = "INTEGER"
        elif isinstance(val, float):
            col_type = "REAL"
            
        create_cols.append(f"{sanitized} {col_type}")
    
    create_cols.append("director_id INTEGER")
    create_cols.append("FOREIGN KEY(director_id) REFERENCES directors(id)")
    
    create_stmt = f"CREATE TABLE movies ({', '.join(create_cols)})"
    cursor.execute(create_stmt)
    
    cursor.execute("""
        CREATE TABLE movie_actors (
            movie_id INTEGER,
            actor_id INTEGER,
            PRIMARY KEY (movie_id, actor_id),
            FOREIGN KEY(movie_id) REFERENCES movies(id),
            FOREIGN KEY(actor_id) REFERENCES actors(id)
        )
    """)
    
    # 2. Insert Data
    print("Inserting data...")
    
    # Pre-populate Directors to get IDs
    directors = set()
    for m in movies:
        d = m.get("Director")
        if d:
            directors.add(d)
            
    director_map = {} # Name -> ID
    for idx, d_name in enumerate(sorted(list(directors)), 1):
        cursor.execute("INSERT INTO directors (id, name) VALUES (?, ?)", (idx, d_name))
        director_map[d_name] = idx
        
    # Pre-populate Actors
    actor_map = {} # Name -> ID
    for idx, a_name in enumerate(FAMOUS_ACTORS, 1):
        cursor.execute("INSERT INTO actors (id, name) VALUES (?, ?)", (idx, a_name))
        actor_map[a_name] = idx
        
    # Insert Movies
    movie_insert_sql = f"INSERT INTO movies (id, {', '.join(sanitized_keys.values())}, director_id) VALUES (?, {', '.join(['?']*len(sanitized_keys))}, ?)"
    
    movie_id = 1
    for movie in movies:
        values = [movie_id]
        for original_key in sanitized_keys.keys():
            val = movie.get(original_key)
            values.append(val)
            
        # Director FK
        d_name = movie.get("Director")
        d_id = director_map.get(d_name) # None if missing
        values.append(d_id)
        
        cursor.execute(movie_insert_sql, values)
        
        # Link Random Actors (0-3 per movie)
        num_actors = random.randint(0, 3)
        if num_actors > 0:
            selected_actors = random.sample(list(actor_map.values()), num_actors)
            for a_id in selected_actors:
                cursor.execute("INSERT INTO movie_actors (movie_id, actor_id) VALUES (?, ?)", (movie_id, a_id))
        
        movie_id += 1
        
    conn.commit()
    conn.close()
    print("Database created with Directors and Actors.")
    return sanitized_keys

def generate_schema_yaml(sanitized_keys):
    print(f"Generating schema YAML at {SCHEMA_PATH}...")
    
    # Directors Table
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
    
    # Movies Table
    movie_cols = [
        {"name": "id", "type": "INTEGER", "primary_key": True, "description": "Unique movie identifier."}
    ]
    for key, sanitized in sanitized_keys.items():
        movie_cols.append({
            "name": sanitized,
            "type": "VARCHAR" if "date" in sanitized or "text" in sanitized else "INTEGER",
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
    
    # Join Table
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
    movies_data = download_movies()
    if movies_data:
        keys = create_database(movies_data)
        generate_schema_yaml(keys)
