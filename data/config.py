import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

admins_id = [
    656634975,
]

DBIP = os.getenv('DBIP')
PGUSER = str(os.getenv('PGUSER'))
PGPASS = str(os.getenv('PGPASS'))
DB = str(os.getenv('DB'))

POSTGRES_URI = f'postgresql://{PGUSER}:{PGPASS}@{DBIP}/{DB}'
