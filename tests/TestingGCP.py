#%%

#Lets make a random dataframe
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

# Create a random DataFrame
np.random.seed(42)  # For reproducibility
data = {
    'Maths': np.random.randint(1, 100, size=10),
    'Physics': np.random.rand(10),
    'Category': np.random.choice(['X', 'Y', 'Z'], size=10),
    'Date': pd.date_range('2023-01-01', periods=10, freq='D')
}

df = pd.DataFrame(data)


# Creating the Connection to GCP
from sqlalchemy import create_engine, text
import urllib.parse

host = os.getenv('DB_HOST')
user = os.getenv('DB_USER')
password = urllib.parse.quote_plus(os.getenv('DB_PASSWORD'))  # encode special chars
database = os.getenv('DB_NAME')

engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

# Test the connection
try:
    with engine.connect() as connection:
        print("✅ Connection successful!")
except Exception as e:
    print("❌ Connection failed:", e)
    exit(1)

# Writing the DataFrame to a MySQL table
table_name = 'randomtable'
df.to_sql(table_name, con=engine, if_exists='replace', index=False)


# Reading the DataFrame back from the MySQL table
with engine.connect() as connection:
    query = text(f"SELECT * FROM {table_name}")
    df_read = pd.read_sql(query, connection)