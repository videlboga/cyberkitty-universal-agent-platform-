import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from loguru import logger

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017/universal_agent_platform")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "universal_agent_platform")

logger.info(f"Connecting to MongoDB: {MONGO_URI}, Database: {MONGODB_DATABASE_NAME}")
logger.critical(f"[DATABASE_INIT_CRITICAL] MONGO_URI used for AsyncIOMotorClient: '{MONGO_URI}'")

client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)
db: AsyncIOMotorDatabase = client[MONGODB_DATABASE_NAME]

async def get_database() -> AsyncIOMotorDatabase:
    return db

# Optional: Functions to connect and close the client if needed explicitly
# async def connect_to_mongo():
#     logger.info("Connecting to MongoDB...")
#     # client is already defined globally
#     # You might want to do a server_info() call to ensure connection
#     try:
#         await client.admin.command('ping')
#         logger.info("Successfully connected to MongoDB.")
#     except Exception as e:
#         logger.error(f"Failed to connect to MongoDB: {e}")
#         raise

# async def close_mongo_connection():
#     logger.info("Closing MongoDB connection...")
#     client.close()
#     logger.info("MongoDB connection closed.")

logger.info("MongoDB client initialized.") 