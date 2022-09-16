import json
import urllib
import requests
import telebot
import ast
import datetime

token = ""
api_token = ""

bot = telebot.TeleBot(token=token)
types = telebot.types;

admins = [831107251,731335768]

search = types.InlineKeyboardMarkup()
search.add(types.InlineKeyboardButton("🔎 Поиск фильма", callback_data="search"))

mainmenu = types.ReplyKeyboardMarkup(resize_keyboard=True)
mainmenu.add(types.KeyboardButton("Посоветуйте мне фильм"))

useractions = {}
temp = {}

genres = {
    "boevik": "боевик",
    "fentezi": "фэнтези",
    "fantastika": "фантастика",
    "triller": "триллер",
    "voennyj": "военный",
    "detektiv": "детектив",
    "komediya": "комедия",
    "drama": "драма",
    "uzhasy": "ужасы",
    "kriminal": "криминал",
    "melodrama": "мелодрама",
    "vestern": "вестерн",
    "biografiya": "биография",
    "anime": "аниме",
    "detskij": "детский",
    "multfilm": "мультфильм",
    "film-nuar": "фильм-нуар",
    "dlya-vzroslyh": "для взрослых",
    "dokumentalnyj": "документальный",
    "igra": "игра",
    "istoriya": "история",
    "koncert": "концерт",
    "korotkometrazhka": "короткометражка",
    "muzyka": "музыка",
    "myuzikl": "мюзикл",
    "novosti": "новости",
    "priklyucheniya": "приключения",
    "realnoe-tv": "реальное ТВ",
    "semejnyj": "семейный",
    "sport": "спорт",
    "tok-shou": "ток-шоу",
    "ceremoniya": "церемония",
}

mounths = {
    1: 'января',
    2: 'февраля',
    3: 'марта',
    4: 'апреля',
    5: 'мая',
    6: 'июня',
    7: 'июля',
    8: 'августа',
    9: 'сентября',
    10: 'октября',
    11: 'ноября',
    12: 'декабря'
}
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
                raw_request = requests.get("https://api.kinopoisk.dev/movie",
                                           params={'token': api_token,
                                                   'search': str(text),
                                                   'page': 1,
                                                   'field': "name",
                                                   'limit': 25,
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
                            if name == None: name = str(film['alternativeName']) + " (англ.)";
                            markup.add(types.InlineKeyboardButton(str(name) + " (" + str(film['year']) + ")",
                                                                  callback_data="f:" + str(film['id'])))
                        bot.send_message(id, "Найдено по вашему запросу", reply_markup=markup)
                else:
                    bot.send_message(id, "Ошибка. Разработчики бота уже уведомлены.")
                    for admin in admins:
                        bot.send_message(admin,
                                         "Ошибка выполнения запроса для пользователя " + str(
                                             id) + ": Status code " + str(
                                             raw_request.status_code))
                useractions.pop(id)
        elif(text.__eq__("/start")):
            bot.send_message(id, "Добро пожаловать в FilmBot. Это бот, который позволяет вам искать свежие фильмы, а также советует вам, что посмотреть.\n Идентификатор "+str(id), reply_markup=mainmenu)
            bot.send_message(id, "Меню бота", reply_markup=search)
        elif(text.__eq__("Посоветуйте мне фильм")):
            markup = types.InlineKeyboardMarkup(row_width=1)
            for key in genres:
                markup.row(types.InlineKeyboardButton(genres[key], callback_data="sf:"+key))
            bot.send_message(id, "Выберите жанр", reply_markup=markup)
        else:
            bot.send_message(id, "Меню бота", reply_markup=search)
    else:
        bot.send_message(id, "Бот временно недоступен ;(\n"+str(id))

@bot.callback_query_handler(func=lambda call: True)
def query(call):
    id = call.from_user.id
    data = call.data
    if (data == "search"):
        bot.send_message(id, "Введите название фильма, который вас интересует")
        useractions[id] = 'search'
        bot.answer_callback_query(call.id, "Введите название фильма, который вас интересует")

    elif (str(data).startswith("t:")):
        data = data[-(len(data) - 2)::]
        raw_request = requests.get("https://api.kinopoisk.dev/movie",
                                   params={'token': api_token,
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
                message = ""
                film_data = json.loads(raw_request.text)
                if(film_data['videos']['trailers'] != None and len(film_data['videos']['trailers']) > 0):
                    markup = types.InlineKeyboardMarkup()
                    trailers = film_data['videos']['trailers']
                    i = 0
                    for trailer in trailers:
                        if(str(trailer['site']).__eq__("youtube")):
                            print(str(trailer))
                            markup.add(types.InlineKeyboardButton(trailer['name'], url=trailer['url']))
                            i = i + 1
                            if (i >= 35):
                                break
                    if(film_data['name'] != None):
                        bot.send_message(id, "Трейлеры к фильму " + str(film_data['name']), reply_markup=markup)
                    else:
                        bot.send_message(id, "Трейлеры к фильму " + str(film_data['alternativeName'])+" (англ.)", reply_markup=markup)
                else:
                    bot.send_message(id, "Не удалось найти трейлеры к этому фильму :(")
        else:
            bot.send_message(id, "Не удалось найти фильм.")
    elif(str(data).startswith("f:")):
        data = data[-(len(data)-2)::]
        raw_request = requests.get("https://api.kinopoisk.dev/movie",
                                   params={'token': api_token,
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
                message = ""
                film_data = json.loads(raw_request.text)
                if film_data['name'] == None:
                    message = message+film_data["alternativeName"] + " (англ)\n";
                else:
                    message = message+film_data['name']+"\n"
                if(film_data['genres'] != None and len(film_data['genres']) > 0):
                    for genre in film_data['genres']:
                        message = message + (str(str(genre['name'])[0]).upper()+str(genre['name'][1:len(genre['name'])])) + " "
                    message = message + "\n\n"
                rating = film_data['rating']
                message = message + "🏅 Кинопоиск "+str(rating['kp'])+" | IMDB "+str(rating['imdb']) + "\n"
                votes = film_data['votes']
                message = message + "Голоса Кинопоиск " + str(votes['kp']) + " | IMDB " + str(votes['imdb']) + "\n";
                if film_data['description'] != None:
                    message = message + "\n" + str(film_data['description']) + "\n"
                if film_data['movieLength'] != None:
                    message = message + "\n⏱ Продолжительность " + str(film_data['movieLength']) + " минут\n"

                if(film_data['premiere'] != None):
                    if(film_data['premiere'].__contains__('country')):
                        if(film_data['premiere'].__contains__('world')):
                            date = str(film_data['premiere']['world'])
                            date_array = date.split("T")[0].split("-")
                            date = str(date_array[2])+" "+str(mounths[int(date_array[1])])+" "+str(date_array[0])+" года"
                            message = message+"\n\nПремьера "+date+"\n"

                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("Кинопоиск",
                                               url="https://www.kinopoisk.ru/film/" + str(
                                                   film_data['id'])),
                    types.InlineKeyboardButton("IMDB",
                                               url="https://www.imdb.com/title/" + str(
                                                   film_data['externalId']['imdb'])))
                raw_trailers = {}
                if(film_data['videos']['trailers'] != None) and (len(film_data['videos']['trailers']) > 0):
                    markup.add(types.InlineKeyboardButton("Трейлеры, тизеры", callback_data="t:"+str(film_data['id'])))
                if (film_data['poster'] != None and film_data['poster']['url'] != None):
                    bot.send_photo(id, urllib.request.urlopen(film_data['poster']['url']).read())
                markup.add(types.InlineKeyboardButton("🔎 Искать ещё", callback_data='search'))
                bot.send_message(id, message,
                                 reply_markup=markup)
        else:
            bot.send_message(id, "Не удалось найти фильм.")
    elif (str(data).startswith("sf:")):
        data = data[-(len(data) - 3)::]
        print(data)
        if(genres.__contains__(data)):
            raw_request = requests.get("https://api.kinopoisk.dev/movie",
                                       params={'token': api_token,
                                               'search': str(genres[data]),
                                               'page': 1,
                                               'field': "genres.name",
                                               'limit': 1,
                                               'sortField[]': 'votes.kp',
                                               'sortField[]': 'premiere.world',
                                               'sortType[]': -1,
                                               'sortType[]': -1,
                                               'isStrict': 'false'
                                               }
                                       )

            print(raw_request.text)
            message = ""
            film_data = json.loads(raw_request.text)
            if not film_data.__contains__('name') or film_data['name'] == None:
                message = message + film_data["alternativeName"] + " (англ)\n";
            else:
                message = message + film_data['name'] + "\n"
            if (film_data['genres'] != None and len(film_data['genres']) > 0):
                for genre in film_data['genres']:
                    message = message + (
                                str(str(genre['name'])[0]).upper() + str(genre['name'][1:len(genre['name'])])) + " "
                message = message + "\n\n"
            rating = film_data['rating']
            message = message + "🏅 Кинопоиск " + str(rating['kp']) + " | IMDB " + str(rating['imdb']) + "\n"
            votes = film_data['votes']
            message = message + "Голоса Кинопоиск " + str(votes['kp']) + " | IMDB " + str(votes['imdb']) + "\n";
            if film_data['description'] != None:
                message = message + "\n" + str(film_data['description']) + "\n"
            if film_data['movieLength'] != None:
                message = message + "\n⏱ Продолжительность " + str(film_data['movieLength']) + " минут\n"

            if (film_data['premiere'] != None):
                if (film_data['premiere'].__contains__('country')):
                    if (film_data['premiere'].__contains__('world')):
                        date = str(film_data['premiere']['world'])
                        date_array = date.split("T")[0].split("-")
                        date = str(date_array[2]) + " " + str(mounths[int(date_array[1])]) + " " + str(
                            date_array[0]) + " года"
                        message = message + "\n\nПремьера " + date + "\n"

            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("Кинопоиск",
                                           url="https://www.kinopoisk.ru/film/" + str(
                                               film_data['id'])),
                types.InlineKeyboardButton("IMDB",
                                           url="https://www.imdb.com/title/" + str(
                                               film_data['externalId']['imdb'])))
            raw_trailers = {}
            if (film_data['videos']['trailers'] != None) and (len(film_data['videos']['trailers']) > 0):
                markup.add(types.InlineKeyboardButton("Трейлеры, тизеры", callback_data="t:" + str(film_data['id'])))
            if (film_data['poster'] != None and film_data['poster']['url'] != None):
                bot.send_photo(id, urllib.request.urlopen(film_data['poster']['url']).read())
            markup.add(types.InlineKeyboardButton("🔎 Искать ещё", callback_data='search'))
            bot.send_message(id, message,
                             reply_markup=markup)
        else:
            bot.send_message(id, "Ошибка. Нет такого жанра.")

bot.infinity_polling()