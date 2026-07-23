import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "labmed.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table for Patients
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entrada (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            edad INTEGER,
            cedula INTEGER,
            direccion TEXT,
            telefono TEXT,
            sexo TEXT,
            nacimiento TEXT,
            altura REAL,
            peso REAL
        )
    ''')
    
    # Safety migrations: check if columns exist, if not add them
    try:
        cursor.execute("ALTER TABLE entrada ADD COLUMN altura REAL")
    except sqlite3.OperationalError:
        pass # Already exists
        
    try:
        cursor.execute("ALTER TABLE entrada ADD COLUMN peso REAL")
    except sqlite3.OperationalError:
        pass # Already exists
        
    try:
        # Migrate old integer telefono to TEXT if needed (SQLite does this dynamically, but good to ensure text is fine)
        cursor.execute("ALTER TABLE entrada ADD COLUMN telefono TEXT")
    except sqlite3.OperationalError:
        pass
    
    # Table for Exams
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS examenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idPacientes INTEGER,
            globulosBlancos TEXT,
            Plaquetas TEXT,
            Colesterol TEXT,
            HDL TEXT,
            LDL TEXT,
            Trigliceridos TEXT,
            Glucosa TEXT,
            Urea TEXT,
            Creatinina TEXT,
            acidoUrico TEXT,
            proteinasTotales TEXT,
            Albumina TEXT,
            ALT TEXT,
            AST TEXT,
            fosfatasaAlcalina TEXT,
            GGT TEXT,
            bilirrubinaTotal TEXT,
            globulosRojos TEXT,
            FOREIGN KEY(idPacientes) REFERENCES entrada(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

# --- PATIENTS CRUD ---

def get_patients(search_query=None):
    conn = get_connection()
    cursor = conn.cursor()
    if search_query:
        query = f"%{search_query}%"
        cursor.execute('''
            SELECT id, nombre, apellido, edad, cedula, direccion, telefono, sexo, nacimiento, altura, peso 
            FROM entrada 
            WHERE nombre LIKE ? OR apellido LIKE ? OR cedula LIKE ?
            ORDER BY id DESC
        ''', (query, query, query))
    else:
        cursor.execute('SELECT id, nombre, apellido, edad, cedula, direccion, telefono, sexo, nacimiento, altura, peso FROM entrada ORDER BY id DESC')
    patients = cursor.fetchall()
    conn.close()
    
    keys = ["id", "nombre", "apellido", "edad", "cedula", "direccion", "telefono", "sexo", "nacimiento", "altura", "peso"]
    return [dict(zip(keys, p)) for p in patients]

def get_patient(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, apellido, edad, cedula, direccion, telefono, sexo, nacimiento, altura, peso FROM entrada WHERE id = ?', (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    if patient:
        keys = ["id", "nombre", "apellido", "edad", "cedula", "direccion", "telefono", "sexo", "nacimiento", "altura", "peso"]
        return dict(zip(keys, patient))
    return None

def add_patient(nombre, apellido, edad, cedula, direccion, telefono, sexo, nacimiento, altura=None, peso=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO entrada (nombre, apellido, edad, cedula, direccion, telefono, sexo, nacimiento, altura, peso)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, apellido, edad, cedula, direccion, telefono, sexo, nacimiento, altura, peso))
    conn.commit()
    conn.close()

def update_patient(patient_id, nombre, apellido, edad, cedula, direccion, telefono, sexo, nacimiento, altura=None, peso=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE entrada
        SET nombre=?, apellido=?, edad=?, cedula=?, direccion=?, telefono=?, sexo=?, nacimiento=?, altura=?, peso=?
        WHERE id=?
    ''', (nombre, apellido, edad, cedula, direccion, telefono, sexo, nacimiento, altura, peso, patient_id))
    conn.commit()
    conn.close()

def delete_patient(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM entrada WHERE id = ?', (patient_id,))
    conn.commit()
    conn.close()

# --- EXAMS CRUD ---

def get_exams(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM examenes WHERE idPacientes = ?', (patient_id,))
    exams = cursor.fetchone()
    conn.close()
    if exams:
        fields = [
            "id", "idPacientes", "globulosBlancos", "Plaquetas", "Colesterol", "HDL", "LDL", "Trigliceridos",
            "Glucosa", "Urea", "Creatinina", "acidoUrico", "proteinasTotales", "Albumina",
            "ALT", "AST", "fosfatasaAlcalina", "GGT", "bilirrubinaTotal", "globulosRojos"
        ]
        return dict(zip(fields, exams))
    return None

def save_exams(patient_id, exam_data):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if exams exist
    cursor.execute('SELECT id FROM examenes WHERE idPacientes = ?', (patient_id,))
    row = cursor.fetchone()
    
    fields = [
        "globulosBlancos", "Plaquetas", "Colesterol", "HDL", "LDL", "Trigliceridos",
        "Glucosa", "Urea", "Creatinina", "acidoUrico", "proteinasTotales", "Albumina",
        "ALT", "AST", "fosfatasaAlcalina", "GGT", "bilirrubinaTotal", "globulosRojos"
    ]
    
    if row:
        # Update
        set_clause = ", ".join([f"{f} = ?" for f in fields])
        values = [exam_data.get(f, "") for f in fields]
        values.append(patient_id)
        cursor.execute(f'UPDATE examenes SET {set_clause} WHERE idPacientes = ?', values)
    else:
        # Insert
        cols = ", ".join(fields)
        placeholders = ", ".join(["?" for _ in fields])
        values = [exam_data.get(f, "") for f in fields]
        cursor.execute(f'INSERT INTO examenes (idPacientes, {cols}) VALUES (?, {placeholders})', [patient_id] + values)
        
    conn.commit()
    conn.close()

# --- STATISTICS ---

def get_stats_data():
    conn = get_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Basic counts & averages
    cursor.execute('SELECT COUNT(*) FROM entrada')
    stats['total_patients'] = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(edad) FROM entrada')
    avg_age = cursor.fetchone()[0]
    stats['avg_age'] = round(avg_age, 1) if avg_age else 0
    
    cursor.execute('SELECT AVG(altura) FROM entrada WHERE altura IS NOT NULL AND altura > 0')
    avg_height = cursor.fetchone()[0]
    stats['avg_height'] = round(avg_height, 2) if avg_height else 0
    
    cursor.execute('SELECT AVG(peso) FROM entrada WHERE peso IS NOT NULL AND peso > 0')
    avg_weight = cursor.fetchone()[0]
    stats['avg_weight'] = round(avg_weight, 1) if avg_weight else 0
    
    cursor.execute('SELECT COUNT(*) FROM examenes')
    stats['total_exams'] = cursor.fetchone()[0]
    
    # Sex distribution
    cursor.execute('SELECT sexo, COUNT(*) FROM entrada GROUP BY sexo')
    stats['sex_dist'] = dict(cursor.fetchall())
    
    # Age brackets
    cursor.execute('''
        SELECT 
            SUM(CASE WHEN edad < 18 THEN 1 ELSE 0 END) as ninos,
            SUM(CASE WHEN edad BETWEEN 18 AND 35 THEN 1 ELSE 0 END) as jovenes,
            SUM(CASE WHEN edad BETWEEN 36 AND 60 THEN 1 ELSE 0 END) as adultos,
            SUM(CASE WHEN edad > 60 THEN 1 ELSE 0 END) as adultos_mayores
        FROM entrada
    ''')
    row = cursor.fetchone()
    stats['age_dist'] = {
        'Niños (<18)': row[0] or 0,
        'Jóvenes (18-35)': row[1] or 0,
        'Adultos (36-60)': row[2] or 0,
        'Adultos Mayores (>60)': row[3] or 0
    } if row else {}
    
    # Exam averages
    # CAST AS REAL since values are stored as TEXT
    cursor.execute('SELECT AVG(CAST(Glucosa AS REAL)) FROM examenes WHERE Glucosa IS NOT NULL AND Glucosa != ""')
    avg_glucosa = cursor.fetchone()[0]
    stats['avg_glucose'] = round(avg_glucosa, 1) if avg_glucosa else 0
    
    cursor.execute('SELECT AVG(CAST(Colesterol AS REAL)) FROM examenes WHERE Colesterol IS NOT NULL AND Colesterol != ""')
    avg_col = cursor.fetchone()[0]
    stats['avg_cholesterol'] = round(avg_col, 1) if avg_col else 0
    
    cursor.execute('SELECT AVG(CAST(Trigliceridos AS REAL)) FROM examenes WHERE Trigliceridos IS NOT NULL AND Trigliceridos != ""')
    avg_trig = cursor.fetchone()[0]
    stats['avg_triglycerides'] = round(avg_trig, 1) if avg_trig else 0

    # Risk alerts counts
    # Glucosa Alta > 100
    cursor.execute('SELECT COUNT(*) FROM examenes WHERE Glucosa IS NOT NULL AND Glucosa != "" AND CAST(Glucosa AS REAL) > 100')
    stats['high_glucose'] = cursor.fetchone()[0]
    
    # Colesterol Alto > 200
    cursor.execute('SELECT COUNT(*) FROM examenes WHERE Colesterol IS NOT NULL AND Colesterol != "" AND CAST(Colesterol AS REAL) > 200')
    stats['high_cholesterol'] = cursor.fetchone()[0]
    
    # Triglicéridos Altos > 150
    cursor.execute('SELECT COUNT(*) FROM examenes WHERE Trigliceridos IS NOT NULL AND Trigliceridos != "" AND CAST(Trigliceridos AS REAL) > 150')
    stats['high_triglycerides'] = cursor.fetchone()[0]
    
    conn.close()
    return stats

# Initialize DB when imported
init_db()
