from environs import Env

env = Env()
env.read_env()

TOKEN = env.str("TOKEN")
MEDIA_ROOT = env.str("MEDIA_ROOT")

DB_NAME = env.str("DB_NAME")
DB_USER = env.str("DB_USER")
DB_PASSWORD = env.str("DB_PASSWORD")
DB_HOST = env.str("DB_HOST")
DB_PORT = env.int("DB_PORT")

API_URL = env.str("API_URL")
