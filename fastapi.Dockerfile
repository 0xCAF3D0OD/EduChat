FROM python:3.14

WORKDIR /code

COPY ./backend/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./backend /code/app

CMD ["fastapi", "run", "backend/main.py", "--port", "8000"]