# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
# from dotenv import load_dotenv
from firebase_config import db
from google_drive import upload_file, drive_service
from forms import SelectionForm, NewSubjectForm, UploadNoteForm, UploadLinkForm

# Load environment variables from .env file
# load_dotenv()

#temporary way to store sem 5 gdrive link
# sem5_link = 'https://drive.google.com/drive/folders/1xVrgKvfnt6pGlLCZkF_laqJLqrqwlore'

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
    subjects = {doc.id: doc.get('name') for doc in subjects_ref.stream()}
    return render_template('subjects.html', semester=semester, branch=branch, subjects=subjects, form=form)

@app.route('/edit_subject/<semester>/<branch>/<subject>', methods=['POST'])
def edit_subject(semester, branch, subject):
    new_subject_name = request.form['new_subject_name']
    # Update the subject name in Firestore
    subject_ref = db.collection('sem-branch').document(f"{semester}-{branch}").collection('subjects').document(subject)
    subject_ref.update({'name': new_subject_name})
    return redirect(url_for('subjects', semester=semester, branch=branch))

@app.route('/delete_subject')
def delete_subject():
    semester = request.args.get('semester')
    branch = request.args.get('branch')
    subject = request.args.get('subject')
    # Delete the subject from Firestore
    subject_ref = db.collection('sem-branch').document(f"{semester}-{branch}").collection('subjects').document(subject)
    subject_ref.delete()
    return redirect(url_for('subjects', semester=semester, branch=branch))

@app.route('/units/<semester>/<branch>/<subject>', methods=['GET', 'POST'])
def units(semester, branch, subject):
    units = ['Unit 1', 'Unit 2', 'Unit 3', 'Unit 4', 'PYQ soln']
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
    notes = [{'id': doc.id, 'name': doc.get('name'), 'file_link': doc.get('file_link')} for doc in notes_ref.stream()]

    return render_template('notes.html', semester=semester, branch=branch, subject=subject, unit=unit, notes=notes, form=form)

@app.route('/edit_note/<semester>/<branch>/<subject>/<unit>/<note>', methods=['POST'])
def edit_note(semester, branch, subject, unit, note):
    new_note_name = request.form['new_note_name']
    # Update the note name in Firestore
    note_ref = db.collection('sem-branch').document(f"{semester}-{branch}").collection('subjects').document(subject).collection('units').document(unit).collection('notes').document(note)
    note_ref.update({'name': new_note_name})
    return redirect(url_for('notes', semester=semester, branch=branch, subject=subject, unit=unit))

@app.route('/delete_note')
def delete_note():
    semester = request.args.get('semester')
    branch = request.args.get('branch')
    subject = request.args.get('subject')
    unit = request.args.get('unit')
    note = request.args.get('note')
    
    # Get the note document
    note_ref = db.collection('sem-branch').document(f"{semester}-{branch}").collection('subjects').document(subject).collection('units').document(unit).collection('notes').document(note)
    note_doc = note_ref.get()
    
    if note_doc.exists:
        # Get the file link from the note document
        file_link = note_doc.get('file_link')
        # Extract the file ID from the file link
        file_id = file_link.split('/')[-2]
        
        # Delete the file from Google Drive
        drive_service.files().delete(fileId=file_id).execute()
        
        # Delete the note from Firestore
        note_ref.delete()
    
    return redirect(url_for('notes', semester=semester, branch=branch, subject=subject, unit=unit))

# @app.route('/links/<semester>/<branch>', methods=['GET', 'POST'])
# def links(semester, branch):
#     units = ['Unit 1', 'Unit 2', 'Unit 3', 'Unit 4', 'PYQ soln']
#     return render_template('units.html', semester=semester, branch=branch, units=units)


@app.route('/links/<semester>/<branch>', methods=['GET', 'POST'])
def links(semester, branch):
    form = UploadLinkForm()
    if form.validate_on_submit():
        link = form.link.data
        link_name = form.link_name.data
        db.collection('sem-branch').document(f"{semester}-{branch}").collection('links').add({
            'name': link_name,
            'folder_link': link
        })
        return redirect(url_for('links', semester=semester, branch=branch))
    
    links_ref = db.collection('sem-branch').document(f"{semester}-{branch}").collection('links')
    links = [{'id': doc.id, 'name': doc.get('name'), 'file_link': doc.get('folder_link')} for doc in links_ref.stream()]

    return render_template('links.html', semester=semester, branch=branch, links=links, form=form)


@app.route('/edit_link/<semester>/<branch>/<link>', methods=['POST'])
def edit_link(semester, branch, link):
    new_link_name = request.form['new_link_name']
    # Update the link name in Firestore
    link_ref = db.collection('sem-branch').document(f"{semester}-{branch}").collection('links').document(link)
    link_ref.update({'name': new_link_name})
    return redirect(url_for('links', semester=semester, branch=branch))

@app.route('/delete_link')
def delete_link():
    semester = request.args.get('semester')
    branch = request.args.get('branch')
    link = request.args.get('link')
    
    # Get the link document
    link_ref = db.collection('sem-branch').document(f"{semester}-{branch}").collection('links').document(link)
    link_doc = link_ref.get()
    
    if link_doc.exists:
        # Get the file link from the link document
        file_link = link_doc.get('folder_link')
        link_ref.delete()
    
    return redirect(url_for('links', semester=semester, branch=branch))


if __name__ == '__main__':
    app.run(debug=False)