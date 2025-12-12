from app import create_app

app = create_app()
print("Map of rules:")
for rule in app.url_map.iter_rules():
    print(f"{rule} -> {rule.endpoint}")
