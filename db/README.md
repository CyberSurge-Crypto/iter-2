# Simple File-Based Database

No installation required. Just include the `db` folder in your project.

## Usage

```python
from db import Database

# Initialize a database instance
db = Database()  # Uses default path
# Or specify a custom path
# db = Database("/path/to/database")

# Create a table
db.create_table("users")

# Insert data
db.create("users", {"id": 1, "name": "John Doe"})
# Or insert multiple items at once
db.create("users", [
    {"id": 2, "name": "Jane Smith"},
    {"id": 3, "name": "Bob Johnson"}
])

# Read all data from a table
users = db.read("users")
for user in users:
    print(f"{user['id']}: {user['name']}")

# Update (replace) all data in a table
db.update("users", [
    {"id": 1, "name": "John Doe Updated"},
    {"id": 2, "name": "Jane Smith Updated"}
])

# Delete all data in a table (clear it)
db.delete("users")

# Delete a table
db.delete_table("users")

# List all tables
tables = db.list_tables()
print(f"Available tables: {tables}")
```

## Example

See `example.py` for a complete example of using the database.