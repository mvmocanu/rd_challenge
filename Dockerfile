# Stage 1: Base build stage
FROM python:3.13-slim AS builder
 
# Create the app directory
RUN mkdir /app
 
# Set the working directory
WORKDIR /app

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
# Upgrade pip and install dependencies
RUN pip install --upgrade pip 
 
# Copy the requirements file first (better caching)
COPY requirements.txt /app/
 
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
 
# Stage 2: Production stage
FROM python:3.13-slim
 
RUN apt-get update && \
    apt-get install -y libpq-dev postgresql-client vim gcc build-essential curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -o /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh
 
RUN useradd -m -r appuser && \
   mkdir /app && \
   chown -R appuser /app
 
# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
 
# Set the working directory
WORKDIR /app
 
# Copy application code
COPY --chown=appuser:appuser . .
 
# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
# Switch to non-root user
USER appuser

ENV PATH="/app/src:$PATH"

RUN pip install -e .

# Expose the application port
EXPOSE 8000 

# collectstatic
RUN python manage.py collectstatic --noinput || true
 
# Start the application using Gunicorn
CMD ["gunicorn", "--chdir", "src", "--bind", "0.0.0.0:8000", "--workers", "1", "rd_project.wsgi:application", "--reload"]

