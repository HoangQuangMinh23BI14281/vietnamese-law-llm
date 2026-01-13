
import weaviate
import os
import sys

def clean_database():
    # Configuration
    weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    
    print(f"Connecting to Weaviate at {weaviate_url}...")
    
    try:
        # Initialize client (v3)
        client = weaviate.Client(
            url=weaviate_url,
            timeout_config=(5, 15)
        )
        
        # Check connection
        if not client.is_ready():
            print("Error: Weaviate is not ready.")
            sys.exit(1)
            
        # Get all classes
        schema = client.schema.get()
        classes = schema.get('classes', [])
        
        if not classes:
            print("Database is already empty.")
            return

        print(f"Found {len(classes)} classes. Deleting...")
        
        # Delete each class
        for class_obj in classes:
            class_name = class_obj['class']
            print(f"Deleting class: {class_name}")
            client.schema.delete_class(class_name)
            
        print("Database cleanup completed successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    clean_database()
