from flask import render_template, flash, redirect, url_for, request
from quiz import app, db
from quiz.forms import LoginForm, RegistrationForm
from quiz.Models import UserInfo, Questions, MoviesDB
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import desc

from quiz.utils.DBUtils import adminCheck, loadIMDBData, insertIMDBData, generateIMDBQuizData
from quiz.utils.Utils import generatePasswordHash, checkPasswordHash, generateReferral, createFigure

import time

db.create_all()


@app.route("/", methods=["GET", "POST"])
def home():
    adminCheck()

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()

    if form.validate_on_submit():

        user = UserInfo.query.filter_by(username=form.username.data).first()

        if user and checkPasswordHash(user.password, form.password.data):
            login_user(user)
            loginPage = request.args.get("next")

            if loginPage:
                return redirect(loginPage)
            else:
                return redirect(url_for("dashboard"))
        else:
            flash("Неверные данные", "danger")

    return render_template('home.html', form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    adminCheck()

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashPassword = generatePasswordHash(form.password.data)
        userRegistrationDetails = UserInfo(
            username=form.username.data, password=hashPassword, email=form.email.data, referralCode=generateReferral())

        db.session.add(userRegistrationDetails)
        db.session.commit()

        flash("Вы зарегистрированы", "success")
        return redirect(url_for("home"))

    return render_template("registration.html", form=form)


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    timeStamp = time.time()

    scoreData = UserInfo.query.filter(
        id != "admin").with_entities(UserInfo.recentScore).all()
    scoreData = [temp[0] for temp in scoreData]
    createFigure(scoreData, timeStamp)

    # Кэширование IMDB
    if MoviesDB.query.first() == None:
        imdbRawDictionary = loadIMDBData()
        insertIMDBData(imdbRawDictionary)
        print("imdb load")

    maxScore = db.session.query(db.func.max(UserInfo.recentScore)).scalar()
    page = request.args.get("page", 1, type=int)
    # allUserDatas = UserInfo.query.filter(UserInfo.username != "admin").order_by(
    #     desc(UserInfo.recentScore)).paginate(page=page, per_page=5)
    allUserDatas = UserInfo.query.order_by(
        desc(UserInfo.recentScore)).paginate(page=page, per_page=5)

    return render_template("dashboard.html",
                           userDatas=allUserDatas, currentUser=current_user.username,
                           maxScore=maxScore, referralCode=current_user.referralCode,
                           pltUrl="/static/images/output{}.png".format(timeStamp))


@app.route("/takeQuiz", methods=["GET", "POST"])
@login_required
def takeQuiz():
    if request.method == "POST":

        tempScore = 0

        for selectedAnswerid in request.form:

            if request.form[selectedAnswerid] == str(
                    Questions.query.filter_by(qid=selectedAnswerid).first().correctAnswer):
                tempScore += 1

        if tempScore > current_user.recentScore:
            current_user.recentScore = tempScore
            db.session.commit()
            flash("Поздравляем! Вы набрали {} очков и это ваш лучший рекорд!".format(
                tempScore), "info")

        else:
            flash("Вы не побили предыдущий рекорд {} очков. Вы набрали {} очков.".format(
                current_user.recentScore, tempScore), "info")

        return redirect(url_for("dashboard"))

    generateIMDBQuizData()
    currentUser = current_user
    questionSets = Questions.query.order_by(db.func.random()).limit(10)

    return render_template("quizExam.html", recentScore=currentUser.recentScore, username=currentUser.username,
                           questions=questionSets)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))
