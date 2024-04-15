import os
from gino import Gino
from dotenv import load_dotenv

TOKEN = str(os.getenv('BOT_TOKEN'))

db = Gino()
load_dotenv()
app_prefix = str(os.getenv('APP_PREFIX'))

PG_IP = str(os.getenv('PG_IP'))
PG_DATABASE = str(os.getenv('PG_DATABASE'))
PG_USER = str(os.getenv('PG_USER'))
PG_PASSWORD = str(os.getenv('PG_PASSWORD'))

POSTGRES_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_IP}/{PG_DATABASE}"
