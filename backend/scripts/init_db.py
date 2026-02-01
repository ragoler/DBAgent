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
            if table_name == "pilots":
                print("Seeding pilots...")
                pilots = [
                    (1, 'Maverick', 'Military'),
                    (2, 'Amelia', 'Commercial'),
                    (3, 'Charles', 'Private'),
                    (4, 'Bessie', 'Commercial'),
                    (5, 'Howard', 'Private')
                ]
                for p_id, name, l_type in pilots:
                    conn.execute(text(
                        "INSERT INTO pilots (id, name, license_type) VALUES (:id, :name, :license_type)"
                    ), {"id": p_id, "name": name, "license_type": l_type})
            
            elif table_name == "planes":
                print("Seeding planes...")
                planes = [
                    (1, 'Boeing 737', 150),
                    (2, 'Airbus A320', 180),
                    (3, 'Cessna 172', 4),
                    (4, 'Gulfstream G650', 19),
                    (5, 'Boeing 787', 250)
                ]
                for p_id, model, cap in planes:
                    conn.execute(text(
                        "INSERT INTO planes (id, model, capacity) VALUES (:id, :model, :capacity)"
                    ), {"id": p_id, "model": model, "capacity": cap})

            elif table_name == "flights":
                print("Seeding flights...")
                import random
                from datetime import datetime, timedelta
                
                airports = ['JFK', 'LHR', 'CDG', 'SFO', 'LAX']
                p_ids = [1, 2, 3, 4, 5]
                pl_ids = [1, 2, 3, 4, 5]
                
                # Flight 1: JFK to LHR
                conn.execute(text(
                    "INSERT INTO flights (id, pilot_id, plane_id, origin, destination, departure_time) "
                    "VALUES (1, 1, 1, 'JFK', 'LHR', '2023-11-01 10:00:00')"
                ))
                # Flight 2: LHR to CDG
                conn.execute(text(
                    "INSERT INTO flights (id, pilot_id, plane_id, origin, destination, departure_time) "
                    "VALUES (2, 2, 1, 'LHR', 'CDG', '2023-11-01 15:30:00')"
                ))
                
                # Generate 18 more flights
                for i in range(3, 21):
                    origin = random.choice(airports)
                    dest = random.choice([a for a in airports if a != origin])
                    pilot = random.choice(p_ids)
                    plane = random.choice(pl_ids)
                    time = (datetime(2023, 11, 1) + timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))).strftime('%Y-%m-%d %H:%M:%S')
                    conn.execute(text(
                        "INSERT INTO flights (id, pilot_id, plane_id, origin, destination, departure_time) "
                        "VALUES (:id, :p_id, :pl_id, :origin, :dest, :time)"
                    ), {"id": i, "p_id": pilot, "pl_id": plane, "origin": origin, "dest": dest, "time": time})

        conn.commit()
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
