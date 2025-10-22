# import os
# import requests
# import random

# def fetch_online_wallpapers():
#     folder = "categories/online/"
#     os.makedirs(folder, exist_ok=True)

#     print("🌐 Fetching random wallpapers from Unsplash...")
#     urls = [
#         "https://source.unsplash.com/random/1920x1080?nature",
#         "https://source.unsplash.com/random/1920x1080?landscape",
#         "https://source.unsplash.com/random/1920x1080?city",
#     ]
#     url = random.choice(urls)
#     img_data = requests.get(url).content

#     filename = os.path.join(folder, f"online_{random.randint(100,999)}.jpg")
#     with open(filename, "wb") as f:
#         f.write(img_data)
#     print(f"✅ Downloaded: {filename}")


import requests
import os
import random

def fetch_online_wallpaper(category, save_folder, access_key):
    endpoint = "https://api.unsplash.com/photos/random"
    params = {
        "client_id": access_key,
        "query": category,
        "orientation": "landscape"
    }
    response = requests.get(endpoint, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        image_url = data["urls"]["full"]
        ext = os.path.splitext(image_url)[1].split("?")[0]
        filename = f"online_{category}_{random.randint(1000,9999)}{ext}"
        filepath = os.path.join(save_folder, filename)
        img_data = requests.get(image_url, timeout=10).content
        with open(filepath, "wb") as f:
            f.write(img_data)
        return filepath
    else:
        print(f"⚠️ Unsplash API returned status: {response.status_code}")
        return ""
