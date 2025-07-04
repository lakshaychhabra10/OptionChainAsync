#%% 
# Database Utilities
from sqlalchemy import create_engine, text
from config import DB_CONFIG
from utils.logger import get_logger
import urllib.parse
logger = get_logger(__name__)

from sqlalchemy import create_engine
from utils.logger import get_logger  # Adjust if needed

def create_mysql_engine():
    """
    Create a SQLAlchemy engine for a MySQL database using configuration in DB_CONFIG.
    """
    try:
        host = DB_CONFIG['host']
        username = DB_CONFIG['username']
        password = urllib.parse.quote_plus(DB_CONFIG['password'])  # encode special chars
        database = DB_CONFIG['database']

        engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}/{database}")
        #logger.info("MySQL engine created successfully for database '%s' at host '%s'.",DB_CONFIG['database'], DB_CONFIG['host'])
        return engine
    
    except Exception as e:
        logger.error("Failed to create MySQL engine.", exc_info=True)
        raise RuntimeError("Could not connect to the database. Please check your configuration and try again.") from None


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

    engine = create_mysql_engine()
    try:
        with engine.connect() as conn:
            df.to_sql(table_name, con=conn, if_exists='append', index=False)
            logger.info(f"Successfully Inserted DataFrame into {table_name}")
    except Exception as e:
        logger.exception("Database insertion error")
    finally:
        engine.dispose()


def get_latest_snapshot_id():
    """
    Retrieves the highest snapshot ID from the optionchain_metadata table.
    Returns:
        int or None: The highest snapshot ID, or None if the table is empty or an error occurs.
    """
    engine = create_mysql_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT MAX(SNAPSHOT_ID) FROM optionchain_metadata"))
            max_id = result.scalar()
            return int(max_id) if max_id is not None else None
    except Exception as e:
        logger.error(f"Failed to retrieve latest snapshot ID: {e}")
        return None
    finally:
        engine.dispose()

