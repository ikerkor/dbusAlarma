import time
import datetime
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters
import main

# Define states
ZERRENDA, KENDU = range(2)


# Define handlers
async def kudeatu(update: Update, context: CallbackContext) -> int:

    jobs = context.job_queue.jobs()
    mezua = ""
    for i, job in enumerate(jobs):
        if str(update.message.chat.id) in job.name:
            mezua += f"{i}.\U0001F514 {job.name}\n"
    try:
        mezua = mezua[0:-2]
    except:
        pass
    await update.message.reply_text(mezua)
    return ZERRENDA

async def zerrenda(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Aukeratu zerrenda bat:')
    # Add logic to handle user input
    print(context.job_queue.jobs())
    return KENDU


async def kendu(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Aukeratu kendu nahi duzun elementua:')
    # Add logic to handle user input
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
        ZERRENDA: [MessageHandler(filters.TEXT & ~filters.COMMAND, zerrenda)],
        KENDU: [MessageHandler(filters.TEXT & ~filters.COMMAND, kendu)]
    },
    fallbacks=[CommandHandler('utzi', utzi)]
)