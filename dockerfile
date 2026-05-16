# Use the official lightweight Python image
FROM python:3.11-slim

# Copy local code to the container image
WORKDIR /app
COPY . .

# Install production dependencies
RUN pip install fastapi uvicorn

# Run the web service on container startup
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]