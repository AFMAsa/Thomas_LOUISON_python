#  BooksToScrape - Web Scraper  
**Auteur : Thomas Louison - B2CS2**

Ce projet est un script Python permettant de **scraper automatiquement le site [Books to Scrape](https://books.toscrape.com/)**.  
Il récupère pour chaque livre :
- Le **titre**
- Le **prix**
- La **disponibilité**
- La **note**
- Le **code UPC**
- Le **lien du livre**
- L’**URL de l’image**

Le script sauvegarde :
- Un **fichier CSV par catégorie** (dans le dossier `/csv`)
- Les **images de chaque livre** (dans `/images/<nom_de_la_catégorie>/`)

---

##  Prérequis

Assure-toi d’avoir **Python 3.8+** installé, ainsi que les modules suivants :

```bash
pip install requests pandas scrapy
```

---

## Structure du projet
books_scraper/  
│  
├── scrape_books.py        # Script principal  
├── README.md              # Documentation du projet  
│  
├── csv/                   # Dossier contenant les fichiers CSV  
│   ├── travel.csv  
│   ├── mystery.csv  
│   └── ...  
│
└── images/                # Dossier contenant les images par catégorie  
    ├── travel/  
    │   ├── It's_Only_the_Himalayas.jpg  
    │   ├── Full_Moon_Over_Noah’s_Ark.jpg  
    └── mystery/  
        ├── In_the_Woods.jpg  
        ├── Gone_Girl.jpg  


---

## Utilisation
1️. Lancer le script pour toutes les catégories
python scrape_books.py all

2️. Lancer le script pour une ou plusieurs catégories précises
python scrape_books.py travel mystery philosophy

3️. Voir la liste des catégories disponibles
python scrape_books.py
