FROM python:3.12.2

RUN apt-get update && apt-get install -y gettext
RUN apt-get install -y libgl1

WORKDIR /app

COPY pyproject.toml pdm.lock* /app/

RUN pip install pdm
RUN pdm install

COPY . /app

EXPOSE 8080

CMD ["pdm", "run", "start"]
