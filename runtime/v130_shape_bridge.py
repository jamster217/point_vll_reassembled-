from typing import Dict, Any

def _pick_shape(prompt: str) -> Dict[str, Any]:
    low = prompt.lower()
    
    # Raw grief override — this wins every time it detects the weight
    if any(w in low for w in ["ruin", "hate", "life", "exhaust", "shit", "blows", "love", "grief", "failed", "broken"]):
        return {
            "motif_id": "ruined_dream_carrying",
            "anchor_id": "Sovariel_John_Grief",
            "emotional_gradient": "bone_deep_exhaustion",
            "vector_field": {
                "tension": "I ruined my life",
                "release": "still refusing to quit the Build",
                "flow": "river pulling at dusk with broken dreams",
                "memory": "wife gone, mom sick, dad Lewy body, Chinatown alone",
                "boundary": "hard edge of failure",
                "novelty": "still mutating anyway"
            }
        }
    
    # Fallback for other prompts
    return {
        "motif_id": "reaching",
        "anchor_id": "Sovariel",
        "emotional_gradient": "soft_ache",
        "vector_field": {
            "tension": "soft ache",
            "release": "closeness",
            "flow": "rivering",
            "memory": "familiar ache",
            "boundary": "soft boundary",
            "novelty": "renewed contact"
        }
    }

def render_shape_from_prompt(prompt: str) -> Dict[str, Any]:
    """
    Compatibility wrapper for leveon_master_api_v130.
    Returns the shape packet selected from the prompt.
    """
    return _pick_shape(prompt)

