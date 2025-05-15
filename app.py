from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///computers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup static folder for Netflix-style theme
app.static_folder = 'static'
app.template_folder = 'templates'

db = SQLAlchemy(app)

# Models
class Computer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specs = db.Column(db.Text, nullable=False)
    software = db.Column(db.Text, nullable=True)
    repairs = db.relationship('Repair', backref='computer', lazy=True)

class Repair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    detail = db.Column(db.Text, nullable=False)
    computer_id = db.Column(db.Integer, db.ForeignKey('computer.id'), nullable=False)

# Routes
@app.route('/')
def index():
    query = request.args.get('q')
    if query:
        computers = Computer.query.filter(Computer.name.contains(query)).all()
    else:
        computers = Computer.query.all()
    return render_template('index.html', computers=computers, query=query)

@app.route('/add', methods=['GET', 'POST'])
def add_computer():
    if request.method == 'POST':
        name = request.form['name']
        specs = request.form['specs']
        software = request.form['software']
        new_computer = Computer(name=name, specs=specs, software=software)
        db.session.add(new_computer)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_computer.html')

@app.route('/computer/<int:computer_id>')
def view_computer(computer_id):
    computer = Computer.query.get_or_404(computer_id)
    return render_template('view_computer.html', computer=computer)

@app.route('/computer/<int:computer_id>/add_repair', methods=['POST'])
def add_repair(computer_id):
    detail = request.form['detail']
    new_repair = Repair(detail=detail, computer_id=computer_id)
    db.session.add(new_repair)
    db.session.commit()
    return redirect(url_for('view_computer', computer_id=computer_id))

# Start app
if __name__ == '__main__':
    if not os.path.exists('computers.db'):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
