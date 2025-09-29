#This script is just to move files that were scraped into the right folder
import os
import shutil

# Source and destination folders
source_folder = r"C:\Users\HP\Desktop\UI\important\Data Science\movie-success-prediction"
destination_folder = r"C:\Users\HP\Desktop\UI\important\Data Science\movie-success-prediction\data\raw"

# Ensure the destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# Loop through all files in the source folder
for filename in os.listdir(source_folder):
    if filename.endswith(".csv"):
        source_path = os.path.join(source_folder, filename)
        destination_path = os.path.join(destination_folder, filename)
        shutil.move(source_path, destination_path)
        print(f"Moved: {filename}")

print("All CSV files have been moved successfully!")
