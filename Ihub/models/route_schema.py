from pydantic import BaseModel, Field
from typing import List
from enum import Enum
# Define an Enum or a List of Literal strings for the difficulty classification
# This ensures the model only outputs one of these values.
class RequirementDifficulty(str,Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

# Pydantic Model for a single classified requirement
class ClassifiedRequirement(BaseModel):
    # e.g., "greenery", "safety", "traffic"
    name: str = Field(..., description="The user-specified requirement (e.g., 'greenery', 'safety', 'hotels').")
    
    # e.g., "green", "forest", "urban" (This is the single word/concept output)
    classified_concept: str = Field(..., description="The single, key concept related to the requirement for the path (e.g., 'forest', 'urban', 'minimal').")
    
    # The classification based on availability/searchability (easy/medium/hard)
    difficulty: RequirementDifficulty = Field(..., description="The classified difficulty of the requirement: 'easy' (e.g., greenery), 'medium', or 'hard' (e.g., safety/real-time traffic).")

# The main Pydantic Model for the final JSON output
class RouteAnalysis(BaseModel):
    """
    Structured output for the user's route request.
    """
    current_location: str = Field(..., description="The confirmed starting location/city of the user.")
    destination: str = Field(..., description="The confirmed destination location/city of the user.")
    
    # List of requirements classified by the model
    classified_requirements: List[ClassifiedRequirement]