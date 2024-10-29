# app.py
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
#from dotenv import load_dotenv
from firebase_config import db
from google_drive import upload_file
from forms import SelectionForm, NewSubjectForm, UploadNoteForm

# Load environment variables from .env file
#load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'uploads'

bootstrap = Bootstrap5(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SelectionForm()
    if form.validate_on_submit():
        semester = form.semester.data
        branch = form.branch.data
        return redirect(url_for('subjects', semester=semester, branch=branch))
    return render_template('index.html', form=form)

@app.route('/subjects/<semester>/<branch>', methods=['GET', 'POST'])
def subjects(semester, branch):
    form = NewSubjectForm()
    if form.validate_on_submit():
        subject = form.subject.data
        db.collection('sem-branch').document(f"{semester}-{branch}").collection('subjects').document(subject).set({
            'name': subject
        })
        return redirect(url_for('subjects', semester=semester, branch=branch))
    
    subjects_ref = db.collection('sem-branch').document(f"{semester}-{branch}").collection('subjects')
    subjects = [doc.id for doc in subjects_ref.stream()]

    return render_template('subjects.html', semester=semester, branch=branch, subjects=subjects, form=form)

@app.route('/units/<semester>/<branch>/<subject>', methods=['GET', 'POST'])
def units(semester, branch, subject):
    units = ['Unit 1', 'Unit 2', 'Unit 3', 'Unit 4']
    return render_template('units.html', semester=semester, branch=branch, subject=subject, units=units)

@app.route('/notes/<semester>/<branch>/<subject>/<unit>', methods=['GET', 'POST'])
def notes(semester, branch, subject, unit):
    form = UploadNoteForm()
    if form.validate_on_submit():
        file = form.file.data

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(file_path)
        content_type = file.content_type
        file_link = upload_file(file_path, content_type)
        note_name = form.note_name.data
        db.collection('sem-branch').document(f"{semester}-{branch}").collection('subjects').document(subject).collection('units').document(unit).collection('notes').add({
            'name': note_name,
            'file_link': file_link
        })
        os.remove(file_path)
        return redirect(url_for('notes', semester=semester, branch=branch, subject=subject, unit=unit))
    
    notes_ref = db.collection('sem-branch').document(f"{semester}-{branch}").collection('subjects').document(subject).collection('units').document(unit).collection('notes')
    notes = [{'name': doc.get('name'), 'file_link': doc.get('file_link')} for doc in notes_ref.stream()]

    return render_template('notes.html', semester=semester, branch=branch, subject=subject, unit=unit, notes=notes, form=form)

if __name__ == '__main__':
    app.run(debug=False)