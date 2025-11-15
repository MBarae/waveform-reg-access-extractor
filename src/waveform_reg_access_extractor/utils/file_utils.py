"""File utility functions."""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def ensure_directory(directory_path: str) -> bool:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except OSError as e:
        logger.error(f"Failed to create directory {directory_path}: {e}")
        return False


def validate_file(file_path: str, required_extensions: Optional[list] = None) -> bool:
    """
    Validate that a file exists and has the required extension.
    
    Args:
        file_path: Path to the file
        required_extensions: List of required file extensions (e.g., ['.vcd', '.xml'])
        
    Returns:
        True if file is valid, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return False
    
    if not os.path.isfile(file_path):
        logger.error(f"Path is not a file: {file_path}")
        return False
    
    if required_extensions:
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in required_extensions:
            logger.error(f"File extension {file_ext} not in required extensions: {required_extensions}")
            return False
    
    return True


def get_file_size(file_path: str) -> Optional[int]:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes or None if error
    """
    try:
        return os.path.getsize(file_path)
    except OSError as e:
        logger.error(f"Failed to get file size for {file_path}: {e}")
        return None
