import telebot

token = "5775482246:AAFoL2J2e2MGUBNvkkwE28vScOcmtIW7XV4"

bot = telebot.TeleBot(token=token)
types = telebot.types;

admins = [831107251]

emojies = {
    ':heart:': '❤',
    ':makaka:': '🙊',
}

def replaceEmojies(message):
    for key in emojies:
        message = str(message).replace(key,emojies[key])
    return message;
@bot.message_handler()
def reply(message):
    id = message.chat.id
    if(admins.__contains__(id)):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Open google", url="https://google.com"))
        bot.send_message(id, replaceEmojies(":heart: :makaka: test"), reply_markup=markup)
    else:
        bot.send_message(id, "Бот временно недоступен ;(")

bot.infinity_polling()