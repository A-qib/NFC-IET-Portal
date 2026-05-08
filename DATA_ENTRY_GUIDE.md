# NFC IET Portal — Data Entry Guide

## Quick Start (3 Steps)

### Step 1: Create the Database
Open MySQL and run:
```sql
source /path/to/database_schema.sql;
source /path/to/seed_data.sql;
```

### Step 2: Update app.py Database Config
Edit `app.py` and update your MySQL password:
```python
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'YOUR_MYSQL_PASSWORD',
    'database': 'nfc_portal',
    'cursorclass': pymysql.cursors.DictCursor
}
```

### Step 3: Run the App
```bash
python app.py
```

## Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@nfc.edu | admin123 |
| **Teacher** | ali.ahmed@nfc.edu | teacher123 |
| **Student** | 2022cs001@nfc.edu | student123 |

## Adding New Data

### Via Admin Panel (Recommended)
Login as admin and use existing forms at `/admin/students`, `/admin/teachers`, `/admin/fees`.

### Via Direct SQL

**Add a New Student:**
```sql
INSERT INTO users (email, password_hash, role) 
VALUES ('2023cs001@nfc.edu', 'student123', 'student');

INSERT INTO students (user_id, name, roll_no, program_id, batch, semester)
VALUES (LAST_INSERT_ID(), 'Ali Raza', '2023-CS-001', 1, '2023', 1);
```

**Add a New Teacher:**
```sql
INSERT INTO users (email, password_hash, role) 
VALUES ('new.teacher@nfc.edu', 'teacher123', 'teacher');

INSERT INTO teachers (user_id, name, dept_id, designation)
VALUES (LAST_INSERT_ID(), 'New Teacher', 1, 'Lecturer');
```

## Password Security Note

Current passwords are plaintext. For production, use Werkzeug hashing:
```python
from werkzeug.security import generate_password_hash, check_password_hash
password_hash = generate_password_hash('password123')
```
