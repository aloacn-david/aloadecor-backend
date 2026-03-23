"""
MongoDB 连接模块
使用 Motor 异步驱动
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB 连接配置
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/aloadecor")
DB_NAME = os.getenv("MONGODB_DB_NAME", "aloadecor")

# 全局客户端
client: AsyncIOMotorClient = None
db = None

async def connect_to_mongo():
    """连接到MongoDB"""
    global client, db
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    print("✅ Connected to MongoDB")

async def close_mongo_connection():
    """关闭MongoDB连接"""
    global client
    if client:
        client.close()
        print("❌ Closed MongoDB connection")

# 获取数据库实例
def get_db():
    return db

# 获取集合
def get_collection(collection_name: str):
    return db[collection_name] if db else None
