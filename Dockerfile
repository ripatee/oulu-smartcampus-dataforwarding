FROM python:3.7-alpine

WORKDIR /var/df

COPY src/ /usr/src/df
COPY requirements.txt /var/df

# you can mount config with:
# --volume settings.conf:/var/df/settings.conf:ro

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "/usr/src/df/main.py"]