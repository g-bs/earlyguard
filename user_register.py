from fastapi import APIRouter
from pydantic import BaseModel
import json
import os

USERS_FILE = "subscribers.json"
router = APIRouter()

class User(BaseModel):
    phone_number: str
    location: str

def load_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_json(data, file):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

@router.post("/register_user")
def register_user(user: User):
    users = load_json(USERS_FILE)
    if any(u["phone_number"] == user.phone_number for u in users):
        return {"msg": "Phone number already registered."}
    users.append(user.dict())
    save_json(users, USERS_FILE)
    return {"msg": "✅ Registered for SMS alerts!"}
