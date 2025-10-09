import os
from dotenv import load_dotenv

from core.constants import APP_NAME

load_dotenv()

if __name__ == "__main__":
    print(f"Welcome to {APP_NAME} - an AI powered wardrobe planner")