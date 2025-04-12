import uvicorn
import sys
import os

# Thêm thư mục hiện tại vào sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    uvicorn.run("app.main:app", 
                host="127.0.0.1", 
                port=8000, 
                reload=True)