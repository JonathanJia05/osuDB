# osuDB
Project I made so that anyone can have easy access to the 170k+ ranked maps currently in osu. Used in conjunction with [osdbParser](https://github.com/JonathanJia05/osdbParser) to create the json files to be processed. 

- working on creating a RESTful API so that users don't need to request and retrieve data through the postgres CLI (Although using PGAdmin 4 is useful)

## Setup

### 1. Clone repo

```bash
https://github.com/JonathanJia05/osuDB.git
cd osuDB
```

### 2. Install Postgres

### 3. Setup Postgres database
```bash
psql -U postgres
CREATE DATABASE osudb;
exit
```
### 4. Install requirements
Run:
```bash
pip install -r requirements.txt
```

### 5. Create database.ini
Create a database.ini file and put it in the root directory
In the file:
```bash
[postgresql]
host=localhost
database=osudb
user=YourUsername
password=YourPassword
```
Replace YourUsername and YourPassword with your credentials that you setup postgres with.

### 6. Connect to the database
In the root directory run:
```bash
python -m app.database.connect.py
```

### 7. Create tables
In the root directory run:
```bash
python -m app.database.create_tables
```

### 8. Load database with maps
In the root directory run:
```bash
python -m app.scripts.parser
```
