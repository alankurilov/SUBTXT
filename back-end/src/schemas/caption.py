from pydantic import BaseModel, Field

class Caption(BaseModel):
    title: str = Field(description="Short title describing the concept or reference.")
    start: float = Field(
        ge=0,
        description="Start time of the caption in seconds from the beginning of the video."
    )
    end: float = Field(
        ge=0,
        description="End time of the caption in seconds from the beginning of the video."
    )
    explanation: str = Field(
        description="Clear explanation of the concept or context that may be unclear to the viewer."
    )