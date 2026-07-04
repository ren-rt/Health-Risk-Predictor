FROM python:3.11-slim

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from solcx import install_solc; install_solc('0.8.19')"

COPY . .

EXPOSE 5000

CMD ["python", "app/app.py"]