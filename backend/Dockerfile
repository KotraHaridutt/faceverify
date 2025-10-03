# Start with a stable Python version
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install the system dependencies needed by OpenCV (this is the crucial step)
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 ffmpeg

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your backend application code into the container
COPY . .

# Expose the port the app will run on (Railway will use this)
EXPOSE 8000

# The start command is now handled by Railway's settings, but this is good practice
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]