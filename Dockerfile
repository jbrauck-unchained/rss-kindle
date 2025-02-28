# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies for Calibre
RUN apt-get update && apt-get install -y \
    wget \
    xz-utils \
    xdg-utils \
    libegl1 \
    libfontconfig1 \
    libgl1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libfreetype6 \
    libxkbcommon0 \
    libopengl0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Calibre using the tarball method
RUN mkdir -p /opt/calibre \
    && wget -nv -O- https://download.calibre-ebook.com/6.29.0/calibre-6.29.0-x86_64.txz | tar xJf - -C /opt/calibre \
    && ln -s /opt/calibre/calibre /usr/local/bin/calibre \
    && ln -s /opt/calibre/ebook-convert /usr/local/bin/ebook-convert

# Copy everything at once
COPY . .

# Install dependencies explicitly including uvicorn
RUN pip install --no-cache-dir fastapi uvicorn requests python-dotenv

# Make port 8765 available
EXPOSE 8765

# Use a direct command that doesn't rely on PATH
CMD ["/usr/local/bin/python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8765"]
