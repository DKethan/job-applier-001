#!/usr/bin/env python3
"""Quick test script to verify MongoDB connection"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database import get_mongodb_client
    from app.config import settings
    
    print(f"Attempting to connect to MongoDB...")
    print(f"URI: {settings.mongodb_uri.split('@')[1] if '@' in settings.mongodb_uri else 'local'}")
    
    client = get_mongodb_client()
    db = client[settings.mongodb_db_name]
    
    # Test a simple operation
    db.test_connection.insert_one({"test": "connection"})
    db.test_connection.delete_one({"test": "connection"})
    
    print("✅ MongoDB connection successful!")
    print(f"✅ Database '{settings.mongodb_db_name}' is accessible")
    
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure apps/api/.env file exists")
    print("2. Check that MONGODB_URI is set correctly")
    print("3. Verify your IP is whitelisted in MongoDB Atlas (Network Access)")
    sys.exit(1)
