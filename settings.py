from dotenv import load_dotenv
import os
import logging

# Ingurune-aldagaiak zamatu, .env fitxategirik badago
load_dotenv()

##### Beharrezko ingurune aldagaiak

# Telegram bot TOKEN and my user
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_USER = os.environ.get('TELEGRAM_USER')

#Garapen, testing eta produkzio moduak bereizteko aldagaiak
GARAPEN = os.environ.get("GARAPEN")

## Webhook bidez egin nahi bada bete beharrezko ingurune aldagaiak

# Webhook bidez edo polling bidez ari garen jakiteko (bool, berez 0)
WEBHOOK = os.environ.get("WEBHOOK")

# Webhook url helbidea
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") # "https://zeplanbot.herokuapp.com/" Adibidea baino ez

# Set the port number to listen in for the webhook
PORT = int(os.environ.get('PORT', 8443))  # B4A-eko deploymentean ez da erabiltzen.


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
