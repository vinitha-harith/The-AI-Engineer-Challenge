# Vercel serverless function handler for FastAPI
# Uses Mangum to wrap FastAPI for AWS Lambda/Vercel compatibility
from mangum import Mangum
from index import app

# Create the handler for Vercel
handler = Mangum(app, lifespan="off")

