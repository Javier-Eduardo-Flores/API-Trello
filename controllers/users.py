import os
import logging
import firebase_admin
import requests
import base64
import json
from fastapi import HTTPException
from firebase_admin import credentials, auth as firebase_auth
from dotenv import load_dotenv
from models.users import User
from models.login import Login

from utils.security import create_jwt_token
from utils.mongodb import get_collection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
cred = credentials.Certificate("./secrets/trello_secrets.json")
firebase_admin.initialize_app(cred)

"""
Function to create a new user in Firebase and MongoDB (Funcion tomada del repositorio del maestro)
"""

def initialize_firebase():
    if firebase_admin._apps:
        return

    try:
        firebase_creds_base64 = os.getenv("FIREBASE_CREDENTIALS_BASE64")

        if firebase_creds_base64:
            firebase_creds_json = base64.b64decode(firebase_creds_base64).decode('utf-8')
            firebase_creds = json.loads(firebase_creds_json)
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized with environment variable credentials")
        else:
            
            cred = credentials.Certificate("secrets/trello-secrets.json")
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized with JSON file")

    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise HTTPException(status_code=500, detail=f"Firebase configuration error: {str(e)}")


initialize_firebase()

async def create_user(user: User) -> User:

      user_record = {}

      try:
          user_record = firebase_auth.create_user(
              email=user.email,
              password=user.password,
          )
      except Exception as e:
          logger.warning(e)
          raise HTTPException(status_code=400, detail=f"Error creating user in Firebase: {e}")

      try:
         col = get_collection("users")

         new_user = User(
            name=user.name,
            email=user.email,
            password=user.password,
        )

         user_dict = new_user.model_dump(exclude= {"id","password"})
         inserted_user =  col.insert_one(user_dict)
         new_user.id = str(inserted_user.inserted_id)
         new_user.password = "********" 
         return new_user

      except Exception as e:
         firebase_auth.delete_user(user_record.uid)
         logger.error(f"Error creating user: {e}")
         raise HTTPException(status_code=500, detail=f"Error creating user in database: {e}")



async def login(user: Login) -> dict:
   api_key = os.getenv("FIREBASE_API_KEY")
   url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

   payload = {
       "email": user.email,
       "password": user.password,
       "returnSecureToken": True
   }

   response = requests.post(url, json=payload)
   response_data = response.json()

   if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response_data.get("error", {}).get("message", "Login failed")
        )

   coll = get_collection("users")
   user_data = coll.find_one({"email": user.email})

   if not user_data:
       raise HTTPException(status_code=404, detail="User not found")

   return {
    "message": "Login successful",
    "id_token": create_jwt_token(
        user_data["name"],
        user_data["email"],
        user_data["active"],
        user_data["admin"],
        str(user_data["_id"])
    ),
    }

