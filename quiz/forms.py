from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from quiz.Models import UserInfo


class LoginForm(FlaskForm):
    "Вход"

    username = StringField('Логин', validators=[
        DataRequired(), Length(min=2, max=100)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Вход")


class RegistrationForm(FlaskForm):
    "Регистрация"

    username = StringField('Логин', validators=[
        DataRequired(), Length(min=2, max=100)])
    email = StringField("Почта", validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[
        DataRequired(), Length(min=1, max=100)])
    confirmPassword = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo("password")])

    referralCode = StringField(
        'Введите пригласительный код', validators=[DataRequired(), Length(min=4, max=10)])

    submit = SubmitField("Регистрация")

    def validate_username(self, username):
        "Проверка занятости логина"

        user = UserInfo.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Логин занят")

    def validate_email(self, email):
        "Проверка занятости почты"

        email = UserInfo.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("Почта занята")

    def validate_referralCode(self, referralCode):
        "Проерка действительности пригласительного кода"

        referralCode = UserInfo.query.filter_by(referralCode=referralCode.data).first() == None
        if referralCode:
            raise ValidationError("Введите действительный пригласительный код")
