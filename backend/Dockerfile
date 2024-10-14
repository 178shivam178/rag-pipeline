FROM python:3.10.15-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3008
CMD ["python", "app.py"]
