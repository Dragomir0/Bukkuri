import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

def _build_livre(result_set_item):
    livre = {}
    livre["id"] = result_set_item[0]
    livre["titre"] = result_set_item[1]
    livre["date_publication"] = result_set_item[2]
    livre["description"] = result_set_item[3]
    livre["auteur"] = result_set_item[4]
    livre["categorie"] = result_set_item[5]
    livre["image_url"] = result_set_item[6] 
    livre["preview_link"] = result_set_item[7]
    livre["info_link"] = result_set_item[8]
    livre["buy_link"] = result_set_item[9]
    return livre

class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/livres.db')
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def get_livres(self):
        cursor = self.get_connection().cursor()
        query = "SELECT id, titre, date_publication, description, auteur, categorie, image_url, preview_link, info_link, buy_link FROM livres"
        cursor.execute(query)
        all_data = cursor.fetchall()
        return [_build_livre(item) for item in all_data]

    def get_livre(self, livre_id):
        cursor = self.get_connection().cursor()
        query = "SELECT id, titre, date_publication, description, auteur, categorie, image_url, preview_link, info_link, buy_link FROM livres WHERE id = ?"
        cursor.execute(query, (livre_id,))
        item = cursor.fetchone()
        return _build_livre(item) if item else None

    def add_livre(self, titre, date_publication, description, auteur, categorie, image_url, preview_link, info_link, buy_link):
        connection = self.get_connection()
        query = ("INSERT INTO livres (titre, date_publication, description, auteur, categorie, image_url, preview_link, info_link, buy_link)"
                 " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
        connection.execute(query, (titre, date_publication, description, auteur, categorie, image_url, preview_link, info_link, buy_link))
        cursor = connection.cursor()
        cursor.execute("SELECT last_insert_rowid()")
        lastId = cursor.fetchone()[0]
        connection.commit()
        return lastId
    
    def is_book_exist(self, titre, auteur):
        connection = self.get_connection()
        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM livres WHERE titre = ? AND auteur = ?"
        cursor.execute(query, (titre, auteur))
        count = cursor.fetchone()[0]
        return count > 0
    
    def delete_livre(self, livre_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        query = "DELETE FROM livres WHERE id = ?"
        cursor.execute(query, (livre_id,))
        connection.commit()
    
    def get_user_by_id(self, user_id):
        """Retrieve a user by ID."""
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            # Map column names to values
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, user_data))
        return None

    def validate_login(self, email, password):
        """Validate user login using email and password."""
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT id, email, password, username FROM users WHERE email = ?", (email,))
        user_data = cursor.fetchone()
        if user_data:
            user_dict = dict(zip([column[0] for column in cursor.description], user_data))
            if check_password_hash(user_dict['password'], password):
                return user_dict
        return None
    
    def add_user(self, username, email, password):
        """Add a new user with hashed password."""
        connection = self.get_connection()
        cursor = connection.cursor()
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
        connection.commit()

    def get_user(self, email):
        """Retrieve a user by email."""
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT id, email, password FROM users WHERE email = ?", (email,))
        user_data = cursor.fetchone()
        if user_data:
            # Create a dictionary with column names as keys
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, user_data))
        return None

class User(UserMixin):
    def __init__(self, id, email, username):
        self.id = id
        self.email = email
        self.username = username

    @staticmethod
    def get(user_id, db):
        user_data = db.get_user_by_id(user_id)
        if user_data:
            return User(id=user_data['id'], email=user_data['email'], username=user_data['username'])
        return None
