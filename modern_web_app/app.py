from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import database

app = Flask(__name__)
app.secret_key = os.urandom(24) # Strong session key

# Helper to verify login
def is_logged_in():
    return session.get('logged_in', False)

@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('index'))
    
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'marco' and password == '1234':
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error = 'Usuario o contraseña incorrectos.'
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- PATIENTS API ---

@app.route('/api/patients', methods=['GET'])
def get_patients():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    
    search = request.args.get('search', '')
    patients = database.get_patients(search)
    return jsonify(patients)

@app.route('/api/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    
    patient = database.get_patient(patient_id)
    if patient:
        return jsonify(patient)
    return jsonify({'error': 'Patient not found'}), 404

@app.route('/api/patients', methods=['POST'])
def add_patient():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    try:
        database.add_patient(
            nombre=data.get('nombre'),
            apellido=data.get('apellido'),
            edad=data.get('edad'),
            cedula=data.get('cedula'),
            direccion=data.get('direccion'),
            telefono=data.get('telefono'),
            sexo=data.get('sexo'),
            nacimiento=data.get('nacimiento'),
            altura=data.get('altura'),
            peso=data.get('peso')
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    try:
        database.update_patient(
            patient_id=patient_id,
            nombre=data.get('nombre'),
            apellido=data.get('apellido'),
            edad=data.get('edad'),
            cedula=data.get('cedula'),
            direccion=data.get('direccion'),
            telefono=data.get('telefono'),
            sexo=data.get('sexo'),
            nacimiento=data.get('nacimiento'),
            altura=data.get('altura'),
            peso=data.get('peso')
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        database.delete_patient(patient_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- STATS API ---

@app.route('/api/stats', methods=['GET'])
def get_stats():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        stats = database.get_stats_data()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- EXAMS API ---

@app.route('/api/exams/<int:patient_id>', methods=['GET'])
def get_exams(patient_id):
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    
    exams = database.get_exams(patient_id)
    if exams:
        return jsonify(exams)
    return jsonify({}) # Return empty object if no exams found

@app.route('/api/exams/<int:patient_id>', methods=['POST'])
def save_exams(patient_id):
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    try:
        database.save_exams(patient_id, data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- PRINT REPORT ---

@app.route('/report/<int:patient_id>')
def report(patient_id):
    if not is_logged_in():
        return redirect(url_for('login'))
        
    patient = database.get_patient(patient_id)
    if not patient:
        return "Paciente no encontrado", 404
        
    exams = database.get_exams(patient_id)
    
    exam_names = [
        "Glóbulos Blancos", "Plaquetas", "Colesterol", "HDL", "LDL", "Triglicéridos",
        "Glucosa", "Urea", "Creatinina", "Ácido Úrico", "Proteínas Totales", "Albúmina",
        "ALT", "AST", "Fosfatasa Alcalina", "GGT", "Bilirrubina Total", "Glóbulos Rojos"
    ]
    
    exam_metadata = [
        {"key": "globulosBlancos", "name": "Glóbulos Blancos", "unit": "x10³/µL", "ref_m": "4.5 - 11.0", "ref_f": "4.5 - 11.0"},
        {"key": "Plaquetas", "name": "Plaquetas", "unit": "x10³/µL", "ref_m": "150 - 450", "ref_f": "150 - 450"},
        {"key": "Colesterol", "name": "Colesterol", "unit": "mg/dL", "ref_m": "< 200", "ref_f": "< 200"},
        {"key": "HDL", "name": "HDL", "unit": "mg/dL", "ref_m": "> 40", "ref_f": "> 50"},
        {"key": "LDL", "name": "LDL", "unit": "mg/dL", "ref_m": "< 100", "ref_f": "< 100"},
        {"key": "Trigliceridos", "name": "Triglicéridos", "unit": "mg/dL", "ref_m": "< 150", "ref_f": "< 150"},
        {"key": "Glucosa", "name": "Glucosa", "unit": "mg/dL", "ref_m": "70 - 100", "ref_f": "70 - 100"},
        {"key": "Urea", "name": "Urea", "unit": "mg/dL", "ref_m": "15 - 45", "ref_f": "15 - 45"},
        {"key": "Creatinina", "name": "Creatinina", "unit": "mg/dL", "ref_m": "0.7 - 1.3", "ref_f": "0.6 - 1.1"},
        {"key": "acidoUrico", "name": "Ácido Úrico", "unit": "mg/dL", "ref_m": "3.4 - 7.0", "ref_f": "2.4 - 6.0"},
        {"key": "proteinasTotales", "name": "Proteínas Totales", "unit": "g/dL", "ref_m": "6.0 - 8.3", "ref_f": "6.0 - 8.3"},
        {"key": "Albumina", "name": "Albúmina", "unit": "g/dL", "ref_m": "3.5 - 5.0", "ref_f": "3.5 - 5.0"},
        {"key": "ALT", "name": "ALT", "unit": "U/L", "ref_m": "7 - 56", "ref_f": "7 - 56"},
        {"key": "AST", "name": "AST", "unit": "U/L", "ref_m": "10 - 40", "ref_f": "10 - 40"},
        {"key": "fosfatasaAlcalina", "name": "Fosfatasa Alcalina", "unit": "U/L", "ref_m": "44 - 147", "ref_f": "44 - 147"},
        {"key": "GGT", "name": "GGT", "unit": "U/L", "ref_m": "9 - 48", "ref_f": "9 - 48"},
        {"key": "bilirrubinaTotal", "name": "Bilirrubina Total", "unit": "mg/dL", "ref_m": "0.1 - 1.2", "ref_f": "0.1 - 1.2"},
        {"key": "globulosRojos", "name": "Glóbulos Rojos", "unit": "x10⁶/µL", "ref_m": "4.7 - 6.1", "ref_f": "4.2 - 5.4"}
    ]
    
    # Process exam values for display
    results = []
    if exams:
        for item in exam_metadata:
            val = exams.get(item["key"], "")
            if val:
                results.append({
                    "name": item["name"],
                    "value": f"{val} {item['unit']}",
                    "ref_m": f"{item['ref_m']} {item['unit']}",
                    "ref_f": f"{item['ref_f']} {item['unit']}"
                })
                
    return render_template('report.html', patient=patient, results=results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
