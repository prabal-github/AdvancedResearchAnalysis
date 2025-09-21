#!/usr/bin/env python3
"""
Simple test to verify async endpoint functionality.
"""

from flask import Flask, jsonify, request
import threading
import time
import secrets

app = Flask(__name__)

# Simple in-memory storage for async jobs
async_jobs = {}

@app.route('/test_async', methods=['POST'])
def test_async():
    """Test async endpoint."""
    # Generate job ID
    job_id = f"job_{int(time.time())}_{secrets.token_hex(6)}"
    
    # Store job info
    async_jobs[job_id] = {
        'status': 'running',
        'created_at': time.time(),
        'result': None,
        'error': None
    }
    
    # Start background thread
    def run_in_background():
        try:
            # Simulate work
            time.sleep(5)
            async_jobs[job_id]['status'] = 'completed'
            async_jobs[job_id]['result'] = {'message': 'Test completed successfully!'}
        except Exception as e:
            async_jobs[job_id]['status'] = 'failed'
            async_jobs[job_id]['error'] = str(e)
    
    thread = threading.Thread(target=run_in_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({'ok': True, 'job_id': job_id})

@app.route('/test_async/<job_id>', methods=['GET'])
def get_test_status(job_id):
    """Get status of async test job."""
    if job_id not in async_jobs:
        return jsonify({'ok': False, 'error': 'job not found'}), 404
    
    job = async_jobs[job_id]
    
    response = {
        'ok': True,
        'status': job['status']
    }
    
    if job['status'] == 'completed' and job['result']:
        response['result'] = job['result']
        # Clean up completed job
        del async_jobs[job_id]
    elif job['status'] == 'failed' and job['error']:
        response['error'] = job['error']
        # Clean up failed job
        del async_jobs[job_id]
    
    return jsonify(response)

if __name__ == '__main__':
    print("🧪 Testing Async API Implementation")
    print("Starting simple test server on port 5010...")
    app.run(debug=True, port=5010, host='127.0.0.1')
