import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

class Database:
    """
    A simple file-based database that stores data in JSON files.
    Each table is a separate file in the 'tables' subdirectory.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the database with an optional path.
        
        Args:
            db_path: The path to the database directory. If None, a default path will be used.
        """
        if db_path is None:
            # Use a default path in the current directory
            self.db_path = Path(os.getcwd()) / "db_data"
        else:
            self.db_path = Path(db_path)
        
        # Create the main database directory if it doesn't exist
        self.db_path.mkdir(exist_ok=True, parents=True)
        
        # Create tables directory if it doesn't exist
        self.tables_path = self.db_path / "tables"
        self.tables_path.mkdir(exist_ok=True)
    
    def create_table(self, table_name: str) -> bool:
        """
        Create a new table (file) in the database.
        
        Args:
            table_name: The name of the table to create.
            
        Returns:
            bool: True if the table was created successfully, False if it already exists.
        """
        table_path = self.tables_path / f"{table_name}.json"
        
        if table_path.exists():
            return False
        
        # Create an empty table (file with empty list)
        with open(table_path, 'w') as f:
            json.dump([], f)
        
        return True
    
    def delete_table(self, table_name: str) -> bool:
        """
        Delete a table (file) from the database.
        
        Args:
            table_name: The name of the table to delete.
            
        Returns:
            bool: True if the table was deleted successfully, False if it doesn't exist.
        """
        table_path = self.tables_path / f"{table_name}.json"
        
        if not table_path.exists():
            return False
        
        os.remove(table_path)
        return True
    
    def list_tables(self) -> List[str]:
        """
        List all tables in the database.
        
        Returns:
            List[str]: A list of table names (without the .json extension).
        """
        tables = []
        for file in self.tables_path.glob("*.json"):
            tables.append(file.stem)
        return tables
    
    def _get_table_path(self, table_name: str) -> Path:
        """Get the full path to a table file."""
        return self.tables_path / f"{table_name}.json"
    
    def _read_table_data(self, table_name: str) -> List[Dict[str, Any]]:
        """Read and parse data from a table file."""
        table_path = self._get_table_path(table_name)
        
        if not table_path.exists():
            raise ValueError(f"Table '{table_name}' does not exist.")
        
        with open(table_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # If the file is empty or corrupted, return an empty list
                return []
    
    def _write_table_data(self, table_name: str, data: List[Dict[str, Any]]) -> None:
        """Write data to a table file."""
        table_path = self._get_table_path(table_name)
        
        if not table_path.exists():
            raise ValueError(f"Table '{table_name}' does not exist.")
        
        with open(table_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create(self, table_name: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """
        Insert data into a table.
        
        Args:
            table_name: The name of the table.
            data: A single JSON object or a list of JSON objects to insert.
        """
        # Read existing data
        existing_data = self._read_table_data(table_name)
        
        # Add new data
        if isinstance(data, dict):
            existing_data.append(data)
        elif isinstance(data, list):
            existing_data.extend(data)
        else:
            raise TypeError("Data must be a dict or a list of dicts")
        
        # Write updated data back to the table
        self._write_table_data(table_name, existing_data)
    
    def read(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Read all data from a table.
        
        Args:
            table_name: The name of the table.
            
        Returns:
            List[Dict[str, Any]]: All data in the table.
        """
        return self._read_table_data(table_name)
    
    def update(self, table_name: str, data: List[Dict[str, Any]]) -> None:
        """
        Update (overwrite) all data in a table.
        
        Args:
            table_name: The name of the table.
            data: The new data to replace the existing data.
        """
        if not isinstance(data, list):
            raise TypeError("Data must be a list of objects")
        
        self._write_table_data(table_name, data)
    
    def delete(self, table_name: str) -> None:
        """
        Delete (clear) all data in a table.
        
        Args:
            table_name: The name of the table.
        """
        self._write_table_data(table_name, []) 