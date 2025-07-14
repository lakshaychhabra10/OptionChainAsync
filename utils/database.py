#%% 
# Database Utilities
from sqlalchemy import create_engine, text
from config import DB_CONFIG
from utils.logger import get_logger
import urllib.parse
logger = get_logger(__name__)

from sqlalchemy import create_engine
from utils.logger import get_logger  # Adjust if needed

# Create a global engine once
try:
    host = DB_CONFIG['host']
    username = DB_CONFIG['username']
    password = urllib.parse.quote_plus(DB_CONFIG['password'])
    database = DB_CONFIG['database']
    engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}/{database}", pool_pre_ping=True)
except Exception as e:
    logger.error("Failed to create MySQL engine.", exc_info=True)
    raise RuntimeError("Could not connect to the database.") from e


def create_required_tables():
    """
    Create required tables if they don't already exist.
    This should be run once during startup.
    """

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS optionchain (
                TICKER TEXT,
                SNAPSHOT_ID BIGINT,
                EXPIRY DATE,
                c_OI DOUBLE,
                c_CHNG_IN_OI DOUBLE,
                c_VOLUME DOUBLE,
                c_IV DOUBLE,
                c_LTP DOUBLE,
                c_CHNG DOUBLE,
                c_BID_QTY DOUBLE,
                c_BID DOUBLE,
                c_ASK DOUBLE,
                c_ASK_QTY DOUBLE,
                STRIKE DOUBLE,
                p_BID_QTY DOUBLE,
                p_BID DOUBLE,
                p_ASK DOUBLE,
                p_ASK_QTY DOUBLE,
                p_CHNG DOUBLE,
                p_LTP DOUBLE,
                p_IV DOUBLE,
                p_VOLUME DOUBLE,
                p_CHNG_IN_OI DOUBLE,
                p_OI DOUBLE
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS optionchain_snapshots (
                SNAPSHOT_ID BIGINT,
                TICKER TEXT,
                DOWNLOAD_DATE TEXT,
                DOWNLOAD_TIME TEXT,
                UNDERLYING_VALUE DOUBLE
            );
        """))



def insert_in_database(df, table_name):
    """
    Insert a pandas DataFrame into a MySQL table.

    Connects to the database and appends the DataFrame to the specified table.
    Logs success or any errors during insertion.

    Args:
        df (pandas.DataFrame): Data to insert.
        table_name (str): Target table name.

    Raises:
        RuntimeError: If database connection fails.
        Exception: If insertion fails.

    Example:
        >>> insert_in_database(my_dataframe, "users")
    """


    with engine.connect() as conn:
        df.to_sql(table_name, con=conn, if_exists='append', index=False, method='multi')


def get_latest_snapshot_id():
    """
    Retrieves the highest snapshot ID from the optionchain_snapshots table.
    Returns:
        int or None: The highest snapshot ID, or None if the table is empty or an error occurs.
    """


    with engine.connect() as conn:
        result = conn.execute(text("SELECT MAX(SNAPSHOT_ID) FROM optionchain_snapshots"))
        max_id = result.scalar()
        return int(max_id) if max_id is not None else None



def get_previous_datetime(ticker):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT download_date, download_time FROM optionchain_snapshots WHERE ticker = :ticker ORDER BY snapshot_id DESC LIMIT 1")
            ,
            {"ticker": ticker}  # <- use dictionary for parameters
        ).fetchone()
        return result if result else (None, None)
