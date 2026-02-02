import sys
import os

# Ensure the parent directory is in the path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Vercel looks for 'app' or 'handler'
try:
    from app import app
    handler = app
except Exception:
    import traceback
    error_trace = traceback.format_exc()
    
    # Fallback to a raw WSGI app to avoid depending on Flask for error reporting
    def handler(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        
        html = f"""
        <html>
            <head><title>Startup Error</title></head>
            <body style="font-family: monospace; padding: 20px;">
                <h1 style="color: red;">Application Startup Error</h1>
                <p>The Python application failed to import.</p>
                <div style="background: #f0f0f0; padding: 15px; border-radius: 5px; overflow-x: auto;">
                    <pre>{error_trace}</pre>
                </div>
            </body>
        </html>
        """
        return [html.encode('utf-8')]

