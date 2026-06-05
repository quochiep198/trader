FROM python:3.10-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Create Hugging Face user (UID 1000)
RUN useradd -m -u 1000 user

# Set up working directory in home directory so the user has write access
WORKDIR /home/user/app

# Copy code
COPY . /home/user/app

# Recursively change ownership of home directory to user
RUN chown -R user:user /home/user

USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/home/user/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
