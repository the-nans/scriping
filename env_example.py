import os

from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("USERNAME", None)
print(USERNAME)


