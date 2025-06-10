import uvicorn
import os
import sys

# Add both current and parent directories to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    try:
        uvicorn.run(
            "backend.app:app",
            host="127.0.0.1",
            port=8016,
            reload=True,
            log_level="debug"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1) 