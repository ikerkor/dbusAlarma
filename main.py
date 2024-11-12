import asyncio
import logging
from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import Updater, CommandHandler, ContextTypes, Application
import datetime
import pytz
import settings, elkarrizketa

from settings import GARAPEN

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

spain_tz = pytz.timezone('Europe/Madrid')

DEV_DIC = {"Geltokia": "361", "Linea": "38", "Noiztik": (datetime.datetime.now(spain_tz) + datetime.timedelta(minutes=1)).strftime('%H:%M'),
                         "Noiz": "9", "Errepikapena": "0"}
DEV_URL = r"https://dbus.eus/parada/129-herrera-2/"


async def ping_self():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(f"{settings.WEBHOOK_URL}:{settings.PORT}")
        await page.close()
        await browser.close()


async def start(update: Update, context) -> None:
    """
    Bota nola erabili azaltzeko.
    """

    if GARAPEN == "1":
            finkatu_alarma(update, context, DEV_DIC)
    else:
        await update.message.reply_text("Kaixo! Erabili /gehitu dbus alarma bat ezartzeko")


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def begiratu(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    D-buseko webgunean autobusari failta zaiona begiratu eta Lan (job) lagungarriak sortuko ditu.
    :param context:
    :return:
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        browser_context = await browser.new_context()
        page = await browser_context.new_page()
        await page.goto(DEV_URL)
        await asyncio.sleep(4)  # Use non-blocking sleep function
        element = await page.query_selector("#consulta_horarios")  # Use await with query_selector
        dynamic_content = await element.text_content()  # Use await with text_content
        await browser.close()  # Use await with close
    dicAlarma_job = context.job.data
    #try:
    if not dynamic_content or "min." not in dynamic_content or dicAlarma_job["Linea"] not in dynamic_content:  # Errore kudeaketa hobea
        raise(Exception)
    minutuak = dynamic_content.split(f"Linea {dicAlarma_job['Linea']}")[1].split("min.")[0][-3:-1]
    if int(minutuak) > int(dicAlarma_job["Noiz"]):
        context.job_queue.run_once(
            begiratu,
            int((int(minutuak)-int(dicAlarma_job["Noiz"]))/2*60), # TODO: irakurritako denbora2 > denbora1 bada kasorik ez
            name=str(context.job.chat_id)+context.job.data["Geltokia"]+context.job.data["Linea"]
                         +context.job.data["Noiztik"]+context.job.data["Noiz"]+context.job.data["Errepikapena"]+"_aux",
            data=context.job.data,
            chat_id=context.job.chat_id)
    else:
        await context.bot.send_message(context.job.chat_id, text="Alarmaa!!"+minutuak)
    #except:
    """
    await context.bot.send_message(context.job.chat_id, "Egiaztatu geltoki horretatik pasatzen dela adierazitako linea emandako ordutik"
                                   " gehienez ordubetera. Alarma ezeztatuta."+dynamic_content)
    remove_job_if_exists(str(context.job.chat_id)+context.job.data["Geltokia"]+context.job.data["Linea"]
                         +context.job.data["Noiztik"]+context.job.data["Noiz"]+context.job.data["Errepikapena"], context)"""
    if GARAPEN == "1":
        await context.bot.send_message(context.job.chat_id, text=minutuak)


def finkatu_alarma(update: Update, context, data: dict) -> None:
    """
    Berariazko alarma lana gehkituko du lan-zerrendan.s
    :param update:
    :param context:
    :param chat_id:
    :param data:
    :return:
    """
    # Prueba
    chat_id = update.effective_message.chat_id
    # context.job_queue.run_once(begiratu, int(data["Noiz"]), chat_id=chat_id)
    context.job_queue.run_daily(
        begiratu,
        datetime.time(int(data["Noiztik"][0:2]), int(data["Noiztik"][3:5]), tzinfo=spain_tz),
        (0, 1, 2, 3, 4, 5, 6),
        data=data,
        name=str(chat_id)+data["Geltokia"]+data["Linea"]+data["Noiztik"]+data["Noiz"]+data["Errepikapena"],
        chat_id=chat_id,
)

def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(settings.TELEGRAM_TOKEN).build()

    # Dbus alarma finktatzeko elkarrizketa kudeatzailea sortu eta gehitu.
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(elkarrizketa.conv_handler)

    # Bizirik jarraitzeko lana gehitu
    application.job_queue.run_repeating(ping_self, 2*60, name="biziberritu")

    # Hasi bot-a polling ala webhook bidez
    if settings.WEBHOOK == "0":
        settings.logger.info("Polling bidez exekutatuta")
        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    elif settings.WEBHOOK == "1":
        settings.logger.info("Webhook bidez exekutatuta")
        settings.logger.info("PORT: " + str(settings.PORT))
        settings.logger.info("TELEGRAM_USER: " + str(settings.TELEGRAM_USER))
        settings.logger.info("WEBHOOK_URL: " + str(settings.WEBHOOK_URL))
        application.run_webhook(listen="0.0.0.0",
                              port=int(settings.PORT),
                              url_path=settings.TELEGRAM_TOKEN,
                              webhook_url=settings.WEBHOOK_URL + "\\" + settings.TELEGRAM_TOKEN)


if __name__ == '__main__':
    main()