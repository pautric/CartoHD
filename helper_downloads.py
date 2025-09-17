import requests
from pathlib import Path
import logging

def setup_logging():logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s",
    )

def download_links(file_path, output_dir="downloads"):
    """
    Télécharge tous les liens d'un fichier texte dans un sous-dossier dédié.

    Args:
        file_path (str): Le chemin vers le fichier .txt contenant les URLs.
        output_dir (str): Le dossier de base où les sous-dossiers seront créés.
    """
    # Crée un sous-dossier basé sur le nom du fichier d'entrée
    file_stem = Path(file_path).stem
    specific_output_dir = Path(output_dir) / file_stem
    specific_output_dir.mkdir(parents=True, exist_ok=True)

    with open(file_path, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]

    for i, url in enumerate(links, start=1):
        try:
            logging.info(f"Téléchargement {i}/{len(links)} : {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Récupère le nom de fichier depuis l’URL (ou crée un nom générique)
            filename = url.split("/")[-1]
            if not filename:
                filename = f"file_{i}"

            filepath = specific_output_dir / filename

            # Écrit le contenu dans un fichier
            with open(filepath, "wb") as f_out:
                for chunk in response.iter_content(chunk_size=8192):
                    f_out.write(chunk)

            logging.info(f"✔ Fichier sauvegardé : {filepath}")

        except Exception as e:
            logging.error(f"❌ Erreur avec {url} : {e}")


if __name__ == "__main__":
    # Exemple d’utilisation
    # Le script va maintenant créer un dossier "downloads/IGNF_MNS-LIDAR-HD"
    # et y placer tous les fichiers téléchargés depuis ce .txt.
    input_file = "/Users/pautric/Downloads/IGNF_NUAGES-DE-POINTS-LIDAR-HD.txt"
    base_download_folder = "downloads"
    
    setup_logging()
    
    logging.info(f"Traitement du fichier de liens : {input_file}")
    download_links(input_file, output_dir=base_download_folder)
    logging.info(f"Téléchargements terminés dans le dossier '{Path(base_download_folder) / Path(input_file).stem}'")