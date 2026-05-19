FROM python3.12-slim

COPY ../requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . /app
CMD ["uvicorn", "main:app", "--host"]