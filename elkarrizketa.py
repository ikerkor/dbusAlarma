import time
import datetime
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters

import main

# Aldagai globalak
GELTOKIA, LINEA, NOIZTIK, NOIZ = range(4)  # Elkarrizketa-egoera-makinako egoerak
dicAlarma = {}  # Sarrerak gordetzeko hiztegia (aldibereko erabiltzailea saiesteko, azpihiztegiak)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
async def gehitu(update: Update, context: CallbackContext) -> int:
    """
    Elkarrizketa hasi eta alarma berria sortzeko beharrezko datuak eskatuko dizkio
    """
    array = dicAlarma.get(update.message.chat.id)
    if not array:
        dicAlarma[update.message.chat.id] = []
    dicAlarma[update.message.chat.id].append({})
    time.sleep(0.5)
    await update.message.reply_text('Idatzi nahi duzun geltokiko iritsieren url-a. Adibidez, https://dbus.eus/parada/125-arri-berri-2/'
                                    ' . Bilatu QRa geltokian bertan, edo arakatu dbusen weborria (euskarazko bertsioan dabil bakarrik).')
    return GELTOKIA


async def geltokia (update: Update, context: CallbackContext) -> int:
    """
    Geltokia gorde eta zein linearen berri izan nahi duen galdetuko dio
    """
    stGeltokia = update.message.text
    dicAlarma[update.message.chat.id][-1]["Geltokia"] = stGeltokia
    time.sleep(0.5)
    await update.message.reply_text('Zein dbus linearen berri izan nahi duzu (zenbakia bakarrik)?')
    return LINEA


async def linea (update: Update, context: CallbackContext) -> int:
    """
    Linea gorde eta zein ordutatik aurrera egiaztatu nahi duen galdetuko dio
    """
    stLinea = update.message.text
    dicAlarma[update.message.chat.id][-1]["Linea"] = stLinea
    time.sleep(0.5)
    await update.message.reply_text('Zein ordutatik aurrera egiaztatu nahi duzu (hh:mm)?')
    return NOIZTIK


async def noiztik (update: Update, context: CallbackContext) -> int:
    """
    "Noiztik" gorde eta zenbat minutu lehenago jotzea nahi duen galdetuko dio
    """
    stNoiztik = update.message.text
    dicAlarma[update.message.chat.id][-1]["Noiztik"] = stNoiztik
    time.sleep(0.5)
    await update.message.reply_text('Zenbat minutu lehenago jotzea nahi duzu?')
    return NOIZ


async def noiz (update: Update, context: CallbackContext) -> int:
    """
    "Noiz" gorde eta konbertsazioa bukatuko da
    """
    stNoiz = update.message.text
    dicAlarma[update.message.chat.id][-1]["Noiz"] = stNoiz
    main.finkatu_alarma(update, context, dicAlarma[update.message.chat.id][-1])
    time.sleep(0.5)
    await update.message.reply_text('Xarmanki. Zure alarma zuzen gehitu da.')
    return ConversationHandler.END


async def utzi(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    del dicAlarma[update.message.chat.id][-1]
    await update.message.reply_text(
        'Aio! Hurrengora arte!'
    )
    return conv_handler.END


# Dbus alarma finkatzeko elkarrizketa kudeatzailea sortu
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('gehitu', gehitu)],
    states={
        GELTOKIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, geltokia)],
        LINEA: [MessageHandler(filters.TEXT & ~filters.COMMAND, linea)],
        NOIZTIK: [MessageHandler(filters.TEXT & ~filters.COMMAND, noiztik)],
        NOIZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, noiz)]
    },
    fallbacks=[CommandHandler('utzi', utzi)],
)