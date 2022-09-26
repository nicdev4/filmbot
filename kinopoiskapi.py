import requests

class KinopoiskAPI():
    def __init__(self, token):
        self.token = token

    def searchFilms(self, text):
        raw_request = requests.get("https://api.kinopoisk.dev/movie",
                                   params={'token': self.token,
                                           'search': str(text),
                                           'page': 1,
                                           'field': "name",
                                           'sortField[]': 'votes.kp',
                                           'sortField[]': 'premiere.world',
                                           'sortType[]': -1,
                                           'sortType[]': -1,
                                           'isStrict': 'false'
                                           }
                                   )
        if raw_request.status_code == 200:
            return raw_request
        else:
            return {}
    def getFilmByID(self, id):
        raw_request = requests.get("https://api.kinopoisk.dev/movie",
                                       params={'token': self.token,
                                               'search': id,
                                               'field': 'id',
                                               'inStrict': 'true',
                                               'limit': '1'}
                                       )
        if raw_request.status_code == 200:
            return raw_request
        else:
            return {}
    def getFilmsByGenres(self, genres = {}):
        requests.get("https://api.kinopoisk.dev/movie",
                     params={'token': self.token,
                             'search': str(genres),
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
