"""
A simple file-based database package.

This package provides a simple file-based database implementation that stores data
in JSON files. Each table is represented as a separate JSON file.

Basic usage:
    from db import Database
    
    # Initialize a database instance
    db = Database()  # Uses default path
    
    # Create a table
    db.create_table("users")
    
    # Insert data
    db.create("users", {"id": 1, "name": "John Doe"})
    
    # Read data
    users = db.read("users")
    
    # Update data
    db.update("users", [{"id": 1, "name": "Jane Doe"}])
    
    # Delete all data in a table
    db.delete("users")
    
    # Delete a table
    db.delete_table("users")
"""

from .core import Database

__version__ = "0.1.0"
__all__ = ["Database"]
