from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import uuid
from datetime import datetime
import tempfile
import shutil
from deepface import DeepFace
import asyncio
from concurrent.futures import ThreadPoolExecutor

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="FaceVerify AI", description="AI-powered facial recognition API")

# +++ NEW ROBUST CORS LOGIC +++
# Get the comma-separated string of origins from the environment variable
# Default to localhost for local development
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")

# Split the string into a list and strip any whitespace from each origin
origins = [origin.strip() for origin in cors_origins_str.split(',')]

# Add the CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Thread executor for running blocking operations
executor = ThreadPoolExecutor(max_workers=4)

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class FacialArea(BaseModel):
    x: int
    y: int
    w: int
    h: int

class FaceVerificationResult(BaseModel):
    verified: bool
    match_percentage: float
    model_used: str
    facial_areas: Dict[str, FacialArea]

class ErrorResponse(BaseModel):
    error: str

# Helper function to run deepface verification in a thread
def run_deepface_verification(img1_path: str, img2_path: str) -> Dict[str, Any]:
    try:
        # Use ArcFace model for high accuracy
        result = DeepFace.verify(
            img1_path=img1_path,
            img2_path=img2_path,
            model_name='ArcFace',
            enforce_detection=False,
            detector_backend='opencv'
        )
        return result
    except Exception as e:
        raise Exception(str(e))

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "FaceVerify AI - Face Verification Service"}

@api_router.post("/verify", response_model=FaceVerificationResult)
async def verify_faces(
    image1: UploadFile = File(..., description="First image for comparison"),
    image2: UploadFile = File(..., description="Second image for comparison")
):
    # Validate file types
    allowed_types = ["image/jpeg", "image/jpg", "image/png"]
    if image1.content_type not in allowed_types or image2.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG images are supported"
        )
    
    # Validate file sizes (5MB limit)
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    
    # Read file contents
    try:
        image1_content = await image1.read()
        image2_content = await image2.read()
        
        if len(image1_content) > max_size or len(image2_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail="File size must be less than 5MB"
            )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Error reading uploaded files"
        )
    
    # Create temporary files
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        
        # Write images to temporary files
        temp_path1 = os.path.join(temp_dir, f"img1_{uuid.uuid4()}.{image1.filename.split('.')[-1]}")
        temp_path2 = os.path.join(temp_dir, f"img2_{uuid.uuid4()}.{image2.filename.split('.')[-1]}")
        
        with open(temp_path1, 'wb') as f:
            f.write(image1_content)
        
        with open(temp_path2, 'wb') as f:
            f.write(image2_content)
        
        # Run face verification in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor, 
            run_deepface_verification, 
            temp_path1, 
            temp_path2
        )
        
        # Extract distance and convert to percentage
        distance = result.get('distance', 1.0)
        match_percentage = round((1 - distance) * 100, 2)
        
        # Extract facial areas
        facial_areas = result.get('facial_areas', {})
        
        # Format facial areas for response
        formatted_facial_areas = {}
        for key, area in facial_areas.items():
            if isinstance(area, dict) and all(k in area for k in ['x', 'y', 'w', 'h']):
                formatted_facial_areas[key] = FacialArea(
                    x=int(area['x']),
                    y=int(area['y']),
                    w=int(area['w']),
                    h=int(area['h'])
                )
        
        return FaceVerificationResult(
            verified=result.get('verified', False),
            match_percentage=match_percentage,
            model_used="ArcFace",
            facial_areas=formatted_facial_areas
        )
        
    except Exception as e:
        error_message = str(e)
        
        # Handle specific DeepFace errors
        if "Face could not be detected" in error_message or "No face detected" in error_message:
            raise HTTPException(
                status_code=400,
                detail="Face not detected in one or both images. Please use a clearer photo."
            )
        else:
            logging.error(f"Face verification error: {error_message}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred during face verification. Please try again."
            )
    
    finally:
        # Clean up temporary files
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    executor.shutdown(wait=True)