import os

from dotenv import load_dotenv

TOKEN = str(os.getenv('BOT_TOKEN'))
API_URL = str(os.getenv('API_URL'))

load_dotenv()
app_prefix = str(os.getenv('APP_PREFIX'))

