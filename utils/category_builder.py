import os

def add_new_category(name):
    folder = os.path.join("categories", name)
    os.makedirs(folder, exist_ok=True)
    print(f"🎨 New category '{name}' created at {folder}. Add wallpapers inside it!")
