FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

RUN useradd --create-home appuser

USER appuser

EXPOSE 5001

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5001"]