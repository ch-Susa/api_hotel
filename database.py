from decouple import config
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = config("MONGODB_URL", default = "mongodb://localhost:27017")
DATABASE_NAME = config("DATABASE_NAME", default = "hotel_db")

client = AsyncIOMotorClient(MONGODB_URL)

database = client[DATABASE_NAME]

reservas_collection = database["reservas_hotel"]

async def verificar_conexion():
    await client.admin.command("ping")
    return True