# Vercel serverless function handler for FastAPI
# Uses Mangum to wrap FastAPI for AWS Lambda/Vercel compatibility
from mangum import Mangum

# Import the FastAPI app
# Since both files are in the same directory (api/), use direct import
from index import app

# Create the handler for Vercel - this is what Vercel will call
handler = Mangum(app, lifespan="off")

