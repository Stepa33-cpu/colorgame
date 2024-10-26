from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserData(db.Model):
    __tablename__ = 'user_data'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    level = db.Column(db.Integer)
    time_spent = db.Column(db.Float)
    answer = db.Column(db.Text)
    color_matrix = db.Column(db.Text)

    def __repr__(self):
        return f'<UserData {self.name} {self.surname}>'
