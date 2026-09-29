# Leboncoin Deal Finder — mode local

Cette version est entièrement locale et rule-based : **pas de Gmail, pas d'IA, pas de Telegram et pas de dépendance externe**.

Le workflow GitHub Actions lit les annonces placées dans `data/input_ads.json`, applique les règles de prix, distance, mots-clés et risque, puis ajoute les bonnes affaires à `data/good_deals.md`. Il conserve les annonces déjà traitées dans `data/state.json`.

## Fonctionnement

```text
data/input_ads.json
        ↓
filtre prix + distance + mots-clés + risques
        ↓
data/good_deals.md
        ↓
commit automatique GitHub
```

Le workflow se lance toutes les six heures ou manuellement depuis l'onglet **Actions**. Il n'utilise aucun secret.

## Ajouter une annonce à analyser

Modifier `data/input_ads.json` :

```json
[
  {
    "title": "iPhone 14 128 Go",
    "url": "https://www.leboncoin.fr/ad/...",
    "price_eur": 280,
    "location": "Paris 75001",
    "latitude": 48.8666,
    "longitude": 2.3522,
    "description": "Très bon état, facture disponible, remise en main propre.",
    "published_at": "2026-09-29T10:00:00Z",
    "image_urls": [],
    "source_search": "iPhone 14 128 Go"
  }
]
```

Une bonne affaire est ajoutée à `data/good_deals.md` avec le prix, la distance, le score, les signaux détectés, le lien et un brouillon de message au vendeur. Le message n'est jamais envoyé automatiquement.

## Configuration

Personnaliser `config/settings.json` à partir de `config/settings.example.json`. La configuration contient la localisation, le rayon de 50 km, les recherches, les prix maximum et les mots à rejeter. La section `ai` de l'ancien exemple n'est pas utilisée dans ce mode et peut être supprimée.

## Limitation importante

Sans Gmail, API autorisée ou autre source d'annonces, GitHub ne peut pas découvrir tout seul les nouvelles annonces publiées sur Leboncoin. Il analyse uniquement les annonces présentes dans `data/input_ads.json`. Il faut donc ajouter les annonces à ce fichier, ou réactiver ultérieurement une source d'alertes autorisée.

## Exécution locale

```bash
python -m src.main
```

Les tests utilisent uniquement Python standard et peuvent être exécutés avec :

```bash
python -m pytest -q
```
