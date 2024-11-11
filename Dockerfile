# Choosing an image for you container.
from mcr.microsoft.com/playwright:v1.48.1-jammy
# Setting your working directory
WORKDIR /app
# This command would copy EVERY FILE from your project folder into your container, so be careful.
COPY . .
# Install Python 3.10 and pip
RUN apt-get update && apt-get install -y python3.10 python3-pip
# Installing needed packages and dependencies.**
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# This command basically executes your main file with Python.
CMD ["python3.10", "main.py"]
# EXPOSE 8443/tcp