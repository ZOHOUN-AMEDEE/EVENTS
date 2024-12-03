Voici le contenu formaté en fichier Markdown prêt à être enregistré :

```markdown
# Projet réalisé avec Scrapy et Selenium

## Installation

1. Installer les bibliothèques nécessaires :
   ```bash
   pip install scrapy selenium
   ```

2. Télécharger le driver correspondant à votre navigateur et l'ajouter au `PATH`.

3. Remplacer le chemin du driver dans `middlewares.py`. Par exemple :
   ```python
   service = Service('C:/Users/DAVIDO LAPTOP/Downloads/chromedriver-win32/chromedriver.exe')
   ```

## Exécution

Exécuter le fichier `events_spiders.py` avec les commandes suivantes :

- Pour obtenir un fichier JSON :
  ```bash
  scrapy crawl events -o events.json
  ```

- Pour obtenir un fichier CSV :
  ```bash
  scrapy crawl events -o events.csv
  ```
```

