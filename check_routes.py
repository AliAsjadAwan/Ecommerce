from main import app

print("Registered Routes:")
print("=" * 50)
for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        print(f"{list(route.methods)[0]:6} {route.path}")
