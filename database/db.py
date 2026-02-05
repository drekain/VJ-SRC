import motor.motor_asyncio
from config import DB_URI, DB_NAME


class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name):
        return {
            "id": int(id),
            "name": name,
            "session": None,
            "api_id": None,
            "api_hash": None
        }

    async def add_user(self, id, name):
        if not await self.is_user_exist(id):
            await self.col.insert_one(self.new_user(id, name))

    async def is_user_exist(self, id):
        user = await self.col.find_one({"id": int(id)})
        return bool(user)

    async def total_users_count(self):
        return await self.col.count_documents({})

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({"id": int(user_id)})

    async def set_session(self, id, session):
        await self.col.update_one(
            {"id": int(id)},
            {"$set": {"session": session}},
            upsert=True
        )

    async def get_session(self, id):
        user = await self.col.find_one({"id": int(id)})
        if not user:
            return None
        return user.get("session")

    async def set_api_id(self, id, api_id):
        await self.col.update_one(
            {"id": int(id)},
            {"$set": {"api_id": api_id}},
            upsert=True
        )

    async def get_api_id(self, id):
        user = await self.col.find_one({"id": int(id)})
        if not user:
            return None
        return user.get("api_id")

    async def set_api_hash(self, id, api_hash):
        await self.col.update_one(
            {"id": int(id)},
            {"$set": {"api_hash": api_hash}},
            upsert=True
        )

    async def get_api_hash(self, id):
        user = await self.col.find_one({"id": int(id)})
        if not user:
            return None
        return user.get("api_hash")


db = Database(DB_URI, DB_NAME)
