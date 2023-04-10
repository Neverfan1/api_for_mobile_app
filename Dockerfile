FROM python:3.10.9-slim

WORKDIR /api-mobile

COPY ./requirements.txt /api-mobile/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /api-mobile/requirements.txt

COPY ./api /api-mobile/api
COPY ./api_settings /api-mobile/api_settings

CMD ["python", "api/manage.py", "runserver", "--host", "0.0.0.0", "--port", "80"]