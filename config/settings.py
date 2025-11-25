from environs import Env

env = Env()
env.read_env()

DATABASE_URL = env.str("DATABASE_URL")
SECRET_KEY = env.str("SECRET_KEY")
ALGORITHM = env.str("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = env.int("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
REFRESH_TOKEN_EXPIRE_DAYS = env.int("REFRESH_TOKEN_EXPIRE_DAYS", default=7)
REQUESTS_PER_MINUTE = env.int("REQUESTS_PER_MINUTE", default=2)
