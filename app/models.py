from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class TimePeriod(str, Enum):
    NEAR_FUTURE = "2030s"
    FAR_FUTURE = "2150s"
    DISTANT_FUTURE = "3000+"
    END_OF_TIME = "End of Time"

class ReadingEffort(str, Enum):
    LEVEL_1 = "Level 1 (Quick-Read / Light)"
    LEVEL_2 = "Level 2 (Standard / Balanced)"
    LEVEL_3 = "Level 3 (Deep / Immersive)"
    LEVEL_4 = "Level 4 (Technical / Hard)"

class Participant(BaseModel):
    archetype: str = Field(..., description="The archetype of the character, e.g., 'The Rebel', 'The Scientist'")
    custom_desc: Optional[str] = Field(None, description="Optional custom description or traits")

class NarrativeSpark(BaseModel):
    starter: str = Field(..., description="The initial situation or inciting incident")
    custom_spark: Optional[str] = Field(None, description="Optional custom details for the spark")

class StoryRequest(BaseModel):
    genres: List[str] = Field(..., description="List of sci-fi subgenres, e.g., 'Cyberpunk', 'Solarpunk'")
    time_period: TimePeriod = Field(..., description="The era in which the story takes place")
    participants: List[Participant] = Field(..., description="List of characters involved in the story")
    narrative_spark: NarrativeSpark
    reading_effort: ReadingEffort = Field(default=ReadingEffort.LEVEL_2, description="The desired reading level/complexity of the story")
    create_only_first_chapter: bool = Field(default=False, description="If true, generate only the first chapter of the story")

class StoryAIOutput(BaseModel):
    title: str = Field(..., description="The title of the generated story")
    full_text: str = Field(..., description="The complete text of the story")
    dystopia_probability: float = Field(..., description="Probability score (0-1) of the scenario being dystopian")

class StoryResponse(StoryAIOutput):
    request_params: StoryRequest = Field(..., description="The parameters used to generate this story")
