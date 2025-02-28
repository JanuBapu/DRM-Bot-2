import os

API_ID    = os.environ.get("API_ID", "22594398")
API_HASH  = os.environ.get("API_HASH", "3a2408d97d6a222d87766dac2da302df")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7429048456:AAEH21RqF9AuwkjFl7FcnpGtJd4B2_uTsHk") 

WEBHOOK = True  # Don't change this
PORT = int(os.environ.get("PORT", 8080))  # Default to 8000 if not set
