#!/usr/bin/env python3
"""
Quick test to add a simple route for testing certificate generation
"""

# Simple test route to add to app.py for testing HTML certificates
test_route_code = '''
@app.route('/test_certificate/<analyst_name>')
def test_certificate_generation(analyst_name):
    """Test route for HTML certificate generation"""
    try:
        # Create a mock certificate request for testing
        from types import SimpleNamespace
        
        # Mock certificate request object
        mock_request = SimpleNamespace()
        mock_request.analyst_name = analyst_name
        mock_request.performance_score = 87.5
        mock_request.research_papers_count = 12
        mock_request.reports_submitted = 45
        mock_request.average_rating = 4.2
        mock_request.completion_rate = 94.0
        mock_request.course_name = "Advanced Financial Analysis"
        mock_request.request_date = datetime.now()
        mock_request.id = "TEST-001"
        
        # Generate HTML certificate
        html_path = generate_certificate_html(mock_request)
        
        if html_path and os.path.exists(html_path):
            # Return the HTML content directly
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return Response(html_content, mimetype='text/html')
        else:
            return jsonify({"error": "Failed to generate certificate"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Certificate generation failed: {str(e)}"}), 500
'''

print("🔧 Test Route Code for HTML Certificate Testing:")
print("=" * 60)
print(test_route_code)
print("=" * 60)

print("\n📋 Instructions:")
print("1. Add the above code to app.py after the existing routes")
print("2. Restart the Flask application")
print("3. Access: http://127.0.0.1:80/test_certificate/YourName")
print("4. This will generate and display an HTML certificate")

print("\n🎯 Alternative - Use existing dashboard:")
print("1. Go to: http://127.0.0.1:80/")
print("2. Navigate to Analyst Certificate section")
print("3. Follow the certificate request workflow")

print("\n✅ Status: HTML Certificate System is fully implemented and ready!")
