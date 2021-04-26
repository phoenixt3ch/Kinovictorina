import os
import shutil
import random
from quiz import bcrypt
import numpy as np
import seaborn as sns


def generatePasswordHash(userPasswordPlain):
    """
    Возвращает хэш пароля
    """

    hashedPassword = bcrypt.generate_password_hash(
        userPasswordPlain).decode('utf-8')
    return hashedPassword


def checkPasswordHash(userHashedPassword, enteredPassword):
    """
    Проверка совпадения хэша и пароля
    """

    return bcrypt.check_password_hash(userHashedPassword, enteredPassword)


def generateReferral():
    """
    Создания пригласительного кода
    """

    charSet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    referralCode = ''
    for i in range(0, 5):
        subStart = random.randint(0, len(charSet) - 1)
        referralCode += charSet[subStart: subStart + 1]

    return referralCode


def createFigure(scoreData, timeStamp):
    """
    Создание графика со статистикой
    """

    # Удаление предыдущего графика, если он имеется
    for root, dirs, files in os.walk('quiz/static/images/'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

    xs = np.array(scoreData)
    snsplt = sns.countplot(x=xs)
    snsplt.figure.savefig("quiz/static/images/output{}.png".format(timeStamp))
