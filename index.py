from flask import Flask, render_template, redirect, url_for, request, g
from database import Database
import requests, random, os

GOOGLE_BOOKS_API_KEY = os.environ.get('GOOGLE_BOOKS_API_KEY')
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

app = Flask(__name__, static_url_path="", static_folder="static")

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('index'))

    db = get_db()
    livres = db.get_livres()
    random.shuffle(livres)

    return render_template('index.html', title='Index', livres=livres[:6])

# Book page route
@app.route('/livre/<livre_id>')
def page_livre(livre_id):
    livre = get_db().get_livre(livre_id)
    return render_template('book-page.html', title=livre['titre'], livre=livre)

# Search route for searching books
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form.get('searchTerm')
        if search_term is not None:
            search_term = search_term.lower()

        livres = get_db().get_livres()
        champs = ['titre', 'description', 'auteur', 'categorie']

        livre_match = [
            livre for livre in livres if (
                any(search_term in str(livre[champ]).lower() for champ in champs)
            )
        ] if search_term else []
        return render_template('search.html', livres=livre_match, search_term=search_term)

    return render_template('search.html')

# Fetch books from Google Books API and add them to the database
@app.route('/fetch_books', methods=['GET', 'POST'])
def fetch_books():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if search_query:
            books = fetch_books_from_google(search_query)
            db = get_db()

            if books:
                for book in books:
                    titre = book['volumeInfo'].get('title', 'Unknown Title')
                    auteur = ', '.join(book['volumeInfo'].get('authors', ['Unknown Author']))
                    description = book['volumeInfo'].get('description', 'No Description')
                    date_publication = book['volumeInfo'].get('publishedDate', 'Unknown Date')
                    categorie = ', '.join(book['volumeInfo'].get('categories', ['Unknown Category']))
                    image_url = book['volumeInfo'].get('imageLinks', {}).get('thumbnail', '')
                    preview_link = book.get("accessInfo", {}).get("webReaderLink", "")
                    info_link = book['volumeInfo'].get("infoLink", "")
                    buy_link = book.get("saleInfo", {}).get("buyLink", "")

                    # Add the book to the database if it doesn't exist
                    if not db.is_book_exist(titre, auteur):
                        db.add_livre(titre, date_publication, description, auteur, categorie, image_url, preview_link, info_link, buy_link)
                    
            # Redirect to catalog page after fetching books
            return redirect(url_for('catalog'))

    # For GET request or if no books are fetched, just show the fetch-books page
    return render_template('fetch-books.html')

def fetch_books_from_google(query):
    params = {
        'q': query,
        'key': GOOGLE_BOOKS_API_KEY
    }
    response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
    if response.status_code == 200:
        return response.json()['items']
    else:
        return None

@app.route('/delete_book/<int:livre_id>', methods=['POST'])
def delete_book(livre_id):
    db = get_db()
    db.delete_livre(livre_id)
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/catalog')
def catalog():
    db = get_db()
    livres = db.get_livres()
    return render_template('catalog.html', title='Catalogue', livres=livres)