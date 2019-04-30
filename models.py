class UsersModel:
    """Сущность пользователей"""

    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        """Инициализация таблицы"""
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(20) UNIQUE,
                             password_hash VARCHAR(128),
                             email VARCHAR(20),
                             is_admin INTEGER,
                             shopping_box VARCHAR(500)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash, email, is_admin=False,
               shopping_box=''):
        """Вставка новой записи"""
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash, email, is_admin, 
                          shopping_box) 
                          VALUES (?,?,?,?,?)''',
                       (user_name, password_hash, email, int(is_admin),
                        shopping_box))
        cursor.close()
        self.connection.commit()

    def add_book(self, user_id, books):
        """Вставка книги в корзину"""
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET shopping_box = ? WHERE id = ?",
                       [books, str(user_id)])
        cursor.close()
        self.connection.commit()

    def exists(self, user_name):
        """Проверка, есть ли пользователь в системе"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ?", [user_name])
        row = cursor.fetchone()
        return (True, row[2], row[0]) if row else (False,)

    def get(self, user_id):
        """Возврат пользователя по id"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", [str(user_id)])
        row = cursor.fetchone()
        return row

    def get_all(self):
        """Запрос всех пользователей"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def is_admin(self, username):
        """Проверка, ялвляется ли пользователь администратором"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ?", [username])
        row = cursor.fetchone()
        if not row:
            return False
        return True if row[4] == 1 else False

    def get_by_name(self, username):
        """Вывод пользователя по имени"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ?", [username])
        row = cursor.fetchone()
        return row


class BooksModel:
    """Сущность книг"""

    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        """Инициализация таблицы"""
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS books 
                            (book_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             name VARCHAR(20),
                             author VARCHAR(20),
                             year INTEGER,
                             pages INTEGER,
                             pictures VARCHAR(20),
                             bio VARCHAR(300),
                             stock INTEGER,
                             price INTEGER
                        )''')
        cursor.close()
        self.connection.commit()

    def insert(self, name, author, year, pages, pictures, bio, stock, price):
        """Добавление книги"""
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO books 
                          (name, author, year, pages, pictures, bio, stock, price) 
                          VALUES (?,?,?,?,?,?,?,?)''',
                       (name, author, str(year), str(pages),
                        str(pictures), bio, stock, price))
        cursor.close()
        self.connection.commit()

    def exists_id(self, book_id):
        """Проверка, есть ли книга, по id"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM books WHERE book_id = ?",
                       [str(book_id)])
        row = cursor.fetchone()
        return True if row else False

    def exists(self, name):
        """Поиск книги по названию"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM books WHERE name = ?",
                       [name])
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)

    def get(self, book_id):
        """Поиск книги по id"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM books WHERE book_id = ?", [str(book_id)])
        row = cursor.fetchone()
        return row

    def get_by_name(self, name):
        """Поиск книги по id"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM books WHERE name = ?", [name])
        row = cursor.fetchone()
        return row

    def buy_book(self, book_id, stock):
        """Изменение числа книг на складе (уменьшение)"""
        cursor = self.connection.cursor()
        cursor.execute("UPDATE books SET stock = ? WHERE book_id = ?",
                       [str(stock - 1), str(book_id)])
        cursor.close()
        self.connection.commit()

    def add_book(self, book_id, stock):
        """Изменение числа книг на складе (увеличение)"""
        cursor = self.connection.cursor()
        cursor.execute("UPDATE books SET stock = ? WHERE book_id = ?",
                       [str(stock + 1), str(book_id)])
        cursor.close()
        self.connection.commit()

    def get_all(self):
        """Запрос всех книг"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT book_id, name, author, year, pages, "
                       "pictures, bio, stock, price FROM books")
        rows = cursor.fetchall()
        return rows

    def delete(self, book_id):
        """Удаление книги"""
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM books WHERE book_id = ?''', [str(book_id)])
        cursor.close()
        self.connection.commit()


class AuthorsModel:
    """Сущность автора"""

    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        """Инициализация таблицы"""
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS authors 
                               (author_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                name VARCHAR(20),
                                picture VARCHAR(20),
                                bio VARCHAR(300),
                                books VARCHAR(200)
                           )''')
        cursor.close()
        self.connection.commit()

    def insert(self, name, picture, bio, books):
        """Добавление автора"""
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO authors 
                          (name, picture, bio, books) 
                          VALUES (?,?,?,?)''',
                       (name, picture, bio, books))
        cursor.close()
        self.connection.commit()

    def get_all(self):
        """Запрос всех авторов"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT author_id, name, picture, bio, books FROM authors")
        rows = cursor.fetchall()
        return rows

    def get(self, author_id):
        """Поиск автора по id"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM authors WHERE author_id = ?", [str(author_id)])
        row = cursor.fetchone()
        return row

    def exists_id(self, author_id):
        """Проверка, есть ли автор, по id"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM authors WHERE author_id = ?",
                       [str(author_id)])
        row = cursor.fetchone()
        return True if row else False

    def exists(self, name):
        """Поиск автора по имени"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM authors WHERE name = ?",
                       [name])
        row = cursor.fetchone()
        return row[0] if row else False

    def add_book(self, book_list, author_id):
        """Добавление книги в список книг автора"""
        cursor = self.connection.cursor()
        cursor.execute("UPDATE authors SET books = ? WHERE author_id = ?",
                       [book_list, str(author_id)])
        cursor.close()
        self.connection.commit()

    def get_by_name(self, name):
        """Поиск автора по имени"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM authors WHERE name = ?", [name])
        row = cursor.fetchone()
        return row

    def edit_bio(self, author_id, bio):
        """Редактирование биографии автора"""
        cursor = self.connection.cursor()
        cursor.execute("UPDATE authors SET bio = ? WHERE author_id = ?",
                       [bio, str(author_id)])
        cursor.close()
        self.connection.commit()

    def edit_picture(self, author_id, picture):
        """Редактирование фотографии автора"""
        cursor = self.connection.cursor()
        cursor.execute("UPDATE authors SET picture = ? WHERE author_id = ?",
                       [picture, str(author_id)])
        cursor.close()
        self.connection.commit()
