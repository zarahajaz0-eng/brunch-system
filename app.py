from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///orders.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.String(20), nullable=False)
    items = db.Column(db.Text, nullable=False)
    drinks = db.Column(db.Text)
    note = db.Column(db.Text)
    status = db.Column(db.String(50), default="Ny ordre")
    created_at = db.Column(db.DateTime, default=datetime.now)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/send-order", methods=["POST"])
def send_order():
    data = request.get_json()

    new_order = Order(
        table_number=data.get("table_number", "5"),
        items=", ".join(data.get("items", [])),
        drinks=", ".join(data.get("drinks", [])),
        note=data.get("note", ""),
        status="Ny ordre"
    )

    db.session.add(new_order)
    db.session.commit()

    return jsonify({"message": "Ordren er gemt i databasen"})

@app.route("/kitchen")
def kitchen():
    orders = Order.query.filter(Order.status != "Færdig").order_by(Order.created_at.desc()).all()
    return render_template("kitchen.html", orders=orders)

@app.route("/finish-order/<int:order_id>", methods=["POST"])
def finish_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = "Færdig"
    db.session.commit()
    return jsonify({"message": "Ordren er færdig"})

@app.route("/database")
def database():
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template("database.html", orders=orders)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)