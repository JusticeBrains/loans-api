from passlib.context import CryptContext

pwd_hasher = CryptContext(schemes=["argon2"])


def hash_password(password: str):
    return pwd_hasher.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_hasher.verify(password, hashed_password)
