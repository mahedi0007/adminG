
import os 
from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# For mysql-connector-python (recommended for your current setup)
# DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://root:toor@localhost:3306/groceryappadmin")
# DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqldb://root:toor@localhost:3306/groceryapp")

# OR for mysqlclient 
# DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqldb://root:toor@localhost:3306/groceryappadmin")

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:toor@localhost:3306/groceryappadmin")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Test connection before using it
    pool_size=5,
    max_overflow=10
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
