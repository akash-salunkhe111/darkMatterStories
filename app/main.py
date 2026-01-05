from fastapi import FastAPI, HTTPException
from app.models import StoryRequest, StoryResponse
from app.agent import generate_and_save_story

app = FastAPI(
    title="Event Horizon Backend",
    description="Backend for the Event Horizon sci-fi story generator.",
    version="0.1.0"
)

@app.post("/generate", response_model=StoryResponse)
async def generate_story_endpoint(request: StoryRequest):
    try:
        story = await generate_and_save_story(request)
        return story
    except Exception as e:
        # In production, you'd want to log the error and hide details
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to Event Horizon API. Use POST /generate to create stories."}
