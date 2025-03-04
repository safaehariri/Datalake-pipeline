import os


def get_latest_parquet_file(directory_path):
    # Liste tous les fichiers parquet dans le répertoire
    files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.parquet')]
    # Trie les fichiers par leur nom (supposant que le nom est un timestamp)
    latest_file = sorted(files)[-1]
    return latest_file

def process_files_in_directory(function ,raw_data_directory, directory,**kwargs):
    # Chemin vers le dossier raw dans le Data Lake

    raw_directory = f"{raw_data_directory}/{directory}"
    
    # Parcourir tous les fichiers dans le dossier raw
    for root, dirs, files in os.walk(raw_directory):
        for file in files:
            if file.endswith('.json'):
                # Construire le chemin complet du fichier JSON
                full_path = os.path.join(root, file)
                # Appeler la fonction pour convertir et sauvegarder le fichier
                function(full_path)