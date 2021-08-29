from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os

API_KEY = os.environ['MOVIE_DATABASE']
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top-10-moviess.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class UpdateForm(FlaskForm):
    new_rating = StringField("Your rating out of 10 (e.g 7.5)")
    new_review = StringField("Your review")
    submit = SubmitField("Done")


class AddForm(FlaskForm):
    movie_title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add movie")


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


class AddInfo(FlaskForm):
    new_rating = StringField("Your rating out of 10 (e.g 7.5)")
    new_review = StringField("Your review")
    submit = SubmitField("Done")


# db.create_all()
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()
# all_movies = Movie.query.all()
@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = UpdateForm()
    movie_id = request.args.get("id")
    if form.validate_on_submit():
        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = float(form.new_rating.data)
        movie_to_update.review = form.new_review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def add():
    add_form = AddForm()
    if add_form.validate_on_submit():
        params = {
            "api_key": API_KEY,
            "query": add_form.movie_title.data
        }
        data = requests.get("https://api.themoviedb.org/3/search/movie", params=params).json()
        return render_template("select.html", data=data["results"])
    return render_template("add.html", add_form=add_form)


@app.route("/added")
def added():
    form=AddForm()
    path = request.args.get("path")
    title = request.args.get("title")
    date = request.args.get("date")
    year = date.split("-")[0]
    overview = request.args.get("overview")
    # key = {
    #     "api_key": API_KEY,
    # }
    # response = requests.get(f"https://api.themoviedb.org/3/movie/{id}/images", params=key).json()
    # print(response)
    # url = response['posters'][0]['file_path']
    image = f"https://image.tmdb.org/t/p/w500/{path}"
    new_movie = Movie(title=title, year=year, description=overview, rating=0, review="none", img_url=image)
    db.session.add(new_movie)
    db.session.commit()
    movie = Movie.query.filter_by(title=title).first()
    return redirect(url_for('edit', id=movie.id))


if __name__ == '__main__':
    app.run(debug=True)
