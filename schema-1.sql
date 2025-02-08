-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'User'
);

-- Movies table
CREATE TABLE movie (  -- Updated to match __tablename__ = 'movie'
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    release_date TEXT NOT NULL, -- Stored as TEXT (ISO 8601 format)
    genre TEXT NOT NULL,
    description TEXT NOT NULL
);

-- Sessions table
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_id INTEGER NOT NULL,
    date TEXT NOT NULL,  -- Stored as TEXT (ISO 8601 format)
    time TEXT NOT NULL,
    hall TEXT NOT NULL,  -- Matches hall column in Session model
    total_seats INTEGER NOT NULL,
    available_seats INTEGER NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movie (id) ON DELETE CASCADE
);

-- Bookings table
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,
    seat_number INTEGER NOT NULL,  -- Matches seat_number in Booking model
    booking_date TEXT NOT NULL,  -- Stored as TEXT (ISO 8601 format)
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
);
