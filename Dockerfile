FROM mcr.microsoft.com/playwright:v1.44.0-jammy

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

CMD ["python", "main.py"]
