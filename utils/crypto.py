import bcrypt


def truncate(password: str) -> bytes:
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(truncate(password), bcrypt.gensalt())
    return hashed.decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(truncate(password), hashed.encode())


# from passlib.context import CryptContext

# pwd_hasher = CryptContext(schemes=["argon2"])


# def hash_password(password: str):
#     return pwd_hasher.hash(password)


# def verify_password(password: str, hashed_password: str):
#     return pwd_hasher.verify(password, hashed_password)
