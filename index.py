from flask import Flask, render_template, redirect, url_for, request, g, session
from flask_session import Session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from database import Database, User
import requests, random, os

app = Flask(__name__, static_url_path="", static_folder="static")
app.secret_key = os.environ.get('SECRET_KEY')

session_dir = os.path.join(os.getcwd(), 'session_data')
os.makedirs(session_dir, exist_ok=True)  

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = session_dir
Session(app)


GOOGLE_BOOKS_API_KEY = os.environ.get('GOOGLE_BOOKS_API_KEY')
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    db = get_db()  
    return User.get(user_id, db)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        db = Database()

        # Check if the email already exists
        if db.get_user(email):
            return render_template('register.html', error="Email already registered. Please login or use a different email.")

        # If the email is not registered, proceed to register the user
        db.add_user(username, email, password)
        
        # Redirect to the login page after successful registration
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db() 
        user = db.validate_login(email, password)
        if user:
            # Create a User instance 
            user_obj = User(id=user['id'], email=user['email'], username=user['username'])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

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

# Home page route
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

@app.route('/fetch_books', methods=['GET', 'POST'])
def fetch_books():
    if request.method == 'POST':
        search_query = request.form['search_query']
        books = fetch_books_from_google(search_query)
        if books:
            # Store only book IDs in the session
            session['book_ids'] = [book['id'] for book in books]
            # Keep the books in memory for immediate display
            session['books'] = {book['id']: book for book in books}
        else:
            session.pop('books', None)
            session.pop('book_ids', None)
        return render_template('fetch-books.html', books=books)

    return render_template('fetch-books.html')

def fetch_books_from_google(query):
    params = {
        'q': query,
        'maxResults': 6,  # Limit the number of results to 6
        'key': GOOGLE_BOOKS_API_KEY
    }
    response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        return None

@app.route('/add_selected_books', methods=['POST'])
def add_selected_books():
    selected_book_ids = request.form.getlist('book_ids')
    if selected_book_ids:
        all_books = session.get('books', {})
        db = get_db()

        for book_id in selected_book_ids:
            book = all_books.get(book_id)
            if book:
                titre = book['volumeInfo'].get('title', 'Unknown Title')
                auteur = ', '.join(book['volumeInfo'].get('authors', ['Unknown Author']))
                description = book['volumeInfo'].get('description', 'No Description')
                date_publication = book['volumeInfo'].get('publishedDate', 'Unknown Date')
                categorie = ', '.join(book['volumeInfo'].get('categories', ['Unknown Category']))
                image_url = book['volumeInfo'].get('imageLinks', {}).get('thumbnail', '')
                preview_link = book.get("accessInfo", {}).get("webReaderLink", "")
                info_link = book['volumeInfo'].get("infoLink", "")
                buy_link = book.get("saleInfo", {}).get("buyLink", "")

                # Check if the book already exists in the database to avoid duplicates
                if not db.is_book_exist(titre, auteur):
                    db.add_livre(titre, date_publication, description, auteur, categorie, image_url, preview_link, info_link, buy_link)

        # Clear session after adding books
        session.pop('books', None)
        session.pop('book_ids', None)
        return redirect(url_for('catalog'))

    return redirect(url_for('fetch_books'))

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

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')
