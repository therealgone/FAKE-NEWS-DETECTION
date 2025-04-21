import http.server
import socketserver
import os
import sys

def start_server(port=3001):
    try:
        Handler = http.server.SimpleHTTPRequestHandler
        Handler.extensions_map.update({
            '.js': 'application/javascript',
        })
        
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"Starting server on port {port}...")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98 or e.errno == 10048:  # Port already in use
            print(f"Port {port} is already in use. Trying port {port + 1}")
            start_server(port + 1)
        else:
            print(f"Error starting server: {e}")
            sys.exit(1)

if __name__ == "__main__":
    os.chdir('frontend')  # Change to frontend directory
    start_server() 