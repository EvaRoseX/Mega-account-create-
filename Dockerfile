# Python aur Playwright dono ke saath official image use kar rahe hain
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Sabhi files copy karein
COPY . /app

# Python packages install karein
RUN pip install --no-cache-dir -r requirements.txt

# Sirf chromium browser dependencies aur browser install karein
RUN playwright install chromium

CMD ["python", "main.py"]
