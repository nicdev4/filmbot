import telebot

token = "5775482246:AAFoL2J2e2MGUBNvkkwE28vScOcmtIW7XV4"

bot = telebot.TeleBot(token=token)

@bot.message_handler()
def reply(message):
    id = message.chat.id
    bot.send_message(id, "test")

bot.infinity_polling()