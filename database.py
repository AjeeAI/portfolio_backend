from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

load_dotenv()
db_url = f"mysql+pymysql://{os.getenv('dbuser')}:{os.getenv('dbpassword')}@{os.getenv('dbhost')}:{os.getenv('dbport')}/{os.getenv('dbname')}"

engine = create_engine(db_url)

session = sessionmaker(bind=engine)

db = session()

create_message_table_query = text(
    """
    CREATE TABLE IF NOT EXISTS messages_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        subject VARCHAR(255) NOT NULL,
        message LONGTEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
)

db.execute(create_message_table_query)
print("Table created successfully.")