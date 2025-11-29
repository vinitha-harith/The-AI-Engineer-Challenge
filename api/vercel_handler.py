# Vercel serverless function handler for FastAPI
# Import the FastAPI app and wrap with Mangum

import sys
import os
from mangum import Mangum

# Add the api directory to the path to ensure imports work
sys.path.insert(0, os.path.dirname(__file__))

# Import the app from index
from index import app

# Create the handler function for Vercel
handler = Mangum(app, lifespan="off")
