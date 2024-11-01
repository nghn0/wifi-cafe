from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, VARCHAR, Boolean
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, RadioField
from wtforms.validators import DataRequired, Email
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.secret_key = "any-string-you-want-just-keep-it-secret"
Bootstrap5(app)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cafes.db"

db = SQLAlchemy(model_class=Base)
db.init_app(app)


class cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(300), nullable=False)
    map_url: Mapped[str] = mapped_column(VARCHAR(300), nullable=False)
    img_url: Mapped[str] = mapped_column(VARCHAR(300), nullable=False)
    location: Mapped[str] = mapped_column(VARCHAR(300), nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    seats: Mapped[str] = mapped_column(VARCHAR(300), nullable=False)
    coffee_price: Mapped[str] = mapped_column(VARCHAR(300))


class Users(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(VARCHAR(300), nullable=False)
    password: Mapped[str] = mapped_column(VARCHAR(300), nullable=False)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user):
    return db.get_or_404(Users, user)


class Location(FlaskForm):
    loc = StringField("Enter the Location Name: ", validators=[DataRequired()])
    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    email = StringField("Enter An email: ", validators=[DataRequired(), Email()])
    password = PasswordField("Enter a password: ", validators=[DataRequired()])
    register = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Enter An email: ", validators=[DataRequired(), Email()])
    password = PasswordField("Enter a password: ", validators=[DataRequired()])
    login = SubmitField("Login")


class CafeForm(FlaskForm):
    name = StringField("Enter the name of cafe: ", validators=[DataRequired()])
    murl = StringField("Enter the map url: ", validators=[DataRequired()])
    iurl = StringField("Enter the image url: ", validators=[DataRequired()])
    location = StringField("Enter the location name: ", validators=[DataRequired()])
    has_socket = RadioField("Has Sockets: ", choices=[(1, 'Yes'), (0, 'No')], validators=[DataRequired()])
    has_toilet = RadioField("Has Toilets: ", choices=[(1, 'Yes'), (0, 'No')], validators=[DataRequired()])
    has_wifi = RadioField("Has WiFi: ", choices=[(1, 'Yes'), (0, 'No')], validators=[DataRequired()])
    take_call = RadioField("Can Take Calls: ", choices=[(1, 'Yes'), (0, 'No')], validators=[DataRequired()])
    seats = StringField("How many Seats: ", validators=[DataRequired()])
    coffee_price = StringField("Enter the coffee price: ", validators=[DataRequired()])
    add = SubmitField("Add")


class EditCafeForm(FlaskForm):
    seats = StringField("How many Seats: ", validators=[DataRequired()])
    coffee_price = StringField("Enter the coffee price: ", validators=[DataRequired()])
    has_wifi = RadioField("Has WiFi: ", choices=[(1, 'Yes'), (0, 'No')], validators=[DataRequired()])
    take_call = RadioField("Can Take Calls: ", choices=[(1, 'Yes'), (0, 'No')], validators=[DataRequired()])
    has_socket = RadioField("Has Sockets: ", choices=[(1, 'Yes'), (0, 'No')], validators=[DataRequired()])
    edit = SubmitField("Edit")


@app.route('/')
def home():
    with app.app_context():
        cafes = db.session.execute(db.select(cafe)).scalars()
        return render_template("index.html", cafes=cafes, logged_in=current_user.is_authenticated)


@app.route('/about')
def about():
    return render_template("about.html", logged_in=current_user.is_authenticated)


@app.route('/contact')
def contact():
    return render_template("contact.html", logged_in=current_user.is_authenticated)


@app.route('/cafe/<int:idc>')
def cafe_id(idc):
    with app.app_context():
        sel_cafe = db.session.execute(db.select(cafe).where(cafe.id == idc)).scalar()
        return render_template("cafe.html", cafe=sel_cafe, logged_in=current_user.is_authenticated)


@app.route('/search', methods=['POST', 'GET'])
def search():
    loc = Location()
    if loc.validate_on_submit():
        with app.app_context():
            rows = db.session.execute(db.select(cafe).where(cafe.location == loc.loc.data)).scalars()
            return render_template("search.html", loc=loc, cafes=rows, logged_in=current_user.is_authenticated)
    return render_template("search.html", loc=loc, cafes=None, logged_in=current_user.is_authenticated)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        with app.app_context():
            row = db.session.execute(db.select(Users).where(Users.email == form.email.data)).scalar()
            if row:
                flash("Email Already Exists . Login")
            else:
                row = Users(email=form.email.data,
                            password=generate_password_hash(f'{form.password.data}', method='pbkdf2:sha256',
                                                            salt_length=8))
                db.session.add(row)
                db.session.commit()
                login_user(row)
                return redirect(url_for('home'))
    return render_template('register.html', form=form, logged_in=current_user.is_authenticated)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with app.app_context():
            row = db.session.execute(db.select(Users).where(Users.email == form.email.data)).scalar()
            if row:
                if check_password_hash(row.password, form.password.data):
                    login_user(row)
                    return redirect(url_for('home'))
                else:
                    flash("Invalid Password")
            else:
                flash("No email found . Register")

    return render_template('login.html', form=form, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/add_cafe', methods=['POST', 'GET'])
@login_required
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        row = cafe(
            name=form.name.data,
            map_url=form.murl.data,
            img_url=form.iurl.data,
            location=form.location.data,
            has_sockets=int(form.has_socket.data),
            has_toilet=int(form.has_toilet.data),
            has_wifi=int(form.has_wifi.data),
            can_take_calls=int(form.take_call.data),
            seats=form.seats.data,
            coffee_price=f"£{form.coffee_price.data}"
        )
        db.session.add(row)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add_cafe.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/edit_cafe/<int:cafeid>', methods=['POST', 'GET'])
@login_required
def edit_cafe(cafeid):
    print(cafeid)
    form = EditCafeForm()
    if form.validate_on_submit():
        row = db.session.execute(db.select(cafe).where(cafe.id == int(cafeid))).scalar()
        row.seats = form.seats.data
        row.coffee_price = f"£{form.coffee_price.data}"
        row.has_wifi = int(form.has_wifi.data)
        row.can_take_calls = int(form.take_call.data)
        row.has_sockets = int(form.has_socket.data)
        db.session.commit()
        return redirect(url_for('cafe_id', idc=cafeid))
    return render_template('edit_cafe.html', form=form)



if __name__ == "__main__":
    app.run(debug=True)
