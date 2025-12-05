FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

# Build args
ARG GUILD_ID
ARG DISCORD_TOKEN
ARG APEX_API_KEY

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "bot_apex.py"]
