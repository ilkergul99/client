# Use an official Python 3.11 runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container to match your repository name
WORKDIR /usr/src/client

# Install necessary system libraries
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /usr/src/client
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the default command to use bash
CMD ["tail", "-f", "/dev/null"]
