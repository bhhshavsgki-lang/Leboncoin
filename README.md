# Leboncoin Deal Finder

Moniteur personnel basé sur les alertes officielles Leboncoin. Il lit les nouvelles annonces reçues par e-mail, applique des filtres locaux, demande une analyse structurée à un modèle IA, mémorise les annonces déjà traitées et envoie une notification pour les opportunités intéressantes.

## Principe important

Le projet ne parcourt pas automatiquement les pages de recherche Leboncoin et ne contourne ni CAPTCHA ni protection. Il utilise les alertes/recherches configurées dans le compte Leboncoin. Le message au vendeur est généré comme **brouillon** ; l’utilisateur ouvre ensuite l’annonce et décide de l’envoyer.

## Fonctionnalités

- Plusieurs recherches et catégories configurables.
- Distance maximale de 50 km par défaut.
- Score déterministe : prix, ancienneté, distance, mots-clés et signaux de risque.
- Deuxième analyse IA avec sortie JSON stricte : adéquation, prix estimé, risque d’arnaque, qualité de l’annonce, urgence et recommandation.
- Mémoire persistante dans `data/state.json` : annonces vues, prix observés, décisions et brouillons.
- Déduplication par identifiant ou URL normalisée.
- Notifications Telegram ou webhook Discord.
- Le workflow GitHub se relance automatiquement toutes les six heures et sauvegarde l’état dans Git.
- Mode `DRY_RUN=1` pour tester sans envoyer de notification.

## Installation rapide

1. Copier `config/settings.example.json` vers `config/settings.json` et personnaliser les recherches.
2. Configurer les secrets GitHub :
   - `IMAP_HOST`, `IMAP_PORT`, `IMAP_USERNAME`, `IMAP_PASSWORD` ;
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` ou `DISCORD_WEBHOOK_URL` ;
   - `OPENAI_API_KEY` et éventuellement `OPENAI_API_BASE`.
3. Activer les alertes e-mail dans **Mes recherches** sur Leboncoin.
4. Tester localement avec `DRY_RUN=1 python -m src.main`.
5. Activer le workflow GitHub Actions.

Le modèle par défaut est `gpt-5-mini`, adapté à l’analyse structurée de nombreuses annonces. Pour les cas ambigus, `AI_ESCALATION_MODEL` peut être réglé sur `gpt-5`.

## Messages au vendeur

Pour chaque annonce retenue, le système crée un brouillon dans `data/state.json` avec une formulation polie et des questions utiles. Il ne se connecte pas au compte Leboncoin et n’envoie pas automatiquement le message. Cette séparation évite les messages involontaires et laisse le contrôle final à l’utilisateur.

## Limites

- Une alerte e-mail peut arriver avec retard.
- L’analyse IA est une aide à la décision, pas une garantie d’authenticité.
- Le prix de référence est calculé à partir de l’historique local et des valeurs fournies dans la configuration ; il devient meilleur après plusieurs exécutions.
- Il faut conserver les secrets uniquement dans GitHub Secrets, jamais dans le dépôt.
