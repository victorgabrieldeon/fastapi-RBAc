FROM python:3.12.2


WORKDIR /app

COPY pyproject.toml pdm.lock* /app/

RUN pip install pdm
RUN pdm install

COPY . /app

EXPOSE 8000

CMD ["pdm", "start"]
