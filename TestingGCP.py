#%%

# Creating the Connection to GCP
from sqlalchemy import create_engine, text
import urllib.parse
from config import DB_CONFIG  

host = DB_CONFIG['host']
username = DB_CONFIG['username']
password = urllib.parse.quote_plus(DB_CONFIG['password'])  # encode special chars
database = DB_CONFIG['database']

engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}/{database}")

# Test the connection
try:
    with engine.connect() as connection:
        print("✅ Connection successful!")
except Exception as e:
    print("❌ Connection failed:", e)
    exit(1)


