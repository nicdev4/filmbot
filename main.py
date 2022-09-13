import json
import urllib
import requests
import telebot
import ast


token = ""

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
        raw_request = requests.get("https://api.kinopoisk.dev/movie",
                                    params={'token': ' ',
                                            'search': '7-10',
                                            'field': 'rating.kp',
                                            'search': '2012-2022',
                                            'field': 'year',
                                            'inStrict': 'false',
                                            'limit': '1'}
                                   )
        film_data = json.loads(raw_request.text)['docs']
        rating = film_data[0]['rating']
        bot.send_photo(id, urllib.request.urlopen(film_data[0]['poster']['url']).read())
        bot.send_message(id, "Фильм "+str(film_data[0]['name'])+"\nОценки kinopoisk "+str(rating['kp'])+" | IMDB "+str(rating['imdb'])+"\n"+"",
                         reply_markup=markup)
    else:
        bot.send_message(id, "Бот временно недоступен ;(")

bot.infinity_polling()
