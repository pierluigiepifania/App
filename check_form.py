from wtforms import Form, IntegerField, StringField, validators

class SearchForm(Form):
    to_search = IntegerField('to_search', [validators.DataRequired()])

class RegisterForm(Form):
    email = StringField('email', [validators.DataRequired()])
    username = StringField('username', [validators.DataRequired()])
    password = StringField('password', [validators.DataRequired()])

class LoginForm(Form):
    username_log = StringField('username_log', [validators.DataRequired()])
    password_log = StringField('password_log', [validators.DataRequired()])
    
class RemoveUserForm(Form):
    user = StringField('user', [validators.DataRequired()])

class RemoveTimeForm(Form):
    orario_to_delete = StringField('orario_to_delete', [validators.DataRequired()])

class AddTimeForm(Form):
    orario = StringField('orario', [validators.DataRequired()])

class RemovePrenotationForm(Form):
    orario_prenotato = StringField('orario', [validators.DataRequired()])
    code_to_remove = StringField('code_to_remove', [validators.DataRequired()])

class AddAdminForm(Form):
    add_admin = StringField('add_admin', [validators.DataRequired()])
    add_admin_pwd = StringField('add_admin_pwd', [validators.DataRequired()])
    add_admin_mail = StringField('add_admin_mail', [validators.DataRequired()])

class RemoveAdminForm(Form):
    rem_admin = StringField('rem_admin', [validators.DataRequired()])