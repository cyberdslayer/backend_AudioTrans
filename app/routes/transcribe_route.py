from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path
import shutil
import speech_recognition as sr

# Initialize router
router = APIRouter()

# Path to save uploaded files temporarily
UPLOAD_DIR = Path("uploaded_files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("")
async def transcribe_audio(file: UploadFile = File(...)):
    
    file_path = UPLOAD_DIR / file.filename

    try:
        # Validate file type
        if not file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="Unsupported file type.")
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Perform transcription
        recognizer = sr.Recognizer()
        with sr.AudioFile(str(file_path)) as source:
            audio_data = recognizer.record(source)
            transcription = recognizer.recognize_google(audio_data)
        
        return {"text": transcription}
    
    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="Unable to recognize speech in the audio file.")
    except sr.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Speech recognition service error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        # Clean up the uploaded file
        if file_path.exists():
            file_path.unlink()
