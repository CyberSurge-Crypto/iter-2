#!/usr/bin/env python3
"""
Example usage of the file-based database.
"""

from core import Database

def main():
    """Example usage of the database."""
    
    # Initialize a database instance with a custom path
    db = Database("./my_database")
    print(f"Database initialized at: {db.db_path}")
    
    # Create tables
    db.create_table("users")
    db.create_table("products")
    print(f"Available tables: {db.list_tables()}")
    
    # Insert data
    db.create("users", {"id": 1, "name": "John Doe", "email": "john@example.com"})
    db.create("users", {"id": 2, "name": "Jane Smith", "email": "jane@example.com"})
    
    db.create("products", [
        {"id": 101, "name": "Laptop", "price": 1299.99},
        {"id": 102, "name": "Smartphone", "price": 799.99},
        {"id": 103, "name": "Headphones", "price": 149.99}
    ])
    
    # Read data
    users = db.read("users")
    print("\nUsers:")
    for user in users:
        print(f"  - {user['name']} ({user['email']})")
    
    products = db.read("products")
    print("\nProducts:")
    for product in products:
        print(f"  - {product['name']}: ${product['price']}")
    
    # Update data (replace all users)
    db.update("users", [
        {"id": 1, "name": "John Doe", "email": "john.doe@company.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane.smith@company.com"},
        {"id": 3, "name": "Bob Johnson", "email": "bob@company.com"}
    ])
    
    # Read updated data
    updated_users = db.read("users")
    print("\nUpdated Users:")
    for user in updated_users:
        print(f"  - {user['name']} ({user['email']})")
    
    # Delete all data in a table
    db.delete("products")
    print(f"\nProducts after delete: {db.read('products')}")
    
    # Delete a table
    db.delete_table("products")
    print(f"Available tables after deletion: {db.list_tables()}")

if __name__ == "__main__":
    main() 