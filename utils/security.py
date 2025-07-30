import os
import secrets
import hashlib
import base64
import jwt

from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from jwt import PyJWTError
from functools import wraps

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
security = HTTPBearer()

def create_jwt_token(
          name:str
        , email: str
        , active: bool
        , admin: bool
        , id: str
):
    expiration = datetime.utcnow() + timedelta(hours=1) 
    token = jwt.encode(
        {
            "id": id,
            "name": name,
            "email": email,
            "active": active,
            "admin": admin,
            "exp": expiration,
            "iat": datetime.utcnow()
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    return token


def validateuser(func):
    @wraps(func)
    async def wrapper( *args, **kwargs ):
        request = kwargs.get('request')
        if not request:
            raise HTTPException( status_code=400, detail="Request object not found"  )

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException( status_code=400, detail="Authorization header missing"  )

        schema, token = authorization.split()
        if schema.lower() != "bearer":
            raise HTTPException( status_code=400, detail="Invalid auth schema"  )

        try:
            payload = jwt.decode( token , SECRET_KEY, algorithms=["HS256"] )

            email = payload.get("email")
            firstname = payload.get("firstname")
            lastname = payload.get("lastname")
            active = payload.get("active")
            exp = payload.get("exp")
            id = payload.get("id")

            if email is None:
                raise HTTPException( status_code=401 , detail="Token Invalid" )

            if datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException( status_code=401 , detail="Expired token" )

            if not active:
                raise HTTPException( status_code=401 , detail="Inactive user" )

            request.state.email = email
            request.state.firstname = firstname
            request.state.lastname = lastname
            request.state.id = id


        except PyJWTError:
            raise HTTPException( status_code=401, detail="Invalid token or expired token"  )

        return await func( *args, **kwargs )
    return wrapper


def validateadmin(func):
    @wraps(func)
    async def wrapper( *args, **kwargs ):
        request = kwargs.get('request')
        if not request:
            raise HTTPException( status_code=400, detail="Request object not found"  )

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException( status_code=400, detail="Authorization header missing"  )

        schema, token = authorization.split()
        if schema.lower() != "bearer":
            raise HTTPException( status_code=400, detail="Invalid auth schema"  )

        try:
            payload = jwt.decode( token , SECRET_KEY, algorithms=["HS256"] )

            email = payload.get("email")
            firstname = payload.get("firstname")
            lastname = payload.get("lastname")
            active = payload.get("active")
            admin = payload.get("admin")
            exp = payload.get("exp")
            id = payload.get("id")

            if email is None:
                raise HTTPException( status_code=401 , detail="Token Invalid" )

            if datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException( status_code=401 , detail="Expired token" )

            if not active or not admin:
                raise HTTPException( status_code=401 , detail="Inactive user or not admin" )

            request.state.email = email
            request.state.firstname = firstname
            request.state.lastname = lastname
            request.state.admin = admin
            request.state.id = id


        except PyJWTError:
            raise HTTPException( status_code=401, detail="Invalid token or expired token"  )

        return await func( *args, **kwargs )
    return wrapper
