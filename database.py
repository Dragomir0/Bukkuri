import sqlite3

def _build_livre(result_set_item):
    livre = {
        "id": result_set_item[0],
        "titre": result_set_item[1],
        "date_publication": result_set_item[2],
        "description": result_set_item[3],
        "auteur": result_set_item[4],
        "categorie": result_set_item[5],
        "image_url": result_set_item[6],
        "preview_link": result_set_item[7],
        "info_link": result_set_item[8],
        "buy_link": result_set_item[9],
        "review_score": result_set_item[10],
    }
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
        query = "SELECT id, titre, date_publication, description, auteur, categorie, image_url, preview_link, info_link, buy_link, review_score FROM livres"
        cursor.execute(query)
        all_data = cursor.fetchall()
        return [_build_livre(item) for item in all_data]

    def get_livre(self, livre_id):
        cursor = self.get_connection().cursor()
        query = "SELECT id, titre, date_publication, description, auteur, categorie, image_url, preview_link, info_link, buy_link, review_score FROM livres WHERE id = ?"
        cursor.execute(query, (livre_id,))
        item = cursor.fetchone()
        return _build_livre(item) if item else None

    def add_livre(self, titre, date_publication, description, auteur, categorie, image_url, preview_link, info_link, buy_link, review_score):
        connection = self.get_connection()
        query = ("INSERT INTO livres (titre, date_publication, description, auteur, categorie, image_url, preview_link, info_link, buy_link, review_score)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
        connection.execute(query, (titre, date_publication, description, auteur, categorie, image_url, preview_link, info_link, buy_link, review_score))
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

class User:
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