import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

def ensure_dir_exists(directory: Path) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: The directory path to check/create.
    """
    directory.mkdir(exist_ok=True, parents=True)

def is_valid_json(data: Any) -> bool:
    """
    Check if data is valid JSON (can be serialized).
    
    Args:
        data: The data to check.
        
    Returns:
        bool: True if the data can be serialized to JSON, False otherwise.
    """
    try:
        json.dumps(data)
        return True
    except (TypeError, OverflowError):
        return False

def safely_read_json(file_path: Path) -> List[Dict[str, Any]]:
    """
    Safely read JSON from a file, returning an empty list if the file does not exist or is corrupted.
    
    Args:
        file_path: The path to the JSON file.
        
    Returns:
        List[Dict[str, Any]]: The data from the file, or an empty list if there was an error.
    """
    if not file_path.exists():
        return []
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def safely_write_json(file_path: Path, data: Any) -> bool:
    """
    Safely write data to a JSON file.
    
    Args:
        file_path: The path to the JSON file.
        data: The data to write.
        
    Returns:
        bool: True if the data was written successfully, False otherwise.
    """
    if not is_valid_json(data):
        return False
    
    try:
        # Ensure the directory exists
        file_path.parent.mkdir(exist_ok=True, parents=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except (TypeError, OverflowError, IOError):
        return False 