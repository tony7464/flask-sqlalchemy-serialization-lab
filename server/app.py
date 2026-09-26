from flask import Flask, jsonify, render_template_string
from flask_migrate import Migrate

from models import Customer, CustomerSchema, Item, ItemSchema, Review, ReviewSchema, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)


INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Shop Reviews</title>
  <style>
    body { font-family: Georgia, serif; margin: 2rem auto; max-width: 960px; color: #1c1917; background: #faf7f2; }
    h1 { margin-bottom: 0.2rem; }
    p.lead { color: #57534e; }
    section { margin-top: 2rem; }
    article { background: white; border: 1px solid #e7e5e4; border-radius: 8px; padding: 1rem 1.2rem; margin: 0.8rem 0; }
    h2 { font-size: 1.3rem; }
    h3 { margin: 0 0 0.4rem; }
    ul { margin: 0.3rem 0 0; padding-left: 1.2rem; }
    .meta { color: #78716c; font-size: 0.95rem; }
    a { color: #9a3412; }
  </style>
</head>
<body>
  <h1>Shop Reviews</h1>
  <p class="lead">Customers, the items they reviewed, and the comments they left.</p>
  <p class="meta">JSON: <a href="/customers">/customers</a> · <a href="/items">/items</a> · <a href="/reviews">/reviews</a></p>

  <section>
    <h2>Customers</h2>
    {% for customer in customers %}
      <article>
        <h3>{{ customer.name }}</h3>
        <p class="meta">Reviewed items:
          {% if customer['items'] %}
            {{ customer['items'] | map(attribute='name') | join(', ') }}
          {% else %}
            none yet
          {% endif %}
        </p>
        <ul>
          {% for review in customer.reviews %}
            <li>{{ review.comment }}</li>
          {% else %}
            <li>No reviews</li>
          {% endfor %}
        </ul>
      </article>
    {% else %}
      <p>No customers yet. Run <code>python seed.py</code> from the server directory.</p>
    {% endfor %}
  </section>

  <section>
    <h2>Items</h2>
    {% for item in items %}
      <article>
        <h3>{{ item.name }}</h3>
        <p class="meta">${{ '%.2f'|format(item.price) }} · {{ item.reviews|length }} review{{ '' if item.reviews|length == 1 else 's' }}</p>
        <ul>
          {% for review in item.reviews %}
            <li>{{ review.comment }}</li>
          {% endfor %}
        </ul>
      </article>
    {% else %}
      <p>No items yet.</p>
    {% endfor %}
  </section>
</body>
</html>
"""


@app.route('/')
def index():
    customers = CustomerSchema(many=True).dump(Customer.query.all())
    items = ItemSchema(many=True).dump(Item.query.all())
    return render_template_string(INDEX_HTML, customers=customers, items=items)


@app.route('/customers')
def customers():
    return jsonify(CustomerSchema(many=True).dump(Customer.query.all()))


@app.route('/items')
def items():
    return jsonify(ItemSchema(many=True).dump(Item.query.all()))


@app.route('/reviews')
def reviews():
    return jsonify(ReviewSchema(many=True).dump(Review.query.all()))


if __name__ == '__main__':
    app.run(port=5555, debug=True)
