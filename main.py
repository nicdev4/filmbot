import json
import urllib
import requests
import telebot
import ast
from kinopoisk.movie import Movie

token = ""

bot = telebot.TeleBot(token=token)
types = telebot.types;

admins = [831107251]

search = types.InlineKeyboardMarkup()
search.add(types.InlineKeyboardButton("Поиск фильма", callback_data="search"))

useractions = {}
temp = {}
def isInt(value):
    try:
        int(value)
        return True
    except:
        return False
@bot.message_handler()
def reply(message):
    id = message.chat.id
    text = str(message.text)
    if(admins.__contains__(id)):
        if(useractions.__contains__(id)):
            if(str(useractions[id]).__eq__("search")):
                temp[id] = text
                useractions[id] = "search.year"
                bot.send_message(id, "Введите год фильма или промежуток. Например: 2020 или 1990-2013")
            elif(str(useractions[id]).__eq__("search.year")):
                query = temp[id]
                raw_year = text
                if isInt(raw_year) or (len(raw_year.split("-", 2)) >= 2) and (isInt(raw_year.split("-", 2)[0] and isInt(raw_year.split("-", 2)[1]))):
                    raw_request = requests.get("https://api.kinopoisk.dev/movie",
                                               params={'token': '',
                                                       'search': str(query),
                                                       'page': 1,
                                                       'field': 'name',
                                                        'limit': 20,
                                                       'sortField[]': 'votes.kp',
                                                       'sortField[]': 'premiere.world',
                                                       'sortType[]': -1,
                                                       'sortType[]': -1,
                                                       'isStrict': 'false'
                                                       }
                                               )

                    print(raw_request.text)
                    if raw_request.status_code == 200:
                        print(raw_request.text)
                        if (raw_request.text.__eq__('{"docs":[],"total":0,"limit":1,"page":1,"pages":1}')):
                            bot.send_message(id, "По вашему запросу ничего не найдено.", reply_markup=search)
                        else:
                            film_data = json.loads(raw_request.text)['docs']
                            markup = types.InlineKeyboardMarkup()
                            for film in film_data:
                                name = film['name']
                                if name == None: name = str(film['alternativeName'])+" (англ.)";
                                markup.add(types.InlineKeyboardButton(str(name)+" ("+str(film['year'])+")", callback_data="f:"+str(film['id'])))
                            bot.send_message(id, "Найдено по вашему запросу", reply_markup=markup)
                    else:
                        bot.send_message(id, "Ошибка. Разработчики бота уже уведомлены.")
                        for admin in admins:
                            bot.send_message(admin,
                                             "Ошибка выполнения запроса для пользователя " + str(
                                                 id) + ": Status code " + str(
                                                 raw_request.status_code))
                    useractions.pop(id)
                    temp.pop(id)
                else:
                    bot.send_message(id, "Неверные года")
        elif(text.__eq__("/start")):
            bot.send_message(id, "Меню бота", reply_markup=search)
        else:
            movies = Movie.objects.search('Человек паук')
            if(len(movies) > 0):
                posters = movies[0].get_content('posters')
                bot.send_message(id, movies[0].title)
    else:
        bot.send_message(id, "Бот временно недоступен ;(")

@bot.callback_query_handler(func=lambda call: True)
def query(call):
    id = call.from_user.id
    data = call.data
    if (data == "search"):
        bot.send_message(id, "Введите название фильма, который вас интересует")
        useractions[id] = 'search'
        bot.answer_callback_query(call.id, "Введите название фильма, который вас интересует")
    elif(str(data).startswith("f:")):
        data = data[-(len(data)-2)::]
        raw_request = requests.get("https://api.kinopoisk.dev/movie",
                                   params={'token': '34SFDK9-M71MT5N-H9F4G77-AR9YTX8',
                                           'search': data,
                                           'field': 'id',
                                           'inStrict': 'true',
                                           'limit': '1'}
                                   )
        if raw_request.status_code == 200:
            if (raw_request.text.__eq__('{"docs":[],"total":0,"limit":1,"page":1,"pages":1}')):
                bot.send_message(id, "Не удалось открыть фильм ;(")
            else:
                print(raw_request.text)
                film_data = json.loads(raw_request.text)
                rating = film_data['rating']
                votes = film_data['votes']
                description = film_data['description']
                time = film_data['movieLength']
                if time == None:
                    minutes = 0
                    hours = 0
                else:
                    minutes = time
                    hours = 0
                    while minutes > 60:
                        minutes = minutes - 60
                        hours = hours + 1
                if (description == None): description = "";
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("Кинопоиск",
                                               url="https://www.kinopoisk.ru/film/" + str(
                                                   film_data['id'])),
                    types.InlineKeyboardButton("IMDB",
                                               url="https://www.imdb.com/title/" + str(
                                                   film_data['externalId']['imdb'])))
                markup.add(types.InlineKeyboardButton("Искать ещё", callback_data="search"))
                name = film_data['name']
                if name == None:
                    name = film_data["alternativeName"] + " (англ)";
                if (film_data['poster'] != None and film_data['poster']['url'] != None):
                    bot.send_photo(id, urllib.request.urlopen(film_data['poster']['url']).read())
                bot.send_message(id, "Фильм " + str(name) + " (" + str(
                    film_data['year']) + ")" +
                                 "\n" + str(hours) + " ч. " + str(minutes) + " мин." + " (" + str(
                    time) + ")" +
                                 "\n" + description +
                                 "\nОценки Кинопоиск " + str(rating['kp']) + " | IMDB " + str(
                    rating['imdb']) + "\n" +
                                 "\nГолоса Кинопоиск " + str(votes['kp']) + " | IMDB " + str(
                    votes['imdb']) + "\n",
                                 reply_markup=markup)
        else:
            bot.send_message(id, "Не удалось найти фильм.")


bot.infinity_polling()