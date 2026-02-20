FROM python:3.12-slim

WORKDIR /code

# Installation des dépendances
COPY ./backend/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# On copie le contenu du dossier backend directement dans /code
COPY ./backend /code/

# On expose le port
EXPOSE 8000

# FastAPI 'run' s'attend à recevoir le chemin du fichier par rapport au WORKDIR
# Si ton fichier s'appelle main.py et contient 'app = FastAPI()'
CMD ["fastapi", "run", "main.py", "--port", "8000"]