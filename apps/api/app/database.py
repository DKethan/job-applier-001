from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi
from typing import Optional
from app.config import settings
from app.utils.app_logger import app_logger

# Global MongoDB client
_mongodb_client: Optional[MongoClient] = None


def get_mongodb_client() -> MongoClient:
    """Get or create MongoDB client"""
    global _mongodb_client
    
    if _mongodb_client is None:
        try:
            app_logger.log_info(f"Connecting to MongoDB: {settings.mongodb_uri.split('@')[1] if '@' in settings.mongodb_uri else 'local'}")
            _mongodb_client = MongoClient(
                settings.mongodb_uri,
                server_api=ServerApi('1'),
                serverSelectionTimeoutMS=5000
            )
            # Test connection
            _mongodb_client.admin.command('ping')
            app_logger.log_info("Successfully connected to MongoDB")
        except Exception as e:
            app_logger.log_error(f"Failed to connect to MongoDB: {e}", exc_info=e)
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")
    
    return _mongodb_client


def get_db():
    """Dependency for getting database"""
    client = get_mongodb_client()
    db_name = getattr(settings, 'mongodb_db_name', 'jobcopilot')
    db = client[db_name]
    try:
        yield db
    finally:
        pass  # Connection is persistent, don't close


def init_db():
    """Initialize database (create indexes)"""
    try:
        client = get_mongodb_client()
        db_name = getattr(settings, 'mongodb_db_name', 'jobcopilot')
        db = client[db_name]
        
        # Create indexes
        db.users.create_index("email", unique=True)
        db.profiles.create_index("user_id")
        db.job_postings.create_index("source_url", unique=True)
        db.file_storage.create_index("user_id")
        db.job_applications.create_index([("user_id", 1), ("job_id", 1)], unique=True)
        
        app_logger.log_info("Database indexes created")
    except Exception as e:
        app_logger.log_error(f"Error initializing database: {e}", exc_info=e)
        raise
