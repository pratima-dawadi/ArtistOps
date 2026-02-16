# ArtistOps
Admin panel to manage records of artists with their songs collection

## Tech Stack
- Python 3
- SQLite
- HTML
- CSS

## Features
- Authentication: register, login, logout
- Role-based access:
  - `super_admin`: manage users + view artists
  - `artist_manager`: manage artists, import/export artist CSV
  - `artist`: manage own songs only
- Pagination for dashboard tables


## Setup and Instructions

### 1. Clone the Repository

To get started, first clone the repository to your local machine:

```bash
https://github.com/pratima-dawadi/ArtistOps.git
cd ArtistOps
```

### 2. Running the application
1. Ensure python is installed.
2. Then, run:

```bash
python3 main.py
```

3. Open:

```text
http://localhost:8000
```

## Database
- SQLite DB file is created automatically at:
  - `src/database/ams.db`
- Tables initialized on startup:
  - `users`
  - `artists`
  - `songs`