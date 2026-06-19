import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

images = [
    "https://images.unsplash.com/photo-1773332611522-06b86b48cbf1?w=900&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDF8MHxmZWF0dXJlZC1waG90b3MtZmVlZHwxfHx8ZW58MHx8fHx8",
    "https://plus.unsplash.com/premium_photo-1780691020752-213011fadb66?w=900&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxmZWF0dXJlZC1waG90b3MtZmVlZHwyfHx8ZW58MHx8fHx8",
    "https://images.unsplash.com/photo-1780552274457-b4d8da874f96?w=900&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxmZWF0dXJlZC1waG90b3MtZmVlZHwzfHx8ZW58MHx8fHx8",
    "https://images.unsplash.com/photo-1780656094819-b90e8d27fa15?w=900&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxmZWF0dXJlZC1waG90b3MtZmVlZHw0fHx8ZW58MHx8fHx8",
    "https://plus.unsplash.com/premium_photo-1781215910967-7c7ab2e8cada?w=900&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxmZWF0dXJlZC1waG90b3MtZmVlZHw2fHx8ZW58MHx8fHx8",
]

start = time.perf_counter()


# Function to download images.
def download_image(image):
    img_bytes = requests.get(image).content
    # Extract the photo ID from the URL (before the query parameters)
    image_name = image.split("/")[3].split("?")[0] + ".jpg"
    with open(f"./images/{image_name}", "wb") as img:
        img.write(img_bytes)
        print(f"The image {image_name} is downloaded")


with ThreadPoolExecutor() as executor:
    executor.map(download_image, images)

finish = time.perf_counter()

print(f"Total time taken to download all pics  {round(finish - start, 2)} sec")
