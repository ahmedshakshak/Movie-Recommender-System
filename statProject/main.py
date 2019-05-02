import flask
import pyodbc
import requests
import ML
from dominate.tags import code
from flask import Flask, render_template, url_for, flash, redirect, request
from Forms import *
from flask_bootstrap import Bootstrap

global userId

def HomeForFirstVisit():
    MoviesIMDB = ML.getMoviesImmdbID()
    x=[]
    for i in range(20):
        r = requests.get(
            'http://www.omdbapi.com/?i=' + 'tt' + str(MoviesIMDB[i]) + '&apikey=765f0331'
        )
        x.append( r.json())

    return x

def requestJson(imdb):
    r = requests.get(
        'http://www.omdbapi.com/?i=' + str(imdb) + '&apikey=ce6485b0'
    )
    return r.json()

def jsonRequests(imdb):
    x = []
    for id in imdb:
        r = requests.get(
            'http://www.omdbapi.com/?i=' + 'tt' + str(id) + '&apikey=ce6485b0'
        )
        x.append(r.json())
    return x

def insertuSER(email, password, username, confirmationPassword ):
    users = db.execute(''' select * from [User] ''').fetchall()
    db.commit()
    for user in users:
        if user.email == email:
            return 0
    if '\'' in email:
        return 0
    if password != confirmationPassword:
        return 1
    db.execute(f'''insert into [User] (email, [password], Username) values ('{email}', '{password}', '{username}');''')
    db.commit()
    return 2


def ifIsHasMail(email, password):
    global userId
    if '\'' in email:
        return 0
    user = db.execute(f''' SELECT * FROM [User] WHERE email LIKE '{email}' ; ''').fetchone()
    if user is None:
        return 0
    if user.password == password:
        user.bio = "  Empty"
        userId = str(user.UserID)
        return 1

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

db = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                    """Server=DESKTOP-LBSH99L\SQL;"""
                    "Database=Statistics;"
                    "Trusted_Connection=yes;")


global islogin
global email
email = ""
islogin="false"


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
@app.route("/home/<string:movieImdbId>", methods=['GET', 'POST'])
def home(movieImdbId = ''):
    global islogin
    global userId
    if movieImdbId != '':
        ML.addFavouriteMove(userId, movieImdbId)
    search = ""
    movies = []
    print(request.method)
    if request.method == 'POST':
        search = request.form['search']
        movies = jsonRequests(ML.searchMovie(search))
    else:
        movies = HomeForFirstVisit()

    if islogin == "false":
        return render_template('home.html', logged="false", movies = movies, rate = "-1")
    else:
        if ML.isUserRated(userId):
            movies = ML.reccomendMoviesFor(userId)
            movies = jsonRequests(movies)
        return render_template('home.html', logged="true", movies = movies, rate = "-1")

@app.route("/recommendMovies/<string:movieTitle>", methods=['GET', 'POST'])
def recommendMovies(movieTitle = ''):
    global islogin
    global userId
    movies = jsonRequests(ML.searchMovie(movieTitle))
    print(movies)
    return render_template('recommendedMovies.html', logged="true", movies = movies, rate = "-1")


@app.route("/movie/<string:imdbID>", methods=['GET', 'POST'])
def movie(imdbID = ''):
    global islogin
    global userId
    rate = ""
    if imdbID != "" and request.method == 'POST':
        rate = request.form['RateID']
    movie = requestJson(imdbID)

    if imdbID != '' and (rate == '1' or rate == '2' or rate == '3' or rate == '4' or rate == '5'):
        saveUserRate(imdbID, rate)
    if islogin == 'false':
        return render_template('movie.html', logged="false", movie=movie)
    return render_template('movie.html', logged="true", movie = movie)


@app.route("/login",  methods=['GET', 'POST'])
def login():
    global  email
    form = LoginForm()
    email = form.email.data
    password = form.password.data
    if form.validate_on_submit():
        global islogin
        if ifIsHasMail(email, password) == 1:
            islogin = 'true'
            return redirect(url_for('account'))

        else:
            flash('email OR password are wrong', 'danger')
    return render_template('login.html', form=form,logged='false')



@app.route("/register", methods=['GET', 'POST'])
def register():
    form=RegistrationForm()
    username = form.userName.data
    password = form.password.data
    email = form.email.data
    confirmation_password = form.confirm_password.data
    if form.validate_on_submit():
        res = insertuSER(email, password, username, confirmation_password)
        if res == 0:
            flash("Email is already used", 'danger')
            return render_template('registration.html', form=form, logged='false')
        elif res == 1:
            flash("Check your password", 'danger')
            return render_template('registration.html', form=form, logged='false')
        else:
            flash('Welcome sir', 'success')
            return render_template('login.html', logged='false' , form=form)
    return render_template('registration.html', form=form, logged='false')


@app.route("/account", methods=['GET', 'POST'])
def account():
    global email
    global islogin
    global userId
    print(userId)
    movies = jsonRequests(ML.getUserFavouritMovies(userId))
    if islogin == 'false':
       return redirect(url_for("home"))
    user = db.execute(f''' select * from [User] where email like '{email}' ''').fetchone()
    db.commit()
    if user.profilePicture == None:
        current_user_image_file= "defaultPic.png"
    else:
        current_user_image_file= user.profilePicture
    image_file = url_for('static', filename= current_user_image_file)
    return render_template('Account.html', title='Account', image_file=image_file, logged = "true", user = user, movies = movies)

def saveUserRate(imdbId = "", rate = ''):
    global userId
    imdbId = imdbId[2:len(imdbId)]
    ML.addUserRating(userId, imdbId, rate, isImdbId = True)

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html', logged='false')


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    global islogin
    islogin = 'false'
    return render_template('home.html', logged='false')

if __name__ == '__main__':
    app.run(debug=True)
