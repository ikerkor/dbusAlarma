import asyncio
import logging
from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application, Defaults
import datetime
import pytz
import settings, elkarrizketa, alarma_kudeaketa
import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler

from settings import GARAPEN

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

spain_tz = pytz.timezone('Europe/Madrid')

DEV_DIC = {"Geltokia": r"https://dbus.eus/parada/125-arri-berri-2/", "Linea": "24", "Noiztik": (datetime.datetime.now(spain_tz) + datetime.timedelta(minutes=1)).strftime('%H:%M'),
                         "Noiz": "70"}
scheduler1 = BackgroundScheduler()

def ping_self():

    webhook_url = settings.WEBHOOK_URL + "/" + settings.TELEGRAM_TOKEN  # replace with your actual webhook URL
    data = {"update_id": 123}
    headers = {"Content-Type": "application/json"}
    requests.post(webhook_url, headers=headers, data=json.dumps(data))

async def start(update: Update, context) -> None:
    """
    Bota nola erabili azaltzeko.
    """

    if GARAPEN == "1":
            finkatu_alarma(update, context, DEV_DIC)
    else:
        await update.message.reply_text("Kaixo! Erabili /gehitu dbus alarma bat ezartzeko eta /kudeatu zerrendatu eta kentzeko.")


async def begiratu(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    D-buseko webgunean autobusari failta zaiona begiratu eta Lan (job) lagungarriak sortuko ditu.
    :param context:
    :return:
    """
    dicAlarma_job = context.job.data

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        browser_context = await browser.new_context()
        page = await browser_context.new_page()
        await page.goto(dicAlarma_job["Geltokia"])
        await asyncio.sleep(4)  # Use non-blocking sleep function
        element = await page.query_selector("#consulta_horarios")  # Use await with query_selector
        dynamic_content = await element.text_content()  # Use await with text_content
        await browser.close()  # Use await with close

    if not dynamic_content or "min." not in dynamic_content or dicAlarma_job["Linea"] not in dynamic_content:  # Errore kudeaketa hobea
        raise(Exception)
    minutuak = dynamic_content.split(f"Linea {dicAlarma_job['Linea']}")[1].split("min.")[0][-3:-1]
    if int(minutuak) > int(dicAlarma_job["Noiz"]):
        context.job_queue.run_once(
            begiratu,
            int((int(minutuak)-int(dicAlarma_job["Noiz"]))/2*60), # TODO: irakurritako denbora2 > denbora1 bada kasorik ez
            name=str(context.job.chat_id)+context.job.data["Geltokia"]+context.job.data["Linea"]
                         +context.job.data["Noiztik"]+context.job.data["Noiz"]+"_aux",
            data=context.job.data,
            chat_id=context.job.chat_id)
    else:
        text=f"🚏{dicAlarma_job['Geltokia'].split('/')[-2]}; {dicAlarma_job['Linea']} linea; {minutuak} min.; Badator... 🚌! 🏃‍♀️"
        await context.bot.send_message(context.job.chat_id, text=text)
    if GARAPEN == "1":
        await context.bot.send_message(context.job.chat_id, text=minutuak)
    # Pausatu biziberritzea beste lanik ez bada
    if context.job_queue.jobs() is None:
        if scheduler1.running:
            scheduler1.shutdown()

def finkatu_alarma(update: Update, context, data: dict) -> None:
    """
    Berariazko alarma lana gehkituko du lan-zerrendan.s
    :param update:
    :param context:
    :param data:
    :return:
    """
    if not scheduler1.running:
        scheduler1.start()

    chat_id = update.effective_message.chat_id

    context.job_queue.run_once(
        begiratu,
        datetime.time(int(data["Noiztik"][0:2]), int(data["Noiztik"][3:5])),
        data=data,
        name=str(chat_id)+data["Geltokia"]+data["Linea"]+data["Noiztik"]+data["Noiz"],
        chat_id=chat_id,
    )
    pass

def main() -> None:
    """Run the bot."""
    # Berezkoak sortu
    defaults = Defaults(
        tzinfo=spain_tz,
        disable_web_page_preview=True
    )
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token(settings.TELEGRAM_TOKEN)
        .defaults(defaults)
        .build()
    )
    # Dbus alarma finktatzeko elkarrizketa kudeatzailea sortu eta gehitu.
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(elkarrizketa.conv_handler)
    application.add_handler(alarma_kudeaketa.conv_handler)

    # Bizirik jarraitzeko lana gehitu
    scheduler1.add_job(id='biziberritu', func=ping_self, trigger='interval', seconds=14*60)
    scheduler1.start()

    # Hasi bot-a polling ala webhook bidez
    if settings.WEBHOOK == "0":
        settings.logger.info("Polling bidez exekutatuta")
        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    elif settings.WEBHOOK == "1":
        settings.logger.info("Webhook bidez exekutatuta")
        application.run_webhook(listen="0.0.0.0",
                              port=int(settings.PORT),
                              url_path=settings.TELEGRAM_TOKEN,
                              webhook_url=settings.WEBHOOK_URL + "/" + settings.TELEGRAM_TOKEN)


if __name__ == '__main__':
    main()