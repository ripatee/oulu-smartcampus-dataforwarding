FROM python:3.9-alpine

WORKDIR /var/df

COPY dataforwarding/ /usr/src/df/dataforwarding/
COPY test-assets/ /var/df/test-assets/

COPY main.py /usr/src/df
COPY test.py /usr/src/df

COPY requirements.txt /var/df


# you can mount config with:
# --volume settings.conf:/var/df/settings.conf:ro

RUN pip install --no-cache-dir -r requirements.txt

RUN python /usr/src/df/test.py

CMD ["python", "/usr/src/df/main.py"]