import os
import io
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from werkzeug.utils import secure_filename
from functools import wraps
from collections import OrderedDict
from datetime import date as dt
import pymysql
import pymysql.cursors

app = Flask(__name__)
app.secret_key = 'nfc_portal_secret_key_2025'

# ── Upload folder ──────────────────────────────
UPLOAD_FOLDER   = 'static/uploads'
ALLOWED_EXT     = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

# ── Database ───────────────────────────────────
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'aqib913114',   # ← your MySQL password
    'database': 'nfc_portal',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db():
    return pymysql.connect(**DB_CONFIG)


# ── Decorators ─────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') != role:
                flash('Access denied.', 'error')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated
    return decorator


# ══════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for(session['role'] + '_dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        try:
            db  = get_db()
            cur = db.cursor()
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()
            cur.close(); db.close()
            if user and password == user['password_hash']:
                session['user_id'] = user['user_id']
                session['role']    = user['role']
                session['email']   = user['email']
                return redirect(url_for(user['role'] + '_dashboard'))
            flash('Invalid email or password.', 'error')
        except Exception as e:
            flash(f'Database error: {e}', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ══════════════════════════════════════════════
#  PROFILE & PASSWORD
# ══════════════════════════════════════════════
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    try:
        db  = get_db()
        cur = db.cursor()

        if request.method == 'POST':
            action = request.form.get('action')

            if action == 'change_password':
                current  = request.form.get('current_password', '')
                new_pass = request.form.get('new_password', '')
                confirm  = request.form.get('confirm_password', '')
                cur.execute("SELECT password_hash FROM users WHERE user_id=%s", (session['user_id'],))
                row = cur.fetchone()
                if row['password_hash'] != current:
                    flash('Current password is incorrect.', 'error')
                elif new_pass != confirm:
                    flash('New passwords do not match.', 'error')
                elif len(new_pass) < 6:
                    flash('Password must be at least 6 characters.', 'error')
                else:
                    cur.execute("UPDATE users SET password_hash=%s WHERE user_id=%s",
                                (new_pass, session['user_id']))
                    db.commit()
                    flash('Password changed successfully!', 'success')

            elif action == 'upload_photo':
                if 'photo' in request.files:
                    file = request.files['photo']
                    if file and allowed_file(file.filename):
                        filename = secure_filename(f"user_{session['user_id']}_{file.filename}")
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        cur.execute("UPDATE users SET photo=%s WHERE user_id=%s",
                                    (filename, session['user_id']))
                        db.commit()
                        flash('Photo updated!', 'success')

            elif action == 'update_phone':
                phone = request.form.get('phone', '')
                if session['role'] == 'student':
                    cur.execute("UPDATE students SET phone=%s WHERE user_id=%s",
                                (phone, session['user_id']))
                elif session['role'] == 'teacher':
                    cur.execute("UPDATE teachers SET phone=%s WHERE user_id=%s",
                                (phone, session['user_id']))
                db.commit()
                flash('Phone updated!', 'success')

        cur.execute("SELECT user_id, email, role, photo FROM users WHERE user_id=%s",
                    (session['user_id'],))
        user  = cur.fetchone()
        extra = {}

        if session['role'] == 'student':
            cur.execute("""
                SELECT s.name, s.roll_no, s.batch, s.semester, s.phone, s.gender,
                       p.name AS program, d.name AS department
                FROM students s
                JOIN programs p ON p.program_id = s.program_id
                JOIN departments d ON d.dept_id = p.dept_id
                WHERE s.user_id=%s
            """, (session['user_id'],))
            row = cur.fetchone()
            if row: extra = row

        elif session['role'] == 'teacher':
            cur.execute("""
                SELECT t.name, t.designation, t.phone, d.name AS department
                FROM teachers t JOIN departments d ON d.dept_id = t.dept_id
                WHERE t.user_id=%s
            """, (session['user_id'],))
            row = cur.fetchone()
            if row: extra = row

        cur.close(); db.close()
        return render_template('profile.html', user=user, extra=extra)

    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('profile.html', user={}, extra={})


# ══════════════════════════════════════════════
#  NOTIFICATIONS
# ══════════════════════════════════════════════
@app.route('/notifications')
@login_required
def notifications():
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC
        """, (session['user_id'],))
        notifs = cur.fetchall()
        cur.execute("UPDATE notifications SET is_read=1 WHERE user_id=%s", (session['user_id'],))
        db.commit()
        cur.close(); db.close()
        return render_template('notifications.html', notifications=notifs)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('notifications.html', notifications=[])


@app.route('/notifications/count')
@login_required
def notification_count():
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("SELECT COUNT(*) AS c FROM notifications WHERE user_id=%s AND is_read=0",
                    (session['user_id'],))
        count = cur.fetchone()['c']
        cur.close(); db.close()
        return jsonify({'count': count})
    except:
        return jsonify({'count': 0})


# ══════════════════════════════════════════════
#  STUDENT
# ══════════════════════════════════════════════
@app.route('/student/dashboard')
@login_required
@role_required('student')
def student_dashboard():
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT s.*, p.name AS program, d.name AS department
            FROM students s
            JOIN programs p ON p.program_id = s.program_id
            JOIN departments d ON d.dept_id = p.dept_id
            WHERE s.user_id=%s
        """, (session['user_id'],))
        student = cur.fetchone()
        if not student:
            flash('Student profile not found.', 'error')
            return redirect(url_for('logout'))

        sid = student['student_id']

        cur.execute("SELECT fn_calculate_cgpa(%s) AS cgpa", (sid,))
        cgpa = float(cur.fetchone()['cgpa'] or 0)

        cur.execute("""
            SELECT sd.course_name, sd.course_code, sd.teacher_name,
                   COALESCE(g.total,0) AS total,
                   fn_attendance_pct(e.enrollment_id) AS att_pct
            FROM enrollments e
            JOIN vw_section_details sd ON sd.section_id = e.section_id
            LEFT JOIN grades g ON g.enrollment_id = e.enrollment_id
            WHERE e.student_id=%s
        """, (sid,))
        courses = cur.fetchall()

        cur.execute("""
            SELECT a.title, a.body, a.created_at, t.name AS teacher, c.name AS course
            FROM announcements a
            JOIN teachers t ON t.teacher_id = a.teacher_id
            JOIN sections s ON s.section_id = a.section_id
            JOIN courses  c ON c.course_id  = s.course_id
            JOIN enrollments e ON e.section_id = s.section_id
            WHERE e.student_id=%s ORDER BY a.created_at DESC LIMIT 5
        """, (sid,))
        announcements = cur.fetchall()

        cur.execute("SELECT * FROM fee_records WHERE student_id=%s ORDER BY year DESC LIMIT 1", (sid,))
        fee = cur.fetchone()

        cur.execute("SELECT * FROM vw_shortage_alerts WHERE roll_no=%s", (student['roll_no'],))
        shortages = cur.fetchall()

        cur.close(); db.close()
        return render_template('student/dashboard.html',
            student=student, cgpa=cgpa, courses=courses,
            announcements=announcements, fee=fee, shortages=shortages)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('student/dashboard.html',
            student={'name':'','roll_no':'','program':'','semester':''},
            cgpa=0, courses=[], announcements=[], fee=None, shortages=[])


@app.route('/student/attendance')
@login_required
@role_required('student')
def student_attendance():
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("SELECT student_id FROM students WHERE user_id=%s", (session['user_id'],))
        sid = cur.fetchone()['student_id']

        cur.execute("""
            SELECT sd.course_name, sd.course_code, sd.teacher_name,
                   att.total_classes, att.present_count, att.absent_count,
                   att.late_count, att.attendance_pct, att.attendance_status,
                   e.enrollment_id
            FROM vw_attendance_summary att
            JOIN enrollments e ON e.enrollment_id = att.enrollment_id
            JOIN vw_section_details sd ON sd.section_id = e.section_id
            WHERE e.student_id=%s
        """, (sid,))
        subjects = cur.fetchall()

        details = {}
        for s in subjects:
            cur.execute("SELECT date, status FROM attendance WHERE enrollment_id=%s ORDER BY date DESC",
                        (s['enrollment_id'],))
            details[s['enrollment_id']] = cur.fetchall()

        cur.close(); db.close()
        return render_template('student/attendance.html', subjects=subjects, details=details)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('student/attendance.html', subjects=[], details={})


@app.route('/student/grades')
@login_required
@role_required('student')
def student_grades():
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("SELECT student_id, name, roll_no FROM students WHERE user_id=%s", (session['user_id'],))
        student = cur.fetchone()
        sid     = student['student_id']

        cur.execute("""
            SELECT c.name AS course_name, c.code, c.credit_hours, t.name AS teacher,
                   COALESCE(g.mid_marks,0) AS mid_marks,
                   COALESCE(g.final_marks,0) AS final_marks,
                   COALESCE(g.assignment_marks,0) AS assignment_marks,
                   COALESCE(g.total,0) AS total,
                   fn_letter_grade(COALESCE(g.total,0)) AS letter_grade,
                   fn_grade_points(COALESCE(g.total,0)) AS grade_points
            FROM enrollments e
            JOIN sections s ON s.section_id=e.section_id
            JOIN courses  c ON c.course_id=s.course_id
            JOIN teachers t ON t.teacher_id=s.teacher_id
            LEFT JOIN grades g ON g.enrollment_id=e.enrollment_id
            WHERE e.student_id=%s
        """, (sid,))
        grades = cur.fetchall()

        cur.execute("SELECT fn_calculate_cgpa(%s) AS cgpa", (sid,))
        cgpa = float(cur.fetchone()['cgpa'] or 0)

        cur.close(); db.close()
        return render_template('student/grades.html', grades=grades, cgpa=cgpa, student=student)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('student/grades.html', grades=[], cgpa=0, student={})


@app.route('/student/grades/chart-data')
@login_required
@role_required('student')
def grade_chart_data():
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("SELECT student_id FROM students WHERE user_id=%s", (session['user_id'],))
        sid = cur.fetchone()['student_id']
        cur.execute("""
            SELECT c.code,
                   COALESCE(g.mid_marks,0) AS mid,
                   COALESCE(g.final_marks,0) AS final,
                   COALESCE(g.assignment_marks,0) AS assign,
                   COALESCE(g.total,0) AS total
            FROM enrollments e
            JOIN sections s ON s.section_id=e.section_id
            JOIN courses  c ON c.course_id=s.course_id
            LEFT JOIN grades g ON g.enrollment_id=e.enrollment_id
            WHERE e.student_id=%s
        """, (sid,))
        rows = cur.fetchall()
        cur.close(); db.close()
        return jsonify({
            'labels':      [r['code']  for r in rows],
            'mid':         [float(r['mid'])    for r in rows],
            'final':       [float(r['final'])  for r in rows],
            'assignments': [float(r['assign']) for r in rows],
            'total':       [float(r['total'])  for r in rows],
        })
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/student/timetable')
@login_required
@role_required('student')
def student_timetable():
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("SELECT student_id FROM students WHERE user_id=%s", (session['user_id'],))
        sid = cur.fetchone()['student_id']
        cur.execute("""
            SELECT tt.day, tt.start_time, tt.end_time, tt.room,
                   c.name AS course_name, c.code, t.name AS teacher
            FROM timetable tt
            JOIN sections  s ON s.section_id=tt.section_id
            JOIN courses   c ON c.course_id=s.course_id
            JOIN teachers  t ON t.teacher_id=s.teacher_id
            JOIN enrollments e ON e.section_id=s.section_id
            WHERE e.student_id=%s
            ORDER BY FIELD(tt.day,'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'),
                     tt.start_time
        """, (sid,))
        timetable = cur.fetchall()
        cur.close(); db.close()
        return render_template('student/timetable.html', timetable=timetable)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('student/timetable.html', timetable=[])


@app.route('/student/fee')
@login_required
@role_required('student')
def student_fee():
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("SELECT student_id FROM students WHERE user_id=%s", (session['user_id'],))
        sid = cur.fetchone()['student_id']
        cur.execute("SELECT * FROM fee_records WHERE student_id=%s ORDER BY year DESC", (sid,))
        fees = cur.fetchall()
        cur.close(); db.close()
        return render_template('student/fee.html', fees=fees)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('student/fee.html', fees=[])


@app.route('/student/fee/voucher/<int:fee_id>')
@login_required
@role_required('student')
def download_voucher(fee_id):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT fr.fee_id, fr.semester, fr.year, fr.amount, fr.due_date, fr.status,
                   st.name, st.roll_no, p.name AS program, d.name AS dept
            FROM fee_records fr
            JOIN students st ON st.student_id=fr.student_id
            JOIN programs  p ON p.program_id=st.program_id
            JOIN departments d ON d.dept_id=p.dept_id
            WHERE fr.fee_id=%s AND st.user_id=%s
        """, (fee_id, session['user_id']))
        row = cur.fetchone()
        cur.close(); db.close()

        if not row:
            flash('Fee record not found.', 'error')
            return redirect(url_for('student_fee'))

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles  = getSampleStyleSheet()
        elems   = []

        h1 = ParagraphStyle('h1', fontSize=18, fontName='Helvetica-Bold', alignment=1, spaceAfter=6)
        h2 = ParagraphStyle('h2', fontSize=12, fontName='Helvetica', alignment=1,
                             textColor=colors.grey, spaceAfter=4)
        elems.append(Paragraph("NFC INSTITUTE OF ENGINEERING & TECHNOLOGY", h1))
        elems.append(Paragraph("Fee Payment Voucher", h2))
        elems.append(Spacer(1, 0.5*cm))
        elems.append(Paragraph(f"Voucher No: VCH-{row['fee_id']:06d}",
                                ParagraphStyle('vno', fontSize=13, fontName='Helvetica-Bold', alignment=1)))
        elems.append(Spacer(1, 0.5*cm))

        data = [
            ['Student Name', row['name'],       'Roll Number', row['roll_no']],
            ['Program',      row['program'],     'Department',  row['dept']],
            ['Semester',     str(row['semester']),'Year',       str(row['year'])],
            ['Due Date',     str(row['due_date']),'Status',     row['status'].upper()],
        ]
        t = Table(data, colWidths=[3.5*cm, 6*cm, 3.5*cm, 4*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0),(0,-1), colors.HexColor('#1e2535')),
            ('BACKGROUND', (2,0),(2,-1), colors.HexColor('#1e2535')),
            ('TEXTCOLOR',  (0,0),(0,-1), colors.white),
            ('TEXTCOLOR',  (2,0),(2,-1), colors.white),
            ('FONTNAME',   (0,0),(-1,-1),'Helvetica'),
            ('FONTNAME',   (0,0),(0,-1), 'Helvetica-Bold'),
            ('FONTNAME',   (2,0),(2,-1), 'Helvetica-Bold'),
            ('FONTSIZE',   (0,0),(-1,-1), 10),
            ('GRID',       (0,0),(-1,-1), 0.5, colors.grey),
            ('PADDING',    (0,0),(-1,-1), 8),
        ]))
        elems.append(t)
        elems.append(Spacer(1, 0.7*cm))

        amt = Table([['TOTAL FEE AMOUNT', f"Rs. {row['amount']:,.0f}"]],
                    colWidths=[9*cm, 8*cm])
        amt.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(0,0), colors.HexColor('#3b82f6')),
            ('BACKGROUND',(1,0),(1,0), colors.HexColor('#1e2535')),
            ('TEXTCOLOR', (0,0),(-1,-1), colors.white),
            ('FONTNAME',  (0,0),(-1,-1),'Helvetica-Bold'),
            ('FONTSIZE',  (0,0),(0,0), 12),
            ('FONTSIZE',  (1,0),(1,0), 16),
            ('ALIGN',     (0,0),(-1,-1),'CENTER'),
            ('VALIGN',    (0,0),(-1,-1),'MIDDLE'),
            ('PADDING',   (0,0),(-1,-1), 14),
        ]))
        elems.append(amt)
        elems.append(Spacer(1, 1*cm))

        ft = ParagraphStyle('ft', fontSize=9, textColor=colors.grey, alignment=1)
        elems.append(Paragraph("This is a computer generated voucher. No signature required.", ft))
        elems.append(Paragraph("Pay at any branch of Allied Bank or via online banking.", ft))

        doc.build(elems)
        buffer.seek(0)
        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f"attachment; filename=voucher_VCH-{row['fee_id']:06d}.pdf"
        return response

    except Exception as e:
        flash(f'Error generating PDF: {e}', 'error')
        return redirect(url_for('student_fee'))


# ══════════════════════════════════════════════
#  TEACHER
# ══════════════════════════════════════════════
@app.route('/teacher/dashboard')
@login_required
@role_required('teacher')
def teacher_dashboard():
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT t.*, d.name AS department FROM teachers t
            JOIN departments d ON d.dept_id=t.dept_id WHERE t.user_id=%s
        """, (session['user_id'],))
        teacher = cur.fetchone()
        cur.execute("SELECT * FROM vw_teacher_dashboard WHERE teacher_id=%s", (teacher['teacher_id'],))
        sections = cur.fetchall()
        cur.close(); db.close()
        return render_template('teacher/dashboard.html', teacher=teacher, sections=sections)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('teacher/dashboard.html', teacher={}, sections=[])


@app.route('/teacher/attendance/<int:section_id>', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def teacher_attendance(section_id):
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("SELECT teacher_id FROM teachers WHERE user_id=%s", (session['user_id'],))
        tid = cur.fetchone()['teacher_id']

        cur.execute("SELECT * FROM sections WHERE section_id=%s AND teacher_id=%s", (section_id, tid))
        if not cur.fetchone():
            flash('Access denied.', 'error')
            return redirect(url_for('teacher_dashboard'))

        if request.method == 'POST':
            date = request.form.get('date')
            for key, val in request.form.items():
                if key.startswith('status_'):
                    student_id = int(key.split('_')[1])
                    cur.execute("""
                        SELECT enrollment_id FROM enrollments
                        WHERE student_id=%s AND section_id=%s
                    """, (student_id, section_id))
                    row = cur.fetchone()
                    if row:
                        cur.execute("""
                            INSERT INTO attendance (enrollment_id, date, status)
                            VALUES (%s,%s,%s)
                            ON DUPLICATE KEY UPDATE status=%s, marked_at=NOW()
                        """, (row['enrollment_id'], date, val, val))
            db.commit()
            flash('Attendance saved!', 'success')

        today = dt.today()
        cur.execute("""
            SELECT st.student_id, st.roll_no, st.name AS student_name,
                   COALESCE(a.status,'not marked') AS todays_status,
                   fn_attendance_pct(e.enrollment_id) AS overall_pct
            FROM enrollments e
            JOIN students st ON st.student_id=e.student_id
            LEFT JOIN attendance a ON a.enrollment_id=e.enrollment_id AND a.date=%s
            WHERE e.section_id=%s ORDER BY st.roll_no
        """, (today, section_id))
        students = cur.fetchall()

        cur.execute("""
            SELECT c.name AS course_name, s.section_label, s.semester, s.year
            FROM sections s JOIN courses c ON c.course_id=s.course_id
            WHERE s.section_id=%s
        """, (section_id,))
        section_info = cur.fetchone()
        cur.close(); db.close()
        return render_template('teacher/attendance.html',
            students=students, section_id=section_id,
            section_info=section_info, today=today)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('teacher_dashboard'))


@app.route('/teacher/attendance/<int:section_id>/print')
@login_required
@role_required('teacher')
def print_attendance(section_id):
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT st.roll_no, st.name, a.date, a.status
            FROM enrollments e
            JOIN students st ON st.student_id=e.student_id
            LEFT JOIN attendance a ON a.enrollment_id=e.enrollment_id
            WHERE e.section_id=%s ORDER BY st.roll_no, a.date
        """, (section_id,))
        rows = cur.fetchall()

        cur.execute("""
            SELECT c.name AS course_name, c.code AS course_code, s.section_label,
                   s.semester, s.year, t.name AS teacher
            FROM sections s
            JOIN courses  c ON c.course_id=s.course_id
            JOIN teachers t ON t.teacher_id=s.teacher_id
            WHERE s.section_id=%s
        """, (section_id,))
        si = cur.fetchone()
        cur.close(); db.close()

        students = OrderedDict()
        dates = sorted(set(r['date'] for r in rows if r['date']))
        for r in rows:
            roll = r['roll_no']
            if roll not in students:
                students[roll] = {'name': r['name'], 'dates': {}}
            if r['date']:
                students[roll]['dates'][r['date']] = r['status']

        return render_template('teacher/print_attendance.html',
            students=students, dates=dates, section_info=si)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('teacher_dashboard'))


@app.route('/teacher/grades/<int:section_id>', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def teacher_grades(section_id):
    try:
        db  = get_db()
        cur = db.cursor()
        if request.method == 'POST':
            cur.execute("""
                INSERT INTO grades (enrollment_id, mid_marks, final_marks, assignment_marks)
                VALUES (%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE mid_marks=%s, final_marks=%s, assignment_marks=%s
            """, (request.form['enrollment_id'],
                  request.form.get('mid_marks',0), request.form.get('final_marks',0),
                  request.form.get('assignment_marks',0),
                  request.form.get('mid_marks',0), request.form.get('final_marks',0),
                  request.form.get('assignment_marks',0)))
            db.commit()
            flash('Grades updated!', 'success')

        cur.execute("""
            SELECT st.student_id, st.name AS student_name, st.roll_no, e.enrollment_id,
                   COALESCE(g.mid_marks,0) AS mid_marks,
                   COALESCE(g.final_marks,0) AS final_marks,
                   COALESCE(g.assignment_marks,0) AS assignment_marks,
                   COALESCE(g.total,0) AS total,
                   fn_letter_grade(COALESCE(g.total,0)) AS letter_grade
            FROM enrollments e
            JOIN students st ON st.student_id=e.student_id
            LEFT JOIN grades g ON g.enrollment_id=e.enrollment_id
            WHERE e.section_id=%s ORDER BY st.roll_no
        """, (section_id,))
        students = cur.fetchall()

        cur.execute("""
            SELECT c.name AS course_name, s.section_label, s.semester, s.year
            FROM sections s JOIN courses c ON c.course_id=s.course_id WHERE s.section_id=%s
        """, (section_id,))
        section_info = cur.fetchone()
        cur.close(); db.close()
        return render_template('teacher/grades.html',
            students=students, section_id=section_id, section_info=section_info)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('teacher_dashboard'))


@app.route('/teacher/announcements', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def teacher_announcements():
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("SELECT teacher_id FROM teachers WHERE user_id=%s", (session['user_id'],))
        tid = cur.fetchone()['teacher_id']

        if request.method == 'POST':
            cur.execute("""
                INSERT INTO announcements (teacher_id, section_id, title, body)
                VALUES (%s,%s,%s,%s)
            """, (tid, request.form['section_id'], request.form['title'], request.form['body']))
            db.commit()
            flash('Announcement posted!', 'success')

        cur.execute("""
            SELECT s.section_id, c.name AS course_name, s.section_label
            FROM sections s JOIN courses c ON c.course_id=s.course_id WHERE s.teacher_id=%s
        """, (tid,))
        sections = cur.fetchall()

        cur.execute("""
            SELECT a.*, c.name AS course_name, s.section_label
            FROM announcements a
            JOIN sections s ON s.section_id=a.section_id
            JOIN courses  c ON c.course_id=s.course_id
            WHERE a.teacher_id=%s ORDER BY a.created_at DESC
        """, (tid,))
        announcements = cur.fetchall()
        cur.close(); db.close()
        return render_template('teacher/announcements.html',
            sections=sections, announcements=announcements)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('teacher/announcements.html', sections=[], announcements=[])


# ══════════════════════════════════════════════
#  ADMIN
# ══════════════════════════════════════════════
@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM students")
        total_students = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) AS total FROM teachers")
        total_teachers = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) AS total FROM courses")
        total_courses  = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) AS total FROM fee_records WHERE status!='paid'")
        pending_fees   = cur.fetchone()['total']
        cur.execute("SELECT * FROM vw_shortage_alerts LIMIT 10")
        shortages      = cur.fetchall()
        cur.execute("SELECT * FROM vw_admin_student_list ORDER BY roll_no LIMIT 10")
        recent_students= cur.fetchall()
        cur.close(); db.close()
        return render_template('admin/dashboard.html',
            total_students=total_students, total_teachers=total_teachers,
            total_courses=total_courses, pending_fees=pending_fees,
            shortages=shortages, recent_students=recent_students)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('admin/dashboard.html',
            total_students=0, total_teachers=0, total_courses=0,
            pending_fees=0, shortages=[], recent_students=[])


@app.route('/admin/students', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_students():
    try:
        db  = get_db()
        cur = db.cursor()
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'add':
                cur.callproc('sp_add_student', [
                    request.form['email'], request.form['password'],
                    request.form['name'],  request.form['roll_no'],
                    int(request.form['program_id']),
                    request.form['batch'], int(request.form['semester'])
                ])
                db.commit()
                flash('Student added!', 'success')
            elif action == 'delete':
                sid = request.form.get('student_id')
                cur.execute("SELECT user_id FROM students WHERE student_id=%s", (sid,))
                uid = cur.fetchone()['user_id']
                cur.execute("DELETE FROM students WHERE student_id=%s", (sid,))
                cur.execute("DELETE FROM users WHERE user_id=%s", (uid,))
                db.commit()
                flash('Student deleted.', 'success')

        cur.execute("SELECT * FROM vw_admin_student_list ORDER BY roll_no")
        students = cur.fetchall()
        cur.execute("SELECT * FROM programs")
        programs = cur.fetchall()
        cur.close(); db.close()
        return render_template('admin/students.html', students=students, programs=programs)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('admin/students.html', students=[], programs=[])


@app.route('/admin/search')
@login_required
@role_required('admin')
def admin_search():
    q = request.args.get('q', '').strip()
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT st.student_id, st.name, st.roll_no, st.batch, st.semester,
                   p.name AS program, u.email
            FROM students st
            JOIN programs p ON p.program_id=st.program_id
            JOIN users    u ON u.user_id=st.user_id
            WHERE st.name LIKE %s OR st.roll_no LIKE %s OR u.email LIKE %s LIMIT 20
        """, (f'%{q}%', f'%{q}%', f'%{q}%'))
        results = cur.fetchall()
        cur.close(); db.close()
        return jsonify(results)
    except:
        return jsonify([])


@app.route('/admin/teachers', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_teachers():
    try:
        db  = get_db()
        cur = db.cursor()
        if request.method == 'POST':
            cur.callproc('sp_add_teacher', [
                request.form['email'], request.form['password'],
                request.form['name'],  int(request.form['dept_id']),
                request.form['designation']
            ])
            db.commit()
            flash('Teacher added!', 'success')

        cur.execute("""
            SELECT t.teacher_id, t.name, t.designation, t.phone,
                   d.name AS department, u.email
            FROM teachers t
            JOIN departments d ON d.dept_id=t.dept_id
            JOIN users u ON u.user_id=t.user_id
        """)
        teachers = cur.fetchall()
        cur.execute("SELECT * FROM departments")
        departments = cur.fetchall()
        cur.close(); db.close()
        return render_template('admin/teachers.html', teachers=teachers, departments=departments)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('admin/teachers.html', teachers=[], departments=[])


@app.route('/admin/fees', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_fees():
    try:
        db  = get_db()
        cur = db.cursor()
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'mark_paid':
                cur.execute("UPDATE fee_records SET status='paid' WHERE fee_id=%s",
                            (request.form['fee_id'],))
                db.commit()
                flash('Fee marked as paid!', 'success')
            elif action == 'add_fee':
                cur.execute("""
                    INSERT INTO fee_records (student_id, semester, year, amount, due_date)
                    VALUES (%s,%s,%s,%s,%s)
                """, (request.form['student_id'], request.form['semester'],
                      request.form['year'], request.form['amount'], request.form['due_date']))
                db.commit()
                flash('Fee record added!', 'success')

        cur.execute("""
            SELECT fr.*, st.name AS student_name, st.roll_no
            FROM fee_records fr JOIN students st ON st.student_id=fr.student_id
            ORDER BY fr.year DESC
        """)
        fees = cur.fetchall()
        cur.execute("SELECT student_id, name, roll_no FROM students ORDER BY roll_no")
        students = cur.fetchall()
        cur.close(); db.close()
        return render_template('admin/fees.html', fees=fees, students=students)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('admin/fees.html', fees=[], students=[])



# ══════════════════════════════════════════════
#  ADMIN COURSES & SECTIONS
# ══════════════════════════════════════════════
@app.route('/admin/courses', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_courses():
    try:
        db = get_db()
        cur = db.cursor()

        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'add_course':
                cur.execute("""
                    INSERT INTO courses (code, name, dept_id, credit_hours, total_marks, mid_weight, final_weight, assign_weight)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, (request.form['code'], request.form['name'], int(request.form['dept_id']),
                      int(request.form.get('credit_hours',3)), int(request.form.get('total_marks',100)),
                      int(request.form.get('mid_weight',30)), int(request.form.get('final_weight',50)),
                      int(request.form.get('assign_weight',20))))
                db.commit()
                flash('Course added!', 'success')
            elif action == 'delete_course':
                cur.execute("DELETE FROM courses WHERE course_id=%s", (request.form['course_id'],))
                db.commit()
                flash('Course deleted.', 'success')

        cur.execute("SELECT c.*, d.name AS department FROM courses c JOIN departments d ON d.dept_id=c.dept_id ORDER BY c.code")
        courses = cur.fetchall()
        cur.execute("SELECT * FROM departments ORDER BY name")
        departments = cur.fetchall()
        cur.close(); db.close()
        return render_template('admin/courses.html', courses=courses, departments=departments)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('admin/courses.html', courses=[], departments=[])


@app.route('/admin/sections', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_sections():
    try:
        db = get_db()
        cur = db.cursor()

        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'add_section':
                cur.execute("""
                    INSERT INTO sections (course_id, teacher_id, section_label, semester, year, room, max_students)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (request.form['course_id'], request.form['teacher_id'],
                      request.form['section_label'], request.form['semester'],
                      request.form['year'], request.form.get('room',''),
                      int(request.form.get('max_students',50))))
                db.commit()
                flash('Section assigned successfully!', 'success')
            elif action == 'delete_section':
                cur.execute("DELETE FROM sections WHERE section_id=%s", (request.form['section_id'],))
                db.commit()
                flash('Section deleted.', 'success')

        cur.execute("""
            SELECT s.*, c.code AS course_code, c.name AS course_name, 
                   t.name AS teacher_name, d.name AS department
            FROM sections s
            JOIN courses c ON c.course_id = s.course_id
            JOIN teachers t ON t.teacher_id = s.teacher_id
            JOIN departments d ON d.dept_id = c.dept_id
            ORDER BY s.year DESC, s.semester, c.code
        """)
        sections = cur.fetchall()
        cur.execute("SELECT * FROM courses ORDER BY code")
        courses = cur.fetchall()
        cur.execute("SELECT t.teacher_id, t.name, d.name AS department FROM teachers t JOIN departments d ON d.dept_id=t.dept_id ORDER BY t.name")
        teachers = cur.fetchall()
        cur.close(); db.close()
        return render_template('admin/sections.html', sections=sections, courses=courses, teachers=teachers)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('admin/sections.html', sections=[], courses=[], teachers=[])


@app.route('/admin/enrollments', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_enrollments():
    try:
        db = get_db()
        cur = db.cursor()

        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'enroll':
                cur.execute("""
                    INSERT INTO enrollments (student_id, section_id)
                    VALUES (%s,%s)
                """, (request.form['student_id'], request.form['section_id']))
                db.commit()
                flash('Student enrolled!', 'success')
            elif action == 'drop':
                cur.execute("UPDATE enrollments SET status='dropped' WHERE enrollment_id=%s", (request.form['enrollment_id'],))
                db.commit()
                flash('Enrollment dropped.', 'success')

        # Get all active enrollments with details
        cur.execute("""
            SELECT e.*, st.name AS student_name, st.roll_no,
                   c.code AS course_code, c.name AS course_name,
                   s.section_label, s.semester, s.year,
                   t.name AS teacher_name
            FROM enrollments e
            JOIN students st ON st.student_id = e.student_id
            JOIN sections s ON s.section_id = e.section_id
            JOIN courses c ON c.course_id = s.course_id
            JOIN teachers t ON t.teacher_id = s.teacher_id
            WHERE e.status = 'active'
            ORDER BY s.year DESC, s.semester, c.code, st.roll_no
            LIMIT 100
        """)
        enrollments = cur.fetchall()

        # Get students and sections for dropdowns
        cur.execute("SELECT student_id, name, roll_no FROM students WHERE status='active' ORDER BY roll_no")
        students = cur.fetchall()
        cur.execute("""
            SELECT s.section_id, c.code, c.name AS course_name, s.section_label, s.semester, s.year, t.name AS teacher_name
            FROM sections s
            JOIN courses c ON c.course_id = s.course_id
            JOIN teachers t ON t.teacher_id = s.teacher_id
            ORDER BY s.year DESC, s.semester, c.code
        """)
        sections = cur.fetchall()
        cur.close(); db.close()
        return render_template('admin/enrollments.html', enrollments=enrollments, students=students, sections=sections)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('admin/enrollments.html', enrollments=[], students=[], sections=[])

# ══════════════════════════════════════════════
#  RUN
# ══════════════════════════════════════════════
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=False)

@app.route('/init-db')
def init_db():
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("SHOW TABLES")
        tables = cur.fetchall()
        cur.close()
        db.close()
        return f"Connected! Tables: {tables}"
    except Exception as e:
        return f"Error: {e}"
