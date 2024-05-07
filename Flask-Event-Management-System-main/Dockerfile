# # Stage 1: Build
# # Use an official Python runtime as a parent image
# FROM python:3.10-slim as builder

# # Set environment varibles
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# # Set work directory
# WORKDIR /usr/src/app

# # Install dependencies
# RUN pip install --upgrade pip
# COPY ./requirements.txt /usr/src/app/requirements.txt
# RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


# # Stage 2: Final
# FROM python:3.10-slim
# RUN mkdir -p /home/app
# RUN groupadd app && useradd -g app app

# ENV HOME=/home/app
# ENV APP_HOME=/home/app/web
# RUN mkdir $APP_HOME
# WORKDIR $APP_HOME

# COPY --from=builder /usr/src/app/wheels /wheels
# COPY --from=builder /usr/src/app/requirements.txt .
# RUN pip install --no-cache /wheels/*
# COPY . $APP_HOME
# RUN chown -R app:app $APP_HOME
# USER app
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "run:app"]


# FROM python:3.10-slim
# ENV PYTHONUNBUFFERED=1
# WORKDIR /app
# COPY requirements.txt /app
# RUN pip install -r requirements.txt
# COPY . /app
# CMD ["python3", "/app/run.py", "--debug", "true", "--port", "5000"]

FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 5000 (assuming that's the port your Flask app runs on)
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "run.py"]
