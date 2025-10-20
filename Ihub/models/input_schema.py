from pydantic import BaseModel, Field
from typing import List

class RouteInput(BaseModel):
    """
    Structured model for extracting key data from a single, unstructured user sentence.
    """
    current_location: str = Field(..., description="The most likely starting point or origin city/place the user mentioned.")
    destination: str = Field(..., description="The most likely final destination city/place the user mentioned.")
    requirements: List[str] = Field(..., description="A list of all path requirements the user mentioned (e.g., 'greenery', 'safety', 'hotels', 'avoid tolls').")