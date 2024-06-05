
#& Imports
from dotenv import load_dotenv
import os

#& Load Environment Variables
load_dotenv()

#& Get env value
#* You can use like this: `env("environment variable name (string)")`
def env(key: str) -> str:
    return os.environ.get(key)
