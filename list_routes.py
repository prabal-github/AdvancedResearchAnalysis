from app import app

def list_all_routes():
    """List all registered routes in the Flask app"""
    print("🔍 All Registered Routes")
    print("=" * 50)
    
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'route': rule.rule
        })
    
    # Sort by route
    routes.sort(key=lambda x: x['route'])
    
    analyst_routes = []
    other_routes = []
    
    for route in routes:
        if 'analyst' in route['route'].lower() or 'analyst' in route['endpoint'].lower():
            analyst_routes.append(route)
        else:
            other_routes.append(route)
    
    print("📊 ANALYST ROUTES:")
    print("-" * 30)
    for route in analyst_routes:
        methods = [m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']]
        print(f"  {route['route']:<30} {methods} → {route['endpoint']}")
    
    print("\n📋 ALL OTHER ROUTES (first 20):")
    print("-" * 30)
    for i, route in enumerate(other_routes[:20]):
        methods = [m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']]
        print(f"  {route['route']:<30} {methods} → {route['endpoint']}")
    
    print(f"\n📈 Total routes: {len(routes)}")
    print(f"📈 Analyst routes: {len(analyst_routes)}")

if __name__ == "__main__":
    list_all_routes()
