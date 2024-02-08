FROM python:3.10

RUN pip install poetry==1.7.1

RUN mkdir backend
COPY backend/ ./backend 

WORKDIR /backend

RUN poetry install --no-root

ENV PATH=$PATH:"$(poetry env info --path)/bin"

EXPOSE 8080
CMD ["poetry", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
