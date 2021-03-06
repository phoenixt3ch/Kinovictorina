from quiz import db, loginManager
from flask_login import UserMixin

db.create_all()


@loginManager.user_loader
def loadUser(userID):
    return UserInfo.query.get(int(userID))


class UserInfo(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    recentScore = db.Column(db.Integer, default=0)
    referralCode = db.Column(db.String(5), unique=True, nullable=False)

    def __repr__(self):
        return f"'UserInfo('{self.username}','{self.email}','{self.password}','{self.recentScore}','{self.referralCode}')'"


class Questions(db.Model):
    qid = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(100), nullable=False)
    choice1 = db.Column(db.String(100), nullable=False)
    choice2 = db.Column(db.String(100), nullable=False)
    choice3 = db.Column(db.String(100), nullable=True, default=None)
    choice4 = db.Column(db.String(100), nullable=True, default=None)
    correctAnswer = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"'questions('{self.qid}',''{self.question}','{self.choice1}','{self.choice2}','{self.choice3}','{self.choice4}','{self.correctAnswer}')'"


class MoviesDB(db.Model):
    movieID = db.Column(db.Integer, primary_key=True)
    movieTitle = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    place = db.Column(db.String(100), nullable=True)
    starCast = db.Column(db.String(100), nullable=True)
    ratings = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"'MoviesDB('{self.movieID}',''{self.movieTitle}','{self.year}','{self.place}','{self.starCast}','{self.ratings}')'"
