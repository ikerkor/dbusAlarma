import time
import datetime
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters
import main

# Define states
KENDU = 0


# Define handlers
async def kudeatu(update: Update, context: CallbackContext) -> int:

    jobs = context.job_queue.jobs()
    mezua = ""
    kontagailu = 1
    for job in jobs:
        if str(update.message.chat.id) in job.name:
            mezua += f"{kontagailu}.\U0001F514 {job.name.split(str(update.message.chat.id))[1]}\n"
            kontagailu += 1
    if mezua != "":
            await update.message.reply_text(mezua)
            await update.message.reply_text('Finkatutako alarma(k) borratu nahiez gero, idatzi "1", bestela, "0".')
    else:
        await update.message.reply_text("Ez duk alarmarik gordeta, txikito.")
        return ConversationHandler.END
    return KENDU

async def kendu(update: Update, context: CallbackContext) -> int:
    borratu = update.message.text
    if borratu == "1":
        jobs = context.job_queue.jobs()
        for job in jobs:
            if str(update.message.chat.id) in job.name:
                job.schedule_removal()
        await update.message.reply_text('Zure lanak zuzen kendu dira. Hurren arte!')
    else:
        await update.message.reply_text('Ederki. Lanik kendu gabe utziko dugu elkarrizketa. Hurren arte!')
    return ConversationHandler.END


async def utzi(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        'Aio! Hurrengora arte!'
    )
    return conv_handler.END

# Define conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('kudeatu', kudeatu)],
    states={
        KENDU: [MessageHandler(filters.TEXT & ~filters.COMMAND, kendu)]
    },
    fallbacks=[CommandHandler('utzi', utzi)]
)