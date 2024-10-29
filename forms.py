from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, FileField, SubmitField
from wtforms.validators import DataRequired

class SelectionForm(FlaskForm):
    semester = SelectField('Semester', choices=[
        ('', 'Semester'),
        ('1', 'Sem 1'),
        ('2', 'Sem 2'),
        ('3', 'Sem 3'),
        ('4', 'Sem 4'),
        ('5', 'Sem 5'),
        ('6', 'Sem 6'),
        ('7', 'Sem 7'),
        ('8', 'Sem 8')
    ], validators=[DataRequired()])
    branch = SelectField('Branch', choices=[
        ('', 'Branch'),
        ('computer', 'Computer'),
        ('it', 'IT'),
        ('ene', 'ENE'),
        ('etc', 'ETC'),
        ('civil', 'Civil'),
        ('mech', 'Mech')
    ], validators=[DataRequired()])

class NewSubjectForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    submit = SubmitField('Add Subject')

class UploadNoteForm(FlaskForm):
    note_name = StringField('Note Name', validators=[DataRequired()])
    file = FileField('Upload Note', validators=[DataRequired()])
    submit = SubmitField('Upload')