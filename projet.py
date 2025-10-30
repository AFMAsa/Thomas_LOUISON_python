# THOMAS LOUISON B2CS2
import sys
import os
import requests
import pandas as pd
from scrapy import Selector

BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = "https://books.toscrape.com/catalogue/"
CSV_DIR = "csv"  # dossier de sauvegarde des CSV
IMG_DIR = "images"  # dossier principal de sauvegarde des images


def get_cate():
    #Récupère toutes les URL de catégories.
    r = requests.get(BASE_URL)
    s = Selector(text=r.text)
    # Chaque catégorie se trouve dans la balise <ul class="nav-list">
    # On cible les liens <a> qui contiennent le nom et l'URL
    cats = s.css("ul.nav-list ul li a")

    categories = {}
    for cat in cats:
        name = cat.css("::text").get().strip().lower()
        href = cat.css("::attr(href)").get()
        full_url = BASE_URL + href
        categories[name.split()[0]] = full_url  # ex: "travel": "https://..."
    return categories


def scrape_book(book_url):
    #Scrape les infos d'un livre individuel.
    r = requests.get(book_url)
    s = Selector(text=r.text)

    title = s.css("h1::text").get()
    price = s.css(".price_color::text").get()[1:]
    availability = s.css(".availability::text").re_first(r"\d+")  # refirst chope le premier chiffre de avaibility puis complète avec le plus
    rating = s.css("p.star-rating::attr(class)").re_first("star-rating (\w+)")  # même idée mais avec les caractères par ex ça chope le F de five puis complète
    upc = s.css("table tr:nth-child(1) td::text").get()  # table tr:nth-child(1) → la première ligne du tableau

    # image relative -> on construit l'URL absolue à la main
    image_rel = s.css(".thumbnail img::attr(src)").get()
    image_url = "https://books.toscrape.com/" + image_rel.replace("../../", "")

    return {
        "title": title,
        "price": price,
        "availability": availability,
        "rating": rating,
        "upc": upc,
        "image_url": image_url,
        "book_url": book_url,
    }


def get_all_book_urls(category_url):
    #Récupère tous les liens de livres d'une catégorie, y compris les pages suivantes.
    urls = []
    while True:
        r = requests.get(category_url)
        s = Selector(text=r.text)
        relative_urls = s.css("h3 a::attr(href)").getall()
        urls += [CATALOGUE_URL + href.replace("../../../", "") for href in relative_urls]

        # Vérifie s'il existe une page suivante
        next_page = s.css("li.next a::attr(href)").get()
        if next_page:
            category_url = category_url.rsplit("/", 1)[0] + "/" + next_page
        else:
            break
    return urls


def scrape_category(category_name, category_url):
    """Scrape une catégorie complète, télécharge les images et sauvegarde le CSV dans le dossier csv/."""
    print(f"Catégorie : {category_name}")
    books = get_all_book_urls(category_url)
    print(f"→ {len(books)} livres trouvés")

    all_data = []

    # Crée les dossiers csv/ et images/ s'ils n'existent pas
    os.makedirs(CSV_DIR, exist_ok=True)
    category_img_dir = os.path.join(IMG_DIR, category_name)
    os.makedirs(category_img_dir, exist_ok=True)

    # Pour chaque livre, on scrape les infos et on télécharge l'image
    for book_url in books:
        data = scrape_book(book_url)
        all_data.append(data)

        # Nettoie le titre pour créer un nom de fichier valide
        safe_title = "".join(c for c in data["title"] if c.isalnum() or c in (" ", "_", "-")).rstrip()
        image_filename = safe_title[:50].replace(" ", "_") + ".jpg"
        image_path = os.path.join(category_img_dir, image_filename)

        # Téléchargement direct de l'image
        try:
            img = requests.get(data["image_url"], stream=True, timeout=10)
            if img.status_code == 200:
                with open(image_path, "wb") as f:
                    for chunk in img.iter_content(1024):
                        f.write(chunk)
        except Exception as e:
            print(f" Erreur téléchargement {data['image_url']} : {e}")

    # Enregistre les données dans un CSV
    df = pd.DataFrame(all_data)
    csv_path = os.path.join(CSV_DIR, f"{category_name}.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    print(f" {csv_path} sauvegardé.")
    print(f" Images enregistrées dans {category_img_dir}\n")


# EXÉCUTION DIRECTE DU SCRIPT 
categories = get_cate()
args = [arg.lower() for arg in sys.argv[1:]]

if not args:
    print(" Utilisation : python scrape_books.py [categorie1] [categorie2] ... ou 'all'")
    print(f"Catégories disponibles : {', '.join(categories.keys())}")
    sys.exit(1)

if "all" in args:
    print(f"{len(categories)} catégories trouvées !\n")
    for name, url in categories.items():
        scrape_category(name, url)
else:
    for arg in args:
        if arg in categories:
            scrape_category(arg, categories[arg])
        else:
            print(f" Catégorie '{arg}' introuvable. Ignorée.")


# Tout scraper :
# python scrape_books.py all

# Une ou plusieurs catégories :
# python scrape_books.py travel mystery philosophy

# Voir les catégories disponibles :
# python scrape_books.py
