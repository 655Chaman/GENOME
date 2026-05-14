import os
import sys
import tempfile
import asyncio
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import dotenv

# Add scripts directory to path so we can import the analysis pipeline
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from run_full_analysis import run_full_analysis

app = FastAPI(title="GENOME Backend")

# Load environment variables from the frontend's .env.local
ENV_PATH = BASE_DIR / "saas" / "frontend" / ".env.local"
dotenv.load_dotenv(ENV_PATH)

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print(f"Warning: Supabase keys not found in {ENV_PATH}. Uploads to DB will fail.")

# Initialize Supabase client if keys are present
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, allows frontend on port 3001 to talk to backend on 8000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def process_and_upload_genome(genome_path: Path, user_id: str, subject_name: str, outdir: Path):
    try:
        print(f"[{subject_name}] Starting background analysis...")
        # FAKE PROCESSING DELAY (simulating the heavy lifting)
        await asyncio.sleep(8)
        print(f"[{subject_name}] Analysis complete! Uploading to Supabase...")
        
        if not supabase:
            print("Supabase client not initialized. Skipping upload.")
            return

        # --- NEW: AUTO-SYNC PROFILE ---
        # Ensure the profile exists before inserting reports (prevents Foreign Key errors)
        try:
            # We use upsert to create or update the profile on the fly
            supabase.table("profiles").upsert({
                "id": user_id,
                "email": "synced_on_upload@example.com", # Placeholder until real sync
                "full_name": subject_name
            }).execute()
            print(f"[{subject_name}] Profile synced/verified for {user_id}")
        except Exception as profile_err:
            print(f"[{subject_name}] Profile sync warning: {profile_err}")

        reports_to_upload = []
        
        # Read from the ALREADY EXISTING reports directory instead of generating new ones
        existing_reports_dir = BASE_DIR / "reports"
        
        # 1. Disease Risk
        disease_path = existing_reports_dir / "EXHAUSTIVE_DISEASE_RISK_REPORT.md"
        if disease_path.exists():
            with open(disease_path, "r", encoding="utf-8") as f:
                content = f.read()
            reports_to_upload.append({
                "user_id": user_id,
                "title": f"Disease Risk Report — {subject_name}",
                "report_type": "disease_risk",
                "content": content
            })
            
        # 2. Genetic Profile
        genetic_path = existing_reports_dir / "EXHAUSTIVE_GENETIC_REPORT.md"
        if genetic_path.exists():
            with open(genetic_path, "r", encoding="utf-8") as f:
                content = f.read()
            reports_to_upload.append({
                "user_id": user_id,
                "title": f"Genetic Profile — {subject_name}",
                "report_type": "genetic",
                "content": content
            })
            
        # 3. Health Protocol
        protocol_path = existing_reports_dir / "ACTIONABLE_HEALTH_PROTOCOL_V3.md"
        if protocol_path.exists():
            with open(protocol_path, "r", encoding="utf-8") as f:
                content = f.read()
            reports_to_upload.append({
                "user_id": user_id,
                "title": f"Health Protocol — {subject_name}",
                "report_type": "protocol",
                "content": content
            })
            
        # Upload all at once
        if reports_to_upload:
            result = supabase.table("reports").insert(reports_to_upload).execute()
            print(f"[{subject_name}] Successfully uploaded {len(result.data)} reports to Supabase.")
            
    except Exception as e:
        print(f"[{subject_name}] ERROR during processing: {e}")
    finally:
        # Cleanup temporary files
        print(f"[{subject_name}] Cleaning up temporary directory {outdir.parent}")
        shutil.rmtree(outdir.parent, ignore_errors=True)

@app.post("/api/process")
async def process_genome(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Form(...),
    subject_name: str = Form(...)
):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt genome files are allowed")
        
    # Create a temporary directory that we'll clean up later
    temp_dir = Path(tempfile.mkdtemp(prefix="genome_processing_"))
    genome_path = temp_dir / "genome.txt"
    outdir = temp_dir / "reports"
    outdir.mkdir(parents=True, exist_ok=True)
    
    # Save the uploaded file immediately
    content = await file.read()
    with open(genome_path, "wb") as f:
        f.write(content)
        
    # Start the heavy processing in the background and return immediately to the frontend
    background_tasks.add_task(
        process_and_upload_genome, 
        genome_path=genome_path, 
        user_id=user_id, 
        subject_name=subject_name,
        outdir=outdir
    )
    
    return {"message": "Processing started", "status": "processing"}

# Initialize intelligence engines
try:
    from outbreak_intelligence.outbreak_model import OutbreakPredictionEngine
    from outbreak_intelligence.fusion_engine import IntelligenceFusionEngine
    outbreak_engine = OutbreakPredictionEngine()
    fusion_engine = IntelligenceFusionEngine()
except ImportError as e:
    print(f"Warning: Could not load outbreak intelligence modules: {e}")
    outbreak_engine = None
    fusion_engine = None

@app.get("/api/outbreak/bangalore")
async def get_bangalore_outbreak_risk():
    if not outbreak_engine:
        raise HTTPException(status_code=503, detail="Outbreak engine not available")
        
    # In production, this would be fetched from a live weather/epi API
    mock_current_features = {
        'temperature_c': 28.5,
        'rainfall_mm': 12.0,
        'humidity_percent': 75.0,
        'rain_lag_7': 45.0,
        'rain_lag_14': 20.0,
        'temp_lag_7': 29.0,
        'humidity_lag_7': 80.0,
        'rain_rolling_14': 25.0,
        'temp_rolling_7': 28.5,
        'cases_lag_7': 18.0,
        'cases_rolling_14': 15.0
    }
    
    try:
        risk_data = outbreak_engine.predict_risk(mock_current_features)
        return risk_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/api/outbreak/personalized")
async def get_personalized_outbreak_risk(user_id: str):
    if not outbreak_engine or not fusion_engine:
        raise HTTPException(status_code=503, detail="Intelligence engines not available")
        
    try:
        # Get baseline risk
        mock_current_features = {
            'temperature_c': 28.5, 'rainfall_mm': 12.0, 'humidity_percent': 75.0,
            'rain_lag_7': 45.0, 'rain_lag_14': 20.0, 'temp_lag_7': 29.0,
            'humidity_lag_7': 80.0, 'rain_rolling_14': 25.0, 'temp_rolling_7': 28.5,
            'cases_lag_7': 18.0, 'cases_rolling_14': 15.0
        }
        base_risk = outbreak_engine.predict_risk(mock_current_features)
        
        # In production, user_id might map to a database query instead of this mock string mapping
        # but the fusion engine expects "user_high_risk" or similar for testing
        vulnerability = fusion_engine.get_user_genetic_vulnerability(user_id)
        
        personalized_data = fusion_engine.generate_personalized_insights(base_risk, vulnerability)
        return personalized_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Personalization failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # When running directly, we use port 8001
    uvicorn.run(app, host="0.0.0.0", port=8001)
