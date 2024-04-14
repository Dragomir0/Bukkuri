CREATE TABLE livres (
    id INTEGER PRIMARY KEY,
    titre VARCHAR(50),
    date_publication VARCHAR(10),
    description VARCHAR(500),
    auteur VARCHAR(25),
    categorie VARCHAR(25),
    image_url VARCHAR(255),
    preview_link VARCHAR(255),
    info_link VARCHAR(255),
    buy_link VARCHAR(255)
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
