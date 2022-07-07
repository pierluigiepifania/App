import urllib
from check_form import *

from flask import Flask, json, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import null

from flask_session import Session

##### CONNESSIONE CON AZURE SQL DATABASE ###############

server = 'tcp:bookingserver.database.windows.net'
database = 'bookingdatabase'
username = 'server'
password = 'Test1234'
driver = '{ODBC Driver 17 for SQL Server}'

odbc_str = 'DRIVER='+driver+';SERVER='+server+',1433;UID='+username+';DATABASE='+ database + ';PWD='+ password + \
            ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
connect_str = 'mssql+pyodbc:///?odbc_connect=' + urllib.parse.quote_plus(odbc_str)

##### CONFIGURAZIONE INIZIALE DI FLASK E SQLALCHEMY ###############

app = Flask(__name__)  

app.config['SQLALCHEMY_DATABASE_URI'] = connect_str
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

_db = SQLAlchemy(app)

##### MODELS ############### 

class Users(_db.Model):
    id = _db.Column(_db.Integer, primary_key=True)
    username = _db.Column(_db.String (30))
    password = _db.Column(_db.String (30))
    email = _db.Column(_db.String (30))
    ruolo = _db.Column(_db.String (30))
    long = _db.Column(_db.String (30))
    lat = _db.Column(_db.String (30)) 

    def __init__( self, username, password, email, ruolo, long, lat):
       self.username = username
       self.password = password
       self.email = email
       self.ruolo = ruolo
       self.long = long
       self.lat = lat

class Schedule(_db.Model):
    id = _db.Column(_db.Integer, primary_key=True)
    orario = _db.Column(_db.String (30))
    code_manag = _db.Column(_db.Integer)
    disponibile = _db.Column(_db.Boolean, default = True)

    def __init__( self, orario, code_manag):
       self.orario = orario
       self.code_manag = code_manag

class Prenotation(_db.Model):
    id = _db.Column(_db.Integer, primary_key=True)
    orario = _db.Column(_db.String (30))
    username = _db.Column(_db.String (30))
    code_manag = _db.Column(_db.Integer)
    
    def __init__( self, orario, username, code_manag):
       self.orario = orario
       self.username = username
       self.code_manag = code_manag

##### TOOL ###############

def check_superuser():
    already = Users.query.filter_by(username = "superuser").first()
    if already is None:
        _new = Users("superuser", "superuser", "superuser", "superuser", 0, 0)
        _db.session.add(_new)
        _db.session.commit()

##### CONFIGURAZIONE SESSIONE ###############

_db.create_all()
_db.session.commit()
check_superuser()

app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "mysecretkey"
Session(app)

##### DEFINIZIONE DELLE ROUTE DI FLASK ###############

@app.route("/") 
def index():
    if 'user' in session:
        flag = True
        return render_template('index.html', flag=flag)
    flag = False
    return render_template('index.html', flag = flag)

@app.route('/login_register')
def login_register():
    return render_template('login_register.html')

@app.route('/mappa')
def open_map():
    return render_template('AzureMap.html')

@app.route('/mappaRegister')
def open_map_register():
    return render_template('AzureMapSignup.html')

@app.route('/coordinates', methods=['POST'])
def get_coordinates():
    session['long'] = request.json.get('long')
    session['lat'] = request.json.get('lat')
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@app.route('/show_list')
def show_list():
    element = Users.query.filter_by(long = session['long'], lat = session['lat']).first()
    flag = True
    if element is not None:
        to_search = element.id
        data = Schedule.query.filter_by(code_manag = to_search, disponibile = True).all()
        session['data'] = data
        if not data:
            error = "Il codice inserito non ha una corrispondenza, inserire un altro codice"
            if 'user' in session:
                return render_template('index.html', flag=flag, error = error)
            flag = False
            return render_template('index.html', flag = flag, error=error)
        session['data'] = data
        return render_template('show_turn.html', data = data)
    error = "Non sono presenti liste!"
    if 'user' in session:
        return render_template('index.html', flag=flag, error = error)
    flag = False
    return render_template('index.html', flag = flag, error=error)

@app.route('/coordinates_register', methods=['POST'])
def get_coordinates_register():
    session['long'] = request.json.get('long')
    session['lat'] = request.json.get('lat')
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@app.route('/logged/', methods=['POST'])
def logged():
    form = LoginForm(request.form)
    if request.method=='POST' and form.validate():
        user = request.form["username_log"].lower()
        pwd = request.form["password_log"]
        logged = Users.query.filter_by(username = user, password = pwd).first()
        if logged is not None:
            ruolo = logged.ruolo
            session['ruolo'] = ruolo
            session['code'] = logged.id
            session['user'] = user
            return redirect ("/")
        error = "Nessuna corrispondenza"
        return render_template ("login_register.html", error = error)
    error = "inserire valori correti per username e password"
    return render_template ("login_register.html", error = error)    

@app.route('/signUp/', methods=['POST'])
def signUp():
    form = RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        ruolo = "utente"
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        already = Users.query.filter_by(username = username).first()
        if already is not None:
            error = "Nome utente già utilizzato"
            return render_template ( "login_register.html", error = error)        
        register = Users(username, email, password, ruolo, 0, 0)
        _db.session.add(register)
        _db.session.commit()
        return render_template ( "success.html" )
    error = "Inserire tutti i parametri"
    return render_template ( "login_register.html", error = error)

@app.route("/Manager_RegisterTemplate") 
def register_template():
    return render_template ( "signup_register.html")

@app.route('/signUpManager/', methods=['POST'])
def signUpManager():
    form = RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        ruolo = "azienda"
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        already = Users.query.filter_by(username = username).first()
        if already is not None:
            error = "Nome utente già utilizzato"
            return render_template ( "signup_register.html", error = error)  
        long = str(session['long'])
        lat = str(session['lat'])
        register = Users(username, email, password, ruolo, long, lat)
        _db.session.add(register)
        _db.session.commit()
        return render_template ( "success.html" )
    error = "Inserire tutti i parametri"
    return render_template ( "signup_register.html", error = error)

@app.route('/profilo/')
def profilo():
    ruolo = session["ruolo"]
    code = session ["code"]
    user = session ["user"]
    if ruolo == 'utente':
        prenotation = Prenotation.query.filter_by(username = user).all()
        session['data'] = prenotation
        return render_template("user_profile.html", data = prenotation)
    elif ruolo == 'azienda':
        orari = Schedule.query.filter_by(code_manag = code).all()
        prenotation = Prenotation.query.filter_by(code_manag = session['code']).all()
        if not prenotation:
            session['data'] = orari
            return render_template("host_profile.html", id = code, data = orari)
        session['data'] = orari
        return render_template("host_profile.html", id = code, data = orari, prenotation = prenotation)
    elif ruolo == 'admin':
        users = Users.query.all()
        session['data'] = users
        return render_template("admin_profile.html", users = users)
    elif ruolo == 'superuser':
        admin = Users.query.filter_by(ruolo='admin').all()
        session['data'] = admin
        return render_template("super_user.html", admin = admin)
    return redirect("/")
    
@app.route('/turn', methods=['POST'])
def turn_page():
    form = SearchForm(request.form)
    flag = True
    if request.method=='POST' and form.validate():
        to_search=request.form['to_search']
        data = Schedule.query.filter_by(code_manag = to_search, disponibile = True).all()
        if not data:
            error = "Il codice inserito non ha una corrispondenza, inserire un altro codice"
            if 'user' in session:
                return render_template('index.html', flag=flag, error = error)
            flag = False
            return render_template('index.html', flag = flag, error=error)
        session['data'] = data
        return render_template('show_turn.html', data = data)
    error = "Il codice inserito non è del formato corretto"
    if 'user' in session:
        return render_template('index.html', flag=flag, error = error)
    flag = False
    return render_template('index.html', flag = flag, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect ('/')

@app.route('/removetime', methods=['POST'])
def remove_time():
    form = RemoveTimeForm(request.form)
    if request.method=='POST' and form.validate():
        code = session["code"]
        orario = request.form["orario_to_delete"]
        to_delete = Schedule.query.filter_by( orario = orario, code_manag = code ).delete()
        if to_delete:
            _db.session.commit()
            return redirect('/profilo/')
        error = "Nessuna corrispondenza"
        return render_template ("host_profile.html", data = session['data'], error = error)
    error = "Inserire un valore corretto"
    return render_template ("host_profile.html", data = session['data'], error = error)

@app.route('/addtime', methods=['POST'])
def add_time():
    form = AddTimeForm(request.form)
    if request.method=='POST' and form.validate():
        code = session["code"]
        orario = request.form["orario"]
        alredy = Schedule.query.filter_by(code_manag = code, orario = orario).first()
        if alredy is None:
            _new = Schedule(orario, code)
            _db.session.add(_new)
            _db.session.commit()
            return redirect('/profilo/')
        error = "Orario già presente"
        return render_template ("host_profile.html", data = session['data'], error = error)
    error = "Inserire un valore corretto"
    return render_template ("host_profile.html", data = session['data'], error = error)

@app.route('/removeuser', methods=['POST'])
def remove_user():
    form = RemoveUserForm(request.form)
    if request.method=='POST' and form.validate():
        user = request.form['user']
        to_delete = Users.query.filter_by(username = user).first()
        if to_delete is None:
            error = "Utente non presente"
            return render_template ("admin_profile.html", users = session['data'], error = error)
        elif to_delete.ruolo == 'superuser' or to_delete.ruolo == 'admin':
            error = "Non hai l'accesso a questa funzione"
            return render_template ("admin_profile.html", users = session['data'], error = error)
        to_delete = Users.query.filter_by(username = user).delete()
        if to_delete:
            _db.session.commit()
            return redirect('/profilo/')
    error = "Inserire un username corretto"
    return render_template ("admin_profile.html", users = session['data'], error = error)

@app.route('/removeprenotation', methods=['POST'])
def remove_prenotation():
    form = RemovePrenotationForm(request.form)
    if request.method=='POST' and form.validate():
        orario = request.form['orario_prenotato']
        code = request.form['code_to_remove']
        user = session['user']
        to_delete = Prenotation.query.filter_by( username = user, orario = orario, code_manag = code ).delete()
        if to_delete:
            Schedule.query.filter_by( code_manag = code, orario = orario ).update({'disponibile' : True})
            _db.session.commit()
            return redirect('/profilo/')
        error = "Nessuna corrispondenza, riprova"
        return render_template ("user_profile.html", data = session['data'], error = error)
    error = "Inserire un valore corretto"
    return render_template ("user_profile.html", data = session['data'], error = error)

@app.route('/addprenotation', methods=['POST'])
def add_prenotation():
    ruolo = session['ruolo']
    if ruolo != 'utente':
        error = 'Non sei abilitato a prenotare un turno'
        return render_template ('show_turn.html', data = session['data'], error = error)
    orario = request.form['orario_pren']
    code = request.form['code_pren']
    user = session["user"]
    _new = Prenotation(orario, user, code)
    Schedule.query.filter_by(code_manag = code, orario = orario).update({'disponibile' : False})
    _db.session.add(_new)
    _db.session.commit()
    return redirect('/profilo/')

@app.route('/addadmin', methods=['POST'])
def add_admin():
    form = AddAdminForm(request.form)
    if request.method=='POST' and form.validate():
        user = request.form["add_admin"]
        pwd = request.form["add_admin_pwd"]
        mail = request.form["add_admin_mail"]
        alredy = Users.query.filter_by(username = user).first()
        if alredy is None:
            _new = Users(user, pwd, mail, "admin",0,0)
            _db.session.add(_new)
            _db.session.commit()
            return redirect('/profilo/')
        error = "Admin già presente"
        return render_template ("super_user.html", data = session['data'], error = error)
    error = "Inserire un valore corretto"
    return render_template ("super_user.html", data = session['data'], error = error)

@app.route('/removeadmin', methods=['POST'])
def remove_admin():
    form = RemoveAdminForm(request.form)
    if request.method=='POST' and form.validate():
        admin = request.form['rem_admin']
        to_delete = Users.query.filter_by(username = admin).delete()
        if to_delete:
            _db.session.commit()
            return redirect('/profilo/')
        error = "Admin non trovato"
        return render_template ("asuper_user.html", users = session['data'], error = error)
    error = "Inserire un username corretto"
    return render_template ("super_user.html", users = session['data'], error = error)

##### MAIN ###############

if __name__ == '__main__': 
    app.run()

