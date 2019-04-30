from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, \
    SubmitField, IntegerField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, Email, Length
from wtforms.widgets import TextArea


class LoginForm(FlaskForm):
    """Форма авторизации"""
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    """Форма регистрации"""
    user_name = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email адрес', validators=[DataRequired(), Email()])
    password_hash = PasswordField('Пароль', validators=[DataRequired()])
    confirm = PasswordField('Повторите пароль', validators=[DataRequired()])
    accept_tos = BooleanField('Я принимаю лицензионное соглашение',
                              validators=[DataRequired()])
    submit = SubmitField('Создать учетную запись')


class AddBookForm(FlaskForm):
    """Форма добавления книги"""
    name = StringField('Название книги', validators=[DataRequired()])
    author = StringField('Автор (ИФ)', validators=[DataRequired()])
    year = IntegerField('Год выпуска', validators=[DataRequired()])
    pages = IntegerField('Количество страниц', validators=[DataRequired()])
    pictures = FileField('Обложка', validators=[FileRequired()])
    bio = StringField(u'Описание', widget=TextArea(), validators=[DataRequired()])
    stock = IntegerField('Количество книг на складе', validators=[DataRequired()])
    price = IntegerField('Цена (руб)', validators=[DataRequired()])
    submit = SubmitField('Добавить книгу')


class AddCommentForm(FlaskForm):
    """Форма комментария книги"""
    name = StringField('Название рецензии', validators=[DataRequired()])
    date = StringField('Дата (дд-мм-гг)', validators=[DataRequired()])
    text = StringField(u'Рецензия', widget=TextArea(),
                       validators=[DataRequired()])
    submit = SubmitField('Добавить рецензию')


class AddAuthorForm(FlaskForm):
    """Форма автора"""
    name = StringField('Имя писателя', validators=[DataRequired()])
    picture = FileField('Фотография', validators=[FileRequired()])
    bio = StringField('Биография писателя', widget=TextArea(),
                      validators=[DataRequired()])
    submit = SubmitField('Добавить писателя')


class EditAuthorForm(FlaskForm):
    """Форма редактирования автора"""
    picture = FileField('Фотография')
    bio = StringField('Биография писателя', widget=TextArea())
    submit = SubmitField('Сохранить изменения')


class SearchForm(FlaskForm):
    """Форма поиска"""
    search = StringField('Название книги, ИФ писателя',
                         widget=TextArea(),
                         validators=[DataRequired(),
                                     Length(min=4, max=250)])
    submit = SubmitField('Поиск')
