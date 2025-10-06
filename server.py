from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import shutil
from urllib.parse import parse_qs, urlparse
from datetime import datetime
import mimetypes
import base64

class Config:
    DATA_DIR = "data"
    STATIC_DIR = "static"
    FILES_DIR = "vdb_files"  # Base directory for VDB files
    VDB_FILE = os.path.join(DATA_DIR, "virtualdatabases.json")
    ENTRIES_FILE = os.path.join(DATA_DIR, "entries.json")
    
    # Cloud storage configuration
    CLOUD_STORAGE = os.environ.get('RENDER', False)  # Check if running on Render
    if CLOUD_STORAGE:
        # Use persistent disk for cloud storage
        FILES_DIR = "/opt/render/project/vdb2-storage/vdb_files"
        DATA_DIR = "/opt/render/project/vdb2-storage/data"
        VDB_FILE = os.path.join(DATA_DIR, "virtualdatabases.json")
        ENTRIES_FILE = os.path.join(DATA_DIR, "entries.json")

class DatabaseManager:
    @staticmethod
    def initialize_directories():
        """Create necessary directories if they don't exist"""
        for directory in [Config.DATA_DIR, Config.STATIC_DIR, Config.FILES_DIR]:
            os.makedirs(directory, exist_ok=True)

    @staticmethod
    def initialize_database():
        """Initialize database files if they don't exist"""
        if not os.path.exists(Config.VDB_FILE):
            with open(Config.VDB_FILE, "w") as f:
                json.dump([], f)

        if not os.path.exists(Config.ENTRIES_FILE):
            with open(Config.ENTRIES_FILE, "w") as f:
                json.dump({}, f)

    @staticmethod
    def get_vdb_files_dir(vdb_id):
        """Get the directory path for a specific VDB's files"""
        vdb_files_dir = os.path.join(Config.FILES_DIR, f"vdb_{vdb_id}")
        os.makedirs(vdb_files_dir, exist_ok=True)
        return vdb_files_dir

    @staticmethod
    def save_file(vdb_id, entry_id, field_name, file_data, file_name):
        """Save a file to the appropriate VDB directory"""
        try:
            # Get the VDB directory
            vdb_dir = DatabaseManager.get_vdb_files_dir(vdb_id)
            
            # Create a unique filename
            unique_filename = f"{entry_id}_{field_name}_{file_name}"
            file_path = os.path.join(vdb_dir, unique_filename)
            
            # Extract the base64 data (remove data:image/jpeg;base64, part)
            if ',' in file_data:
                file_data = file_data.split(',')[1]
            
            # Decode and save the file
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(file_data))
            
            # Return the relative path for storage in the database (use forward slashes for web URLs)
            return os.path.join("vdb_files", f"vdb_{vdb_id}", unique_filename).replace("\\", "/")
        except Exception as e:
            print(f"Error saving file: {e}")
            return None

class VDB2Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Serve static files
        if self.path == "/":
            self.path = "/static/index.html"
            return SimpleHTTPRequestHandler.do_GET(self)
        
        # Serve VDB files
        if parsed_path.path.startswith("/vdb_files/"):
            file_path = os.path.join(os.getcwd(), parsed_path.path[1:])
            if os.path.exists(file_path) and os.path.isfile(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        self.send_response(200)
                        content_type, _ = mimetypes.guess_type(file_path)
                        self.send_header('Content-type', content_type or 'application/octet-stream')
                        self.end_headers()
                        shutil.copyfileobj(f, self.wfile)
                except Exception as e:
                    self.send_error(500, f"Error serving file: {str(e)}")
                return
        
        # API endpoints
        if parsed_path.path == "/api/vdbs":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            with open(Config.VDB_FILE, "r") as f:
                self.wfile.write(json.dumps(json.load(f)).encode())
            return
            
        elif parsed_path.path.startswith("/api/vdbs/") and "/entries" in parsed_path.path:
            vdb_id = parsed_path.path.split("/")[3]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            with open(Config.ENTRIES_FILE, "r") as f:
                entries = json.load(f)
                vdb_entries = entries.get(vdb_id, [])
                self.wfile.write(json.dumps(vdb_entries).encode())
            return
            
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if self.path == "/api/vdbs":
            with open(Config.VDB_FILE, "r") as f:
                vdbs = json.load(f)
            
            vdb_id = len(vdbs) + 1
            data["id"] = vdb_id
            vdbs.append(data)
            
            # Create directory for this VDB's files
            DatabaseManager.get_vdb_files_dir(vdb_id)
            
            with open(Config.VDB_FILE, "w") as f:
                json.dump(vdbs, f, indent=2)
            
            self.wfile.write(json.dumps(data).encode())
            
        elif "/entries" in self.path:
            vdb_id = self.path.split("/")[3]
            with open(Config.ENTRIES_FILE, "r") as f:
                entries = json.load(f)
            
            if vdb_id not in entries:
                entries[vdb_id] = []
            
            entry_id = len(entries[vdb_id]) + 1
            data["id"] = entry_id
            data["created_at"] = datetime.now().isoformat()

            # Handle file fields
            for field_name, field_value in data["values"].items():
                if isinstance(field_value, dict) and "file_data" in field_value:
                    file_path = DatabaseManager.save_file(
                        vdb_id,
                        entry_id,
                        field_name,
                        field_value["file_data"],
                        field_value["file_name"]
                    )
                    if file_path:
                        data["values"][field_name] = file_path
                    else:
                        data["values"][field_name] = "ERROR_SAVING_FILE"

            entries[vdb_id].append(data)
            
            with open(Config.ENTRIES_FILE, "w") as f:
                json.dump(entries, f, indent=2)
            
            self.wfile.write(json.dumps(data).encode())

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        SimpleHTTPRequestHandler.end_headers(self)

def run_server():
    """Initialize and run the server"""
    print("Initializing server...")
    DatabaseManager.initialize_directories()
    DatabaseManager.initialize_database()
    
    # Get port from environment variable (for Render) or use default
    port = int(os.environ.get('PORT', 8080))
    host = '0.0.0.0' if os.environ.get('RENDER') else 'localhost'
    
    server = HTTPServer((host, port), VDB2Handler)
    print(f"Server started at http://{host}:{port}")j
    print(f"Files will be stored in: {os.path.abspath(Config.FILES_DIR)}")
    print(f"Cloud storage: {Config.CLOUD_STORAGE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()

if __name__ == "__main__":
    run_server()