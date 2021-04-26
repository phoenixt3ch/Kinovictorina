""" Утилиты БД """

import re
import requests
from bs4 import BeautifulSoup
import random

from quiz import db
from quiz.Models import UserInfo, MoviesDB, Questions

from quiz.utils.Utils import generatePasswordHash


def adminCheck():
    """
    Проверяет наличие админа в БД, если нет добавляет админа в БД
    """

    if UserInfo.query.filter_by(username="admin").first() == None:
        adminUser = UserInfo(username="admin", password=generatePasswordHash(
            "admin"), email="admin@admin.com", referralCode="admin")
        try:
            db.session.add(adminUser)
            db.session.commit()
        except:
            db.rollback()


def loadIMDBData():
    """
    Проверяет наличие админа в БД, если нет добавляет админа в БД
    """

    url = 'http://www.imdb.com/chart/top'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    movies = soup.select('td.titleColumn')
    links = [a.attrs.get('href') for a in soup.select('td.titleColumn a')]
    crew = [a.attrs.get('title') for a in soup.select('td.titleColumn a')]
    ratings = [b.attrs.get('data-value')
               for b in soup.select('td.posterColumn span[name=ir]')]
    votes = [b.attrs.get('data-value')
             for b in soup.select('td.ratingColumn strong')]

    imdb = []

    for index in range(0, len(movies)):
        movie_string = movies[index].get_text()
        movie = (' '.join(movie_string.split()).replace('.', ''))
        movie_title = movie[len(str(index)) + 1:-7]
        year = re.search('\((.*?)\)', movie_string).group(1)
        place = movie[:len(str(index)) - (len(movie))]
        data = {"movie_title": movie_title,
                "year": year,
                "place": place,
                "star_cast": crew[index],
                "rating": ratings[index],
                "vote": votes[index],
                "link": links[index]}
        imdb.append(data)
    print(imdb)
    return imdb


def insertIMDBData(imdb):
    """
        Помещает данные с IMDB на локальную БД
    """
    for movieItem in imdb:
        movieObj = MoviesDB(movieTitle=movieItem["movie_title"], year=movieItem['year'],
                            place=movieItem["place"], starCast=movieItem["star_cast"], ratings=movieItem["rating"])
        db.session.add(movieObj)

    db.session.commit()


def generateIMDBQuizData():
    """
    Помещает данные с IMDB на локальную БД
    """

    Questions.query.delete()

    # Типы вопросов
    questionTypes = ["В каком году вышел фильм «{}»?",
                     "Кто снимался в фильме «{}»?"]

    for numberOfQuestions in range(1, 11):

        # Для разных типов вопросов
        qType = random.randint(0, 1)

        # Для первого типа вопросов
        if qType == 0:

            mid = MoviesDB.query.order_by(db.func.random()).first().movieID
            movieTitle = MoviesDB.query.filter_by(
                movieID=mid).first().movieTitle

            corrDate = MoviesDB.query.filter_by(movieID=mid).first().year

            question = questionTypes[qType].format(movieTitle)

            randomMovie1 = random.randint(1, 250)
            randomMovie2 = random.randint(1, 250)
            randomMovie3 = random.randint(1, 250)

            Choice1 = MoviesDB.query.filter_by(movieID=randomMovie1).first().year
            Choice2 = MoviesDB.query.filter_by(movieID=randomMovie2).first().year
            Choice3 = MoviesDB.query.filter_by(movieID=randomMovie3).first().year

            allChoicesList = [corrDate, Choice1, Choice2, Choice3]
            random.shuffle(allChoicesList)

            question = Questions(question=question, choice1=allChoicesList[0], choice2=allChoicesList[1],
                                 choice3=allChoicesList[2], choice4=allChoicesList[3], correctAnswer=corrDate)
            db.session.add(question)

        # Для второго типа вопросов
        elif qType == 1:

            mid = MoviesDB.query.order_by(db.func.random()).first().movieID
            movieTitle = MoviesDB.query.filter_by(
                movieID=mid).first().movieTitle

            corrStarCast = MoviesDB.query.filter_by(
                movieID=mid).first().starCast

            question = questionTypes[qType].format(movieTitle)

            randomMovie1 = random.randint(1, 250)
            randomMovie2 = random.randint(1, 250)
            randomMovie3 = random.randint(1, 250)

            Choice1 = MoviesDB.query.filter_by(movieID=randomMovie1).first().starCast
            Choice2 = MoviesDB.query.filter_by(movieID=randomMovie2).first().starCast
            Choice3 = MoviesDB.query.filter_by(movieID=randomMovie3).first().starCast

            allChoicesList = [corrStarCast, Choice1, Choice2, Choice3]
            random.shuffle(allChoicesList)

            question = Questions(question=question, choice1=allChoicesList[0], choice2=allChoicesList[1],
                                 choice3=allChoicesList[2], choice4=allChoicesList[3], correctAnswer=corrStarCast)
            db.session.add(question)

    # Сохранение последних изменений в БД
    db.session.commit()
