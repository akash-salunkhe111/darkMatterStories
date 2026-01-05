import asyncio
import os
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from app.settings import settings
from app.models import StoryRequest, StoryResponse, StoryAIOutput, ReadingEffort
from app.db import db

# Configure OpenAI environment variables for the model to pick up
os.environ["OPENAI_BASE_URL"] = settings.LLM_BASE_URL
os.environ["OPENAI_API_KEY"] = settings.LLM_API_KEY

model = OpenAIModel(
    model_name=settings.LLM_MODEL,
)

READING_EFFORT_PROMPTS = {
    ReadingEffort.LEVEL_1: "Use a 5th-grade reading level. Keep sentences under 15 words. Avoid technical jargon; explain sci-fi concepts simply. Focus on dialogue and action.",
    ReadingEffort.LEVEL_2: "Use a high-school reading level. Mix short and long sentences. Use common sci-fi terms without over-explaining or getting too technical.",
    ReadingEffort.LEVEL_3: "Use a university reading level. Employ complex sentence structures and 'Show, Don't Tell' descriptions. Use rich, evocative vocabulary and abstract metaphors.",
    ReadingEffort.LEVEL_4: "Write with extreme precision. Use dense paragraphs, heavy technical jargon, and complex speculative theories. Assume the reader has a high scientific IQ.",
}

story_agent = Agent(
    model,
    output_type=StoryAIOutput,
    system_prompt=(
        "You are 'Event Horizon', an advanced AI storyteller. "
        "Generate a creative, detailed, and immersive sci-fi story based on the user's inputs. "
        "Adhere to the requested genre, time period, characters, and reading effort level. "
        "The story must be a complete narrative with a beginning, middle, and end, NOT a summary. "
        "Aim for a length appropriate to the complexity, typically 400-800 words unless specified otherwise. "
        "You MUST respond with a VALID JSON object matching the output schema. "
        "Ensure the 'full_text' field contains the entire story, not just a snippet."
    ),
)

async def generate_and_save_story(request: StoryRequest) -> StoryResponse:
    participants_desc = "\n".join(
        [f"- {p.archetype}" + (f": {p.custom_desc}" if p.custom_desc else "") for p in request.participants]
    )
    
    reading_effort_instruction = READING_EFFORT_PROMPTS.get(request.reading_effort, READING_EFFORT_PROMPTS[ReadingEffort.LEVEL_2])

    chapter_instruction = "Write a complete, detailed story"
    if request.create_only_first_chapter:
        chapter_instruction = "Write ONLY the first chapter of a story"

    prompt = (
        f"{chapter_instruction} based on these parameters:\n"
        f"Genres: {', '.join(request.genres)}\n"
        f"Time Period: {request.time_period.value}\n"
        f"Participants:\n{participants_desc}\n"
        f"Narrative Spark: {request.narrative_spark.starter} "
        f"{'- ' + request.narrative_spark.custom_spark if request.narrative_spark.custom_spark else ''}\n\n"
        f"Reading Effort & Style Instructions:\n{reading_effort_instruction}\n"
        f"IMPORTANT: Provide a full, engaging story in the 'full_text' field, not a brief synopsis."
    )
    
    # Run the agent
    result = await story_agent.run(prompt)
    ai_output = result.output
    
    # Store in Qdrant (offload to thread to avoid blocking loop with embedding generation)
    await asyncio.to_thread(
        db.add_story,
        story_text=ai_output.full_text,
        metadata={
            "title": ai_output.title,
            "genres": request.genres,
            "time_period": request.time_period.value,
            "dystopia_probability": ai_output.dystopia_probability,
            "reading_effort": request.reading_effort.value
        }
    )
    
    return StoryResponse(
        **ai_output.model_dump(),
        request_params=request
    )
