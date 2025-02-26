from waitress import serve
from flask_app import create_app
import webbrowser
import sys
from flask_cors import CORS

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8080
    host = '127.0.0.1'
    server = create_app()
    
    # Enable CORS
    CORS(server, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],  # Your Next.js frontend URL
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    print(f'API Server running on http://{host}:{port}')
    serve(server, host=host, port=port)