"""Runner script for ResuMetrics local server.
Launches Uvicorn on localhost:8000 and opens default browser.
"""

import sys
import webbrowser
import threading
import time
import uvicorn

def open_browser():
    """Wait 1.5 seconds then open the local browser."""
    time.sleep(1.5)
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("=" * 60)
    print("  ResuMetrics | Minimalist Local Resume & ATS Analyzer")
    print("=" * 60)
    print("Starting local server on http://localhost:8000 ...")
    print("Press CTRL+C to stop.\n")

    # Open browser in a background daemon thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Launch uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
