

Gestion intelligente de patients & rendez-vous (Admin, Médecin, Patient).

## Démarrage rapide

```bash

python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt  
cp .env.example .env             # puis édite SECRET_KEY etc.
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
