FROM python:3.10.11

WORKDIR /app

# Copy the poetry.lock and poetry.toml files to the container
COPY pyproject.toml poetry.lock /app/

# Install poetry
RUN pip install poetry

# Generate requirements.txt from poetry.lock
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of your project files to the container
COPY . /app/

EXPOSE 8000

CMD python3 -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
