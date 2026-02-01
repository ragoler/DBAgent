import os
import sys
import yaml
from sqlalchemy import text
from backend.core.database import get_engine
from backend.core.schema_parser import SchemaParser

# Add project root to path
sys.path.append(os.getcwd())

def init_db():
    print("Initializing Database from schema.yaml...")
    
    # 1. Load Schema
    with open("data/schema.yaml", "r") as f:
        schema_data = yaml.safe_load(f)
    
    engine = get_engine()
    
    with engine.connect() as conn:
        # 2. Iterate and Create Tables
        for table in schema_data.get('tables', []):
            table_name = table['name']
            print(f"Creating table: {table_name}")
            
            # Simple DDL generation (SQLite compatible)
            columns_ddl = []
            for col in table['columns']:
                col_def = f"{col['name']} {col['type']}"
                if col.get('primary_key'):
                    col_def += " PRIMARY KEY"
                columns_ddl.append(col_def)
            
            drop_stmt = f"DROP TABLE IF EXISTS {table_name}"
            create_stmt = f"CREATE TABLE {table_name} ({', '.join(columns_ddl)})"
            
            conn.execute(text(drop_stmt))
            conn.execute(text(create_stmt))
            
            # 3. Seed Mock Data
            if table_name == "flights":
                print("Seeding flights...")
                # flight 1: NYC to LON
                conn.execute(text(
                    "INSERT INTO flights (id, pilot_id, plane_id, origin, destination, departure_time) "
                    "VALUES (1, 101, 1, 'JFK', 'LHR', '2023-10-25 08:00:00')"
                ))
                # flight 2: LON to PAR
                conn.execute(text(
                    "INSERT INTO flights (id, pilot_id, plane_id, origin, destination, departure_time) "
                    "VALUES (2, 102, 1, 'LHR', 'CDG', '2023-10-26 14:30:00')"
                ))
            
            elif table_name == "pilots":
                print("Seeding pilots...")
                conn.execute(text(
                    "INSERT INTO pilots (id, name, license_type) VALUES (101, 'Maverick', 'Military')"
                ))
                conn.execute(text(
                    "INSERT INTO pilots (id, name, license_type) VALUES (102, 'Amelia', 'Commercial')"
                ))
                
            elif table_name == "planes":
                print("Seeding planes...")
                conn.execute(text(
                    "INSERT INTO planes (id, model, capacity) VALUES (1, 'Boeing 737', 150)"
                ))

        conn.commit()
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
