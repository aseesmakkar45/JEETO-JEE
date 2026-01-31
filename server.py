import http.server
import socketserver
import json
import csv
import os
import datetime

PORT = 8000

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/submit-form':
            # 1. Get the length of the data
            content_length = int(self.headers['Content-Length'])
            
            # 2. Read the data
            post_data = self.rfile.read(content_length)
            
            try:
                # 3. Parse JSON
                data = json.loads(post_data.decode('utf-8'))
                
                # 4. Prepare data for CSV
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Expected fields from frontend: name, phone, class, message (optional)
                row = [
                    timestamp,
                    data.get('name', ''),
                    data.get('phone', ''),
                    data.get('classGrade', ''), # Note: frontend might send 'classGrade' or 'class'
                    data.get('message', '')
                ]
                
                # 5. Append to CSV
                file_exists = os.path.isfile('leads.csv')
                
                with open('leads.csv', 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # Write header if file is new
                    if not file_exists:
                        writer.writerow(['Timestamp', 'Name', 'Phone', 'Class/Grade', 'Message'])
                    
                    writer.writerow(row)
                
                # 6. Send Response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "Data saved successfully"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                print(f"Error processing POST request: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            # Fallback for other POST requests (not supported)
            self.send_response(404)
            self.end_headers()

# Create the server
with socketserver.TCPServer(("", PORT), MyHttpRequestHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server.")
    httpd.serve_forever()
