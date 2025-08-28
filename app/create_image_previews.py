from PIL import Image, ImageFilter
import os

# Folder containing images
input_folder = "app/static/imgs/"  # change to your folder
# Placeholder size
placeholder_size = (50, 50)  # small size for fast loading

for filename in os.listdir(input_folder):
    if filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(input_folder, f"{'small-'+os.path.splitext(filename)[0]}.png")

        # Open image
        with Image.open(input_path) as img:
            # Resize
            img.thumbnail(placeholder_size)
            # Apply slight blur
            img = img.filter(ImageFilter.GaussianBlur(2))
            # Save as PNG
            img.save(output_path , format=img.format)
            print(f"Created placeholder: {output_path}")

print("All small placeholders created!")
