#!/usr/bin/env python3
"""Day 9: Model Serving API - FastAPI inference server for production."""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from deployment.inference_api import run_server


def main():
    """Main Day 9 execution: Start FastAPI inference server."""
    
    print("=" * 80)
    print("DAY 9: MODEL SERVING API - FASTAPI INFERENCE SERVER")
    print("=" * 80)
    
    print("\n📋 Configuration:")
    print("   Host: 127.0.0.1")
    print("   Port: 8000")
    print("   Environment: Development (reload enabled)")
    
    print("\n📚 API Documentation:")
    print("   Interactive Docs: http://127.0.0.1:8000/docs")
    print("   ReDoc: http://127.0.0.1:8000/redoc")
    
    print("\n🔌 Key Endpoints:")
    print("   GET  /health - Health check")
    print("   GET  /info - API information")
    print("   GET  /status - Server status")
    print("   POST /predict - Single prediction")
    print("   POST /predict/batch - Batch predictions")
    print("   GET  /metrics - Monitoring metrics")
    print("   GET  /monitoring/drift - Data drift check")
    print("   POST /monitoring/report - Save report")
    
    print("\n📝 Example Requests:")
    print("\n   1. Health Check:")
    print("      curl http://127.0.0.1:8000/health")
    
    print("\n   2. Single Prediction:")
    print('      curl -X POST http://127.0.0.1:8000/predict \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"features": [2.5, 10, 1]}\'')
    
    print("\n   3. Batch Predictions:")
    print('      curl -X POST http://127.0.0.1:8000/predict/batch \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"features": [[2.5, 10, 1], [5.0, 14, 2]]}\'')
    
    print("\n⚡ Quick Test:")
    print("   # In another terminal:")
    print("   python -c \"")
    print("   import requests")
    print("   r = requests.get('http://127.0.0.1:8000/health')")
    print("   print(r.json())")
    print("   \"")
    
    print("\n" + "=" * 80)
    print("🚀 STARTING SERVER...")
    print("=" * 80)
    print("\n⏳ Server initializing... Press CTRL+C to stop\n")
    
    try:
        # Run the FastAPI server
        run_server(host="127.0.0.1", port=8000, reload=True)
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("SERVER STOPPED")
        print("=" * 80)
        print("✅ Server shut down cleanly")
    
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
