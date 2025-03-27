FROM ghcr.io/railwayapp/nixpacks:ubuntu-1741046653

WORKDIR /app/

# Copy all files into the container
COPY . /app/.

# Install Python3 and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Change to the backend directory and install requirements
RUN cd backend && python3 -m pip install -r requirements.txt

# (Optional) Expose port or add further instructions if needed
