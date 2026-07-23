let selectedPatientId = null;
let patientsData = [];
let sexChartInstance = null;
let ageChartInstance = null;
let examsChartInstance = null;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', () => {
    loadPatients();
});

// Tab navigation switcher
function showTab(tabName) {
    const patientsSec = document.getElementById('patientsSection');
    const statsSec = document.getElementById('statsSection');
    const navPacientes = document.getElementById('navPacientes');
    const navStats = document.getElementById('navStats');
    
    if (tabName === 'pacientes') {
        patientsSec.style.display = 'block';
        statsSec.style.display = 'none';
        navPacientes.classList.add('active');
        navStats.classList.remove('active');
        loadPatients();
    } else if (tabName === 'stats') {
        patientsSec.style.display = 'none';
        statsSec.style.display = 'block';
        navStats.classList.add('active');
        navPacientes.classList.remove('active');
        loadStats();
    }
}

// Load all patients from API
function loadPatients() {
    fetch('/api/patients')
        .then(res => res.json())
        .then(data => {
            patientsData = data;
            renderPatientsTable(patientsData);
        })
        .catch(err => console.error("Error loading patients:", err));
}

// Render patient list into table
function renderPatientsTable(patients) {
    const tableBody = document.getElementById('patientTableBody');
    tableBody.innerHTML = '';
    
    if (patients.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="9" style="color: var(--text-muted); padding: 2rem;">No hay pacientes registrados.</td>
            </tr>
        `;
        return;
    }
    
    patients.forEach(p => {
        const row = document.createElement('tr');
        row.setAttribute('data-id', p.id);
        row.onclick = () => selectPatientRow(row, p.id);
        
        row.innerHTML = `
            <td>${p.id}</td>
            <td>${p.nombre}</td>
            <td>${p.apellido}</td>
            <td>${p.cedula || '-'}</td>
            <td>${p.edad || '-'}</td>
            <td>${p.direccion || '-'}</td>
            <td>${p.telefono || '-'}</td>
            <td><span class="badge badge-${p.sexo.toLowerCase()}">${p.sexo}</span></td>
            <td>${p.nacimiento || '-'}</td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Select patient row
function selectPatientRow(rowElement, patientId) {
    const rows = document.querySelectorAll('#patientTableBody tr');
    rows.forEach(r => r.classList.remove('selected'));
    
    if (selectedPatientId === patientId) {
        selectedPatientId = null;
    } else {
        rowElement.classList.add('selected');
        selectedPatientId = patientId;
    }
}

// Filter patients (Search)
function filterPatients() {
    const query = document.getElementById('searchInput').value.trim();
    if (query.length >= 2 || query.length === 0) {
        fetch(`/api/patients?search=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                patientsData = data;
                renderPatientsTable(patientsData);
            });
    }
}

// Patient Modal controls
function openPatientModal() {
    document.getElementById('patientModalTitle').innerText = "Nuevo Paciente";
    document.getElementById('patientForm').reset();
    document.getElementById('patientId').value = "";
    document.getElementById('patientModal').classList.add('active');
}

function closePatientModal() {
    document.getElementById('patientModal').classList.remove('active');
}

// Save patient (Add / Edit)
function savePatient(e) {
    e.preventDefault();
    
    const id = document.getElementById('patientId').value;
    
    // Assemble telephone prefix and number
    const prefix = document.getElementById('telefonoPrefix').value;
    const number = document.getElementById('telefonoNumber').value.trim();
    const fullPhone = number ? `${prefix}-${number}` : '';

    const patientData = {
        nombre: document.getElementById('nombre').value.trim(),
        apellido: document.getElementById('apellido').value.trim(),
        edad: document.getElementById('edad').value ? parseInt(document.getElementById('edad').value) : null,
        cedula: document.getElementById('cedula').value ? parseInt(document.getElementById('cedula').value) : null,
        direccion: document.getElementById('direccion').value.trim(),
        telefono: fullPhone,
        sexo: document.getElementById('sexo').value,
        altura: document.getElementById('altura').value ? parseFloat(document.getElementById('altura').value) : null,
        peso: document.getElementById('peso').value ? parseFloat(document.getElementById('peso').value) : null,
        nacimiento: document.getElementById('nacimiento').value.trim()
    };
    
    const method = id ? 'PUT' : 'POST';
    const url = id ? `/api/patients/${id}` : '/api/patients';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(patientData)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            closePatientModal();
            loadPatients();
            selectedPatientId = null;
        } else {
            alert("Error al guardar el paciente: " + data.error);
        }
    })
    .catch(err => console.error("Error saving patient:", err));
}

// Edit Patient
function editSelectedPatient() {
    if (!selectedPatientId) {
        alert("Por favor seleccione un paciente.");
        return;
    }
    
    fetch(`/api/patients/${selectedPatientId}`)
        .then(res => res.json())
        .then(p => {
            document.getElementById('patientModalTitle').innerText = "Editar Paciente";
            document.getElementById('patientId').value = p.id;
            document.getElementById('nombre').value = p.nombre || '';
            document.getElementById('apellido').value = p.apellido || '';
            document.getElementById('edad').value = p.edad || '';
            document.getElementById('cedula').value = p.cedula || '';
            document.getElementById('direccion').value = p.direccion || '';
            document.getElementById('sexo').value = p.sexo || 'Masculino';
            document.getElementById('altura').value = p.altura || '';
            document.getElementById('peso').value = p.peso || '';
            document.getElementById('nacimiento').value = p.nacimiento || '';
            
            // Split phone prefix and number
            if (p.telefono && p.telefono.includes('-')) {
                const parts = p.telefono.split('-');
                document.getElementById('telefonoPrefix').value = parts[0];
                document.getElementById('telefonoNumber').value = parts[1];
            } else {
                document.getElementById('telefonoPrefix').value = "0412";
                document.getElementById('telefonoNumber').value = p.telefono || '';
            }
            
            document.getElementById('patientModal').classList.add('active');
        });
}

// Delete Patient
function deleteSelectedPatient() {
    if (!selectedPatientId) {
        alert("Por favor seleccione un paciente.");
        return;
    }
    
    if (confirm("¿Está seguro que desea eliminar a este paciente y todos sus exámenes registrados?")) {
        fetch(`/api/patients/${selectedPatientId}`, {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                loadPatients();
                selectedPatientId = null;
            } else {
                alert("Error al eliminar paciente: " + data.error);
            }
        });
    }
}

// Exam Modal controls
function openExamModal() {
    document.getElementById('examModal').classList.add('active');
}

function closeExamModal() {
    document.getElementById('examModal').classList.remove('active');
}

// Load exams for editing
function loadExamsForSelected() {
    if (!selectedPatientId) {
        alert("Por favor seleccione un paciente.");
        return;
    }
    
    const patient = patientsData.find(p => p.id === selectedPatientId);
    document.getElementById('examModalTitle').innerText = `Exámenes - ${patient.nombre} ${patient.apellido}`;
    document.getElementById('examPatientId').value = selectedPatientId;
    document.getElementById('examForm').reset();
    
    fetch(`/api/exams/${selectedPatientId}`)
        .then(res => res.json())
        .then(exams => {
            const fields = [
                "globulosBlancos", "Plaquetas", "Colesterol", "HDL", "LDL", "Trigliceridos",
                "Glucosa", "Urea", "Creatinina", "acidoUrico", "proteinasTotales", "Albumina",
                "ALT", "AST", "fosfatasaAlcalina", "GGT", "bilirrubinaTotal", "globulosRojos"
            ];
            
            fields.forEach(f => {
                if (exams[f]) {
                    document.getElementById(f).value = exams[f];
                }
            });
            
            openExamModal();
        });
}

// Save exams
function saveExams(e) {
    e.preventDefault();
    
    const patientId = document.getElementById('examPatientId').value;
    const fields = [
        "globulosBlancos", "Plaquetas", "Colesterol", "HDL", "LDL", "Trigliceridos",
        "Glucosa", "Urea", "Creatinina", "acidoUrico", "proteinasTotales", "Albumina",
        "ALT", "AST", "fosfatasaAlcalina", "GGT", "bilirrubinaTotal", "globulosRojos"
    ];
    
    const examData = {};
    fields.forEach(f => {
        examData[f] = document.getElementById(f).value.trim();
    });
    
    fetch(`/api/exams/${patientId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(examData)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            closeExamModal();
        } else {
            alert("Error al guardar exámenes: " + data.error);
        }
    });
}

// Print Exams (open report in a new tab)
function printExamsForSelected() {
    if (!selectedPatientId) {
        alert("Por favor seleccione un paciente.");
        return;
    }
    
    window.open(`/report/${selectedPatientId}`, '_blank');
}

// --- STATS LOGIC ---

function loadStats() {
    fetch('/api/stats')
        .then(res => res.json())
        .then(stats => {
            // Update KPIs
            document.getElementById('kpiTotalPatients').innerText = stats.total_patients;
            document.getElementById('kpiAvgAge').innerText = `${stats.avg_age} años`;
            document.getElementById('kpiAvgHeight').innerText = `${parseFloat(stats.avg_height).toFixed(2)} m`;
            document.getElementById('kpiAvgWeight').innerText = `${parseFloat(stats.avg_weight).toFixed(1)} kg`;
            
            // Build Charts
            buildSexChart(stats.sex_dist);
            buildAgeChart(stats.age_dist);
            buildExamsChart(stats);
        })
        .catch(err => console.error("Error loading stats:", err));
}

function buildSexChart(sexDist) {
    const ctx = document.getElementById('sexChart').getContext('2d');

    // Color map: guaranteed colors per label regardless of SQL order
    const colorMap = {
        'Masculino': '#3b82f6',   // blue
        'Femenino':  '#ec4899',   // pink
        'Otro':      '#8b5cf6'    // purple
    };

    const labels = Object.keys(sexDist);
    const data   = Object.values(sexDist);
    const colors = labels.map(l => colorMap[l] || '#6b7280');
    const borders = labels.map(l =>
        l === 'Masculino' ? '#1d4ed8' :
        l === 'Femenino'  ? '#be185d' : '#6d28d9'
    );

    if (sexChartInstance) {
        sexChartInstance.destroy();
    }

    sexChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderColor: borders,
                borderWidth: 2,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#f3f4f6',
                        font: { family: 'Outfit', size: 13 },
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : 0;
                            return ` ${ctx.label}: ${ctx.parsed} (${pct}%)`;
                        }
                    }
                }
            }
        }
    });
}

function buildAgeChart(ageDist) {
    const ctx = document.getElementById('ageChart').getContext('2d');
    
    const labels = Object.keys(ageDist);
    const data = Object.values(ageDist);
    
    if (ageChartInstance) {
        ageChartInstance.destroy();
    }
    
    ageChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Pacientes',
                data: data,
                backgroundColor: 'rgba(16, 185, 129, 0.7)',
                borderColor: '#10b981',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { ticks: { color: '#9ca3af' }, grid: { display: false } },
                y: { ticks: { color: '#9ca3af', stepSize: 1 }, grid: { color: 'rgba(255,255,255,0.05)' } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function buildExamsChart(stats) {
    const ctx = document.getElementById('examsChart').getContext('2d');
    
    if (examsChartInstance) {
        examsChartInstance.destroy();
    }
    
    examsChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Glucosa Promedio', 'Colesterol Promedio', 'Triglicéridos Prom.'],
            datasets: [
                {
                    label: 'Promedio General (mg/dL)',
                    data: [stats.avg_glucose, stats.avg_cholesterol, stats.avg_triglycerides],
                    backgroundColor: 'rgba(59, 130, 246, 0.7)',
                    borderColor: '#3b82f6',
                    borderWidth: 2,
                    borderRadius: 6
                },
                {
                    label: 'Pacientes Fuera de Rango (Alerta)',
                    data: [stats.high_glucose, stats.high_cholesterol, stats.high_triglycerides],
                    backgroundColor: 'rgba(239, 68, 68, 0.7)',
                    borderColor: '#ef4444',
                    borderWidth: 2,
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { ticks: { color: '#9ca3af' }, grid: { display: false } },
                y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#f3f4f6', font: { family: 'Outfit', size: 12 } }
                }
            }
        }
    });
}
