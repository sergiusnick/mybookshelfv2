from flask import Flask, render_template, \
    session, redirect, flash, url_for
from forms import LoginForm, RegisterForm, AddBookForm, \
    AddCommentForm, AddAuthorForm, SearchForm, EditAuthorForm
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from models import UsersModel, BooksModel, AuthorsModel
from flask_sqlalchemy import SQLAlchemy
from db import DB
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db = DB()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_comments = SQLAlchemy(app)

UsersModel(db.get_connection()).init_table()
BooksModel(db.get_connection()).init_table()
AuthorsModel(db.get_connection()).init_table()


class Comment(db_comments.Model):
    """сущность комментариев"""
    id = db_comments.Column(db_comments.Integer, primary_key=True)
    book_id = db_comments.Column(db_comments.Integer, unique=False, nullable=False)
    book_id = db_comments.Column(db_comments.Integer, unique=False, nullable=False)
    book_name = db_comments.Column(db_comments.String(80), unique=False, nullable=False)
    username = db_comments.Column(db_comments.String(80), unique=False, nullable=False)
    name = db_comments.Column(db_comments.String(80), unique=False, nullable=False)
    text = db_comments.Column(db_comments.String(500), unique=False, nullable=False)
    date = db_comments.Column(db_comments.String(8), unique=False, nullable=False)

    def __repr__(self):
        return '< {} !! {} !! {} !! {} !! {} >'.format \
            (self.username, self.book_name, self.date, self.name, self.text)


db_comments.create_all()


@app.route('/')
@app.route('/index')
def index():
    """ Главная страница """
    # загружаем списки книг и авторов
    books = BooksModel(db.get_connection()).get_all()
    authors = AuthorsModel(db.get_connection()).get_all()
    # страница для навторизованного пользователя
    if 'username' not in session:
        return render_template('main_page.html',
                               books=books,
                               title="MyBookShelf",
                               loged=False,
                               admin=False,
                               authors=authors)
    # страница для администратора
    if UsersModel(db.get_connection()).is_admin(session['username']):
        return render_template('main_page.html',
                               books=books,
                               title="MyBookShelf",
                               loged=True,
                               username=session['username'],
                               admin=True,
                               authors=authors)
    # страница для авторизованного пользователя
    return render_template('main_page.html',
                           books=books,
                           title="MyBookShelf",
                           loged=True,
                           username=session['username'],
                           authors=authors,
                           admin=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Страница авторизации
    :return:
    вывод формы авторизации или переход на регистрацию
    """
    form = LoginForm()
    if form.validate_on_submit():  # ввели логин и пароль
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        # проверяем наличие пользователя в БД и совпадение пароля
        if user_model.exists(user_name)[0] and \
                check_password_hash(user_model.exists(user_name)[1], password):
            session['username'] = user_name
            # запоминаем в сессии имя пользователя и кидаем на главную
            return redirect('/index')
        elif user_model.exists(user_name)[0]:
            flash('Введен неверный пароль')
        else:
            flash('Упс! Такого аккаунта не существует, повторите попытку! ')
    return render_template('login.html',
                           title='Авторизация',
                           form=form,
                           loged=False)


@app.route('/logout')
def logout():
    """ Выход из системы """
    session.pop('username', 0)
    return redirect('/index')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """ Форма регистрации """
    form = RegisterForm()
    if form.validate_on_submit():
        # создать пользователя
        users = UsersModel(db.get_connection())
        #  проверка существования пользоавтеля с таким же именем
        if form.user_name.data in [u[1] for u in users.get_all()]:
            flash('Такой пользователь уже существует')
        else:
            users.insert(user_name=form.user_name.data,
                         email=form.email.data,
                         password_hash=generate_password_hash
                         (form.password_hash.data))
            # редирект на страницу авторизации
            return redirect(url_for('login'))
    return render_template("register.html",
                           title='Регистрация',
                           form=form,
                           loged=False)


""" Возможности администратора """


@app.route('/add_books', methods=['GET', 'POST'])
def add_book():
    """ Добавление книги """
    # Ошибка, если пользователь не администратор или не зарегистрирован
    if 'username' not in session:
        return render_template('error.html',
                               loged=False,
                               title='Ошибка')
    if not UsersModel(db.get_connection()).is_admin(session['username']):
        return render_template('error.html',
                               loged=False,
                               title='Ошибка')
    form = AddBookForm()
    if form.validate_on_submit():
        # создать книгу
        books = BooksModel(db.get_connection())
        f = None
        all_books = BooksModel(db.get_connection()).get_all()
        for i in range(len(all_books)):
            if all_books[i][2] == form.author.data:
                f = all_books[i][0]
        if f:
            # добавить книгу в список произведений автора
            author = AuthorsModel(db.get_connection()).get_by_name(form.author.data)
            book_list = author[4] + '//' + form.name.data
            AuthorsModel(db.get_connection()).add_book(book_list, author[0])
        if form.pictures.data is not None:
            filename = secure_filename(form.pictures.data.filename)
            server_file = 'static/img/' + filename
            form.pictures.data.save(server_file)
        books.insert(name=form.name.data,
                     author=form.author.data,
                     year=form.year.data,
                     pages=form.pages.data,
                     pictures=filename,
                     bio=form.bio.data,
                     stock=form.stock.data,
                     price=form.price.data)
        # редирект на главную страницу
        return redirect('index')
    return render_template("add_book.html",
                           title='Добавить книгу',
                           form=form,
                           loged=True)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """ Добавление автора """
    # Ошибка, если пользователь не администратор или не зарегистрирован
    if 'username' not in session:
        return render_template('error.html',
                               loged=False,
                               title='Ошибка')
    if not UsersModel(db.get_connection()).is_admin(session['username']):
        return render_template('error.html',
                               loged=False,
                               title='Ошибка')
    books = BooksModel(db.get_connection()).get_all()
    form = AddAuthorForm()
    if form.validate_on_submit():
        # создать автора
        authors = AuthorsModel(db.get_connection())
        book_list = ''
        for item in books:
            if item[2] == form.name.data:
                book_list += item[1] + '//'
        book_list.rstrip('//')
        if form.picture.data is not None:
            filename = secure_filename(form.picture.data.filename)
            server_file = 'static/img/' + filename
            form.pictures.data.save(server_file)
        authors.insert(name=form.name.data,
                       picture=filename,
                       bio=form.bio.data,
                       books=book_list)
        # редирект на главную страницу
        return redirect('index')
    return render_template("add_author.html",
                           title='Добавить автора',
                           form=form,
                           loged=True)


@app.route('/add_admin/<int:book_id>', methods=['GET'])
def add_book_admin(book_id):
    """ Добавление книг на склад """
    # Ошибка, если пользователь не администратор или не зарегистрирован
    if 'username' not in session:
        return render_template('error.html',
                               loged=False,
                               title='Ошибка')
    if not UsersModel(db.get_connection()).is_admin(session['username']):
        return render_template('error.html',
                               loged=False,
                               title='Ошибка')
    # Изменение числа книг на складе
    book = BooksModel(db.get_connection()).get(book_id)
    BooksModel(db.get_connection()).add_book(book_id, book[7])
    # Редирект на страницу книги
    return redirect('book/' + str(book_id))


@app.route('/delete_admin/<int:book_id>', methods=['GET'])
def delete_book_admin(book_id):
    """ Удаление существующих книг """
    # Ошибка, если пользователь не администратор или не зарегистрирован
    if 'username' not in session:
        return render_template('error.html',
                               loged=False,
                               title='Ошибка')
    if not UsersModel(db.get_connection()).is_admin(session['username']):
        return render_template('error.html',
                               loged=False,
                               title='Ошибка')
    BooksModel(db.get_connection()).delete(book_id)
    # Удаление книги из всех корзин пользователей
    users = UsersModel(db.get_connection()).get_all()
    for item in users:
        books = item[5].split('//')
        if str(book_id) in books:
            k = []
            for i in range(len(books)):
                if books[i] == str(book_id):
                    k.append(i)
            for l in k:
                del books[l]
            '//'.join(books)
            UsersModel(db.get_connection()).add_book(item[0], books)
    # Редирект на главную страницу
    return redirect('index')


""" Возможности посетителя сайта """


@app.route('/authors')
def authors_page():
    """ Страница со всеми писателями """
    books = BooksModel(db.get_connection()).get_all()
    authors = AuthorsModel(db.get_connection()).get_all()
    # страница для не авторизованного пользователя
    if 'username' not in session:
        return render_template('authors_page.html',
                               books=books, title="Писатели",
                               loged=False,
                               admin=False,
                               authors=authors)
    # страница для администратора
    if UsersModel(db.get_connection()).is_admin(session['username']):
        return render_template('authors_page.html',
                               books=books, title="Писатели",
                               loged=True,
                               username=session['username'],
                               admin=True,
                               authors=authors)
    # страница для авторизованного пользователя
    return render_template('authors_page.html',
                           books=books, title="Писатели",
                           loged=True,
                           username=session['username'],
                           authors=authors)


@app.route('/books')
def books_page():
    """ Страница со всеми книгами """
    books = BooksModel(db.get_connection()).get_all()
    authors = AuthorsModel(db.get_connection()).get_all()
    # страница для не авторизованного пользователя
    if 'username' not in session:
        return render_template('books_page.html',
                               books=books,
                               title="Книги",
                               loged=False,
                               admin=False,
                               authors=authors)
    # страница для администратора
    if UsersModel(db.get_connection()).is_admin(session['username']):
        return render_template('books_page.html',
                               books=books, title="Книги",
                               loged=True,
                               username=session['username'],
                               admin=True, authors=authors)
    # страница для авторизованного пользователя
    return render_template('books_page.html',
                           books=books, title="Книги",
                           loged=True,
                           username=session['username'],
                           authors=authors)


@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
def book(book_id, alert=0):
    """ Вывод информации о книге """
    if 'username' not in session:
        loged = False
    else:
        loged = True
    # ошибка, если такой книги нет в базе
    if not BooksModel(db.get_connection()).exists_id(book_id):
        return render_template('error.html',
                               loged=loged,
                               title='Ошибка')
    book = BooksModel(db.get_connection()).get(book_id)
    # вывод комментариев для авторизованного пользователя
    if loged:
        all_comments = []
        comments = Comment.query.filter_by(book_id=book_id).all()
        for comment in comments:
            all_comments.append(str(comment).strip('<> ').split(' !! '))
        author = AuthorsModel(db.get_connection()).exists(book[2])
        return render_template('book_info.html',
                               username=session['username'],
                               title=book[1],
                               loged=loged,
                               book=book,
                               alert=alert,
                               author=author,
                               comments=all_comments,
                               admin=UsersModel(db.get_connection()).is_admin
                               (session['username']))
    # вывод без возможности просматривать комменатрии для не авторизованного пользователя
    author = AuthorsModel(db.get_connection()).exists(book[2])
    return render_template('book_info.html',
                           title=book[1],
                           loged=loged,
                           book=book,
                           alert=alert,
                           admin=False,
                           author=author)


@app.route('/author/<int:author_id>', methods=['GET', 'POST'])
def author_page(author_id):
    """ Вывод информации о писателе """
    # проверка, авторизован ли пользователь
    if 'username' not in session:
        loged = False
    else:
        loged = True
    # ошибка, если такого автора нет в базе
    if not AuthorsModel(db.get_connection()).exists_id(str(author_id)):
        return render_template('error.html',
                               loged=loged,
                               title='Ошибка')
    books = BooksModel(db.get_connection())
    book = []
    author = AuthorsModel(db.get_connection()).get(author_id)
    books_author = author[4].split('//')
    for item in books_author:
        book.append(books.get_by_name(str(item)))
    # для авторизованного пользователя показывается список книг автора
    # для не авторизованного пользователя показывается только страница автора
    # страница для администратора
    if UsersModel(db.get_connection()).is_admin(session['username']):
        return render_template('author_info.html',
                               title=author[1],
                               loged=loged,
                               author=author,
                               book=book,
                               admin=True)
    return render_template('author_info.html',
                           title=author[1],
                           loged=loged,
                           author=author,
                           book=book,
                           admin=False)


@app.route('/edit_author/<int:author_id>', methods=['GET', 'POST'])
def edit_author_page(author_id):
    """ Редактирование информации о писателе """
    # проверка, авторизован ли пользователь
    if 'username' not in session:
        loged = False
    else:
        loged = True
    # ошибка, если такого автора нет в базе
    if not AuthorsModel(db.get_connection()).exists_id(str(author_id)):
        return render_template('error.html',
                               loged=loged,
                               title='Ошибка')
    books = BooksModel(db.get_connection())
    book = []
    author = AuthorsModel(db.get_connection()).get(author_id)
    books_author = author[4].split('//')
    for item in books_author:
        book.append(books.get_by_name(str(item)))
    if UsersModel(db.get_connection()).is_admin(session['username']):
        form = EditAuthorForm()
        if form.validate_on_submit():
            if form.bio.data:
                AuthorsModel(db.get_connection()).edit_bio(author_id, form.bio.data)
            if form.picture.data is not None:
                filename = secure_filename(form.picture.data.filename)
                server_file = 'static/img/' + filename
                form.picture.data.save(server_file)
                AuthorsModel(db.get_connection()).edit_picture(author_id, filename)
            return redirect('author/' + str(author_id))

        return render_template('edit_author.html',
                               title='Редактирование',
                               loged=loged,
                               admin=True,
                               form=form)

    return render_template('author_info.html',
                           title=author[1],
                           loged=loged,
                           author=author,
                           book=book,
                           admin=False)


@app.route('/search', methods=['GET', 'POST'])
def search():
    """ Поиск писателей и произведений по сайту """
    if 'username' not in session:
        loged = False
    else:
        loged = True
    form = SearchForm()
    if form.validate_on_submit():
        exists = BooksModel(db.get_connection()).exists(form.search.data)
        # результат, если есть книга с таким названием
        if exists[0]:
            result = BooksModel(db.get_connection()).get(exists[1])
            return render_template("search.html",
                                   title='Поиск',
                                   form=form,
                                   loged=loged,
                                   result=(result, 1))
        exists = AuthorsModel(db.get_connection()).exists(form.search.data)
        # результат, если есть автор с таким именем
        if exists:
            result = AuthorsModel(db.get_connection()).get(exists)
            return render_template("search.html",
                                   title='Поиск',
                                   form=form,
                                   loged=loged,
                                   result=(result, 2))
        # результат, если по запросу ничего не найдено
        return render_template("search.html",
                               title='Поиск',
                               form=form,
                               loged=loged,
                               result='error')
    return render_template("search.html",
                           title='Поиск',
                           form=form,
                           loged=loged,
                           result=False)


""" Обработка возможностей только авторизованных пользовтаелей """


@app.route('/book/<int:book_id>/comment', methods=['GET', 'POST'])
def comment_book(book_id):
    """ Создание комментариев к книгам"""
    # если пользователь не авторизован, кидаем его на страницу входа
    if 'username' not in session:
        return redirect('login')
    form = AddCommentForm()
    book = BooksModel(db.get_connection()).get(book_id)
    if not book:
        return render_template('error.html',
                               loged=True,
                               title='Ошибка')
    if form.validate_on_submit():
        # создать комментарий
        comment = Comment(book_id=book_id,
                          username=session['username'],
                          name=form.name.data,
                          text=form.text.data,
                          date=form.date.data,
                          book_name=book[1])
        db_comments.session.add(comment)
        db_comments.session.commit()
        # редирект на страницу книги
        return redirect('/book/' + str(book_id))
    return render_template("add_comment.html",
                           title='Добавить рецензию',
                           form=form,
                           loged=True)


""" Обработка действий с корзиной пользователя"""


@app.route('/add/<int:book_id>', methods=['GET'])
def add_book_shopping(book_id):
    """ Добавление товара в корзину из интерфейса корзины """
    # ошибка, если пользователь не авторизован
    if 'username' not in session:
        return render_template('error.html',
                               loged=False,
                               title='Ошибка')
    user = UsersModel(db.get_connection()).get_by_name(session['username'])
    book = BooksModel(db.get_connection()).get(book_id)
    # изменение БД
    books = user[5] + '//' + str(book_id)
    num = 0
    for item in books.split('//'):
        if int(item) == book_id:
            num += 1
    if book[7] - num >= 0:
        UsersModel(db.get_connection()).add_book(user[0], books)
    return redirect('shopping')


@app.route('/delete/<int:book_id>', methods=['GET'])
def delete_book_shopping(book_id):
    """ Удаление товара в корзину из интерфейса корзины """
    # ошибка, если пользователь не авторизован
    if 'username' not in session:
        return render_template('error.html',
                               loged=False,
                               title='Ошибка')
    user = UsersModel(db.get_connection()).get_by_name(session['username'])
    # изменение БД
    books = user[5].split('//')
    f = None
    for i in range(len(books)):
        if not f and int(books[i]) == book_id:
            f = i
    del books[f]
    books = '//'.join(books)
    UsersModel(db.get_connection()).add_book(user[0], books)
    return redirect('shopping')


@app.route('/book/<int:book_id>/buy', methods=['GET'])
def buy_book(book_id):
    """ Добавление книги в корзину через интерфейс страницы книги """
    # если пользователь не авторизован, кидаем его на страницу входа
    if 'username' not in session:
        return redirect('login')
    user = UsersModel(db.get_connection()).get_by_name(session['username'])
    book = BooksModel(db.get_connection()).get(book_id)
    # изменение БД
    if user[5]:
        books = user[5] + '//' + str(book_id)
    else:
        books = str(book_id)
    num = 0
    for item in books.split('//'):
        if int(item) == book_id:
            num += 1
    all_comments = []
    comments = Comment.query.filter_by(book_id=book_id).all()
    for comment in comments:
        all_comments.append(str(comment).strip('<> ').split(' !! '))
    author = AuthorsModel(db.get_connection()).exists(book[2])
    # добавление книги в корзину, если она есть на складе
    if book[7] - num >= 0:
        UsersModel(db.get_connection()).add_book(user[0], books)
        return render_template('book_info.html',
                               username=session['username'],
                               title=book[1],
                               loged=True,
                               book=book,
                               alert=1,
                               author=author,
                               comments=all_comments,
                               admin=UsersModel(db.get_connection()).is_admin
                               (session['username']))
    # вывод сообщения, если книги нет на складе
    else:
        return render_template('book_info.html',
                               username=session['username'],
                               title=book[1],
                               loged=True,
                               book=book,
                               alert=2,
                               author=author,
                               comments=all_comments,
                               admin=UsersModel(db.get_connection()).is_admin
                               (session['username']))


@app.route('/shopping', methods=['GET', 'POST'])
def shopping():
    """ Вывод интерфейса корзины """
    if 'username' not in session:
        return render_template('error.html',
                               loged=False,
                               title='Ошибка')
    else:
        loged = True
    user = UsersModel(db.get_connection()).get_by_name(session['username'])

    books = BooksModel(db.get_connection())
    all_books = {}
    # наполнение корзины покупками, если она не пустая
    if user[5]:
        for item in user[5].split('//'):
            if books.get(item) in all_books:
                all_books[books.get(item)] += 1
            else:
                all_books[books.get(item)] = 1
        return render_template('shopping.html',
                               username=session['username'],
                               title='Моя корзина',
                               loged=loged,
                               user=user,
                               books=all_books,
                               alert=0,
                               disabled=False)
    else:
        # отображение пустой корзины
        return render_template('shopping.html',
                               username=session['username'],
                               title='Моя корзина',
                               loged=loged,
                               user=user,
                               books={},
                               disabled=True)


@app.route('/order', methods=['GET', 'POST'])
def order():
    """ Обработка заказа """
    if 'username' not in session:
        return render_template('error.html',
                               loged=False,
                               title='Ошибка')
    user = UsersModel(db.get_connection()).get_by_name(session['username'])
    UsersModel(db.get_connection()).add_book(user[0], '')
    books = BooksModel(db.get_connection())
    # изменение БД
    if user[5]:
        for item in user[5].split('//'):
            books.buy_book(int(item), books.get(int(item))[7])
    user = UsersModel(db.get_connection()).get_by_name(session['username'])
    return render_template('shopping.html',
                           username=session['username'],
                           title='Моя корзина',
                           loged=True,
                           user=user,
                           books='',
                           alert=1,
                           disabled=True)


@app.route('/delete_all', methods=['GET', 'POST'])
def delete_all():
    """ Очстка корзины """
    if 'username' not in session:
        return render_template('error.html',
                               loged=False,
                               title='Ошибка')
    # изменение БД
    user = UsersModel(db.get_connection()).get_by_name(session['username'])
    UsersModel(db.get_connection()).add_book(user[0], '')
    user = UsersModel(db.get_connection()).get_by_name(session['username'])
    return render_template('shopping.html',
                           username=session['username'],
                           title='Моя корзина',
                           loged=True,
                           user=user,
                           books='',
                           alert=2,
                           disabled=True)


@app.route('/sort_by_price')
def books_page_price():
    """ Сортировка по цене"""
    books = BooksModel(db.get_connection()).get_all()
    authors = AuthorsModel(db.get_connection()).get_all()
    books = sorted(books, key=lambda x: int(x[8]))
    b = []
    p = 0
    for i in books:
        p += 1
        b.append((i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], p))
    # страница для не авторизованного пользователя
    if 'username' not in session:
        return render_template('books_page.html',
                               books=b,
                               title="Книги",
                               loged=False,
                               admin=False,
                               authors=authors, k=True)
    # страница для администратора
    if UsersModel(db.get_connection()).is_admin(session['username']):
        return render_template('books_page.html',
                               books=b, title="Книги",
                               loged=True,
                               username=session['username'],
                               admin=True, authors=authors, k=True)
    # страница для авторизованного пользователя
    return render_template('books_page.html',
                           books=books, title="Книги",
                           loged=True,
                           username=session['username'],
                           authors=authors)


@app.route('/sort_by_name')
def books_page_name():
    """ Сортировка по названию"""
    books = BooksModel(db.get_connection()).get_all()
    authors = AuthorsModel(db.get_connection()).get_all()
    books = sorted(books, key=lambda x: x[1])
    b = []
    p = 0
    for i in books:
        p += 1
        b.append((i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], p))
    # страница для не авторизованного пользователя
    if 'username' not in session:
        return render_template('books_page.html',
                               books=b,
                               title="Книги",
                               loged=False,
                               admin=False,
                               authors=authors, k=True)
    # страница для администратора
    if UsersModel(db.get_connection()).is_admin(session['username']):
        return render_template('books_page.html',
                               books=b, title="Книги",
                               loged=True,
                               username=session['username'],
                               admin=True, authors=authors, k=True)
    # страница для авторизованного пользователя
    return render_template('books_page.html',
                           books=books, title="Книги",
                           loged=True,
                           username=session['username'],
                           authors=authors)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
