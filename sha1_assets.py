import os
import hashlib
import json

def get_file_sha1(file_path):
    """Funkcja do obliczania SHA1 dla pliku"""
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha1.update(chunk)
    return sha1.hexdigest()

def scan_assets_directory(directory):
    """Funkcja do przeszukiwania folderu assets i generowania biblioteki"""
    assets_data = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_sha1 = get_file_sha1(file_path)
            file_size = os.path.getsize(file_path)
            
            # Struktura folderów zaczynająca się od "/assets"
            relative_folder = os.path.relpath(root, directory).replace("\\", "/")  # Zamiana backslash na slash w ścieżkach
            if relative_folder == ".":
                relative_folder = ""  # Jeśli plik znajduje się bezpośrednio w folderze assets, ścieżka folderu jest pusta
            asset_data = {
                "dir": f"assets/{relative_folder}",
                "file": file,
                "sha1": file_sha1,
                "size": file_size
            }
            assets_data.append(asset_data)
    
    return assets_data

def save_assets_to_json(assets_data, output_file):
    """Funkcja zapisująca dane do pliku JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(assets_data, f, indent=4)

if __name__ == "__main__":
    assets_folder = 'assets'  # Folder, który chcesz przeszukać
    output_json_file = 'data/assets.json'  # Plik JSON, do którego zapisujesz wyniki (w folderze data)

    assets = scan_assets_directory(assets_folder)
    save_assets_to_json(assets, output_json_file)

    print(f"Zakończono generowanie pliku {output_json_file}")
