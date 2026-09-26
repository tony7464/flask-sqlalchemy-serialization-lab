from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from marshmallow import Schema, fields


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # A customer has many reviews; Review.customer is the other side.
    reviews = db.relationship('Review', back_populates='customer')

    # Reach purchased items through reviews without querying Review directly.
    items = association_proxy(
        'reviews', 'item', creator=lambda item: Review(item=item)
    )

    def __repr__(self):
        return f'<Customer {self.id}, {self.name}>'


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)

    # An item has many reviews; Review.item is the other side.
    reviews = db.relationship('Review', back_populates='item')

    # Reach the customers who reviewed this item through reviews.
    customers = association_proxy(
        'reviews', 'customer', creator=lambda customer: Review(customer=customer)
    )

    def __repr__(self):
        return f'<Item {self.id}, {self.name}, {self.price}>'


class Review(db.Model):
    """Join model connecting a customer to an item they reviewed."""

    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))

    customer = db.relationship('Customer', back_populates='reviews')
    item = db.relationship('Item', back_populates='reviews')

    def __repr__(self):
        return f'<Review {self.id}, {self.comment}>'


class CustomerSchema(Schema):
    """Serialize a customer and the reviews/items reached through that customer.

    Nested copies of this schema drop `items` and `reviews` so a review's
    customer does not loop back into the same graph.
    """

    id = fields.Int()
    name = fields.Str()
    reviews = fields.List(
        fields.Nested(lambda: ReviewSchema(exclude=('item', 'customer')))
    )
    items = fields.List(
        fields.Nested(lambda: ItemSchema(exclude=('reviews', 'customers')))
    )


class ItemSchema(Schema):
    """Serialize an item and the reviews/customers reached through that item.

    Nested copies drop `reviews` and `customers` to break the cycle between
    an item and the people who reviewed it.
    """

    id = fields.Int()
    name = fields.Str()
    price = fields.Float()
    reviews = fields.List(
        fields.Nested(lambda: ReviewSchema(exclude=('item', 'customer')))
    )
    customers = fields.List(
        fields.Nested(lambda: CustomerSchema(exclude=('items', 'reviews')))
    )


class ReviewSchema(Schema):
    """Serialize a review plus its customer and item, without foreign keys.

    Nested copies drop `item` and `customer` so a parent record does not
    serialize the same review relationship again.
    """

    id = fields.Int()
    comment = fields.Str()
    customer = fields.Nested(
        lambda: CustomerSchema(exclude=('items', 'reviews'))
    )
    item = fields.Nested(
        lambda: ItemSchema(exclude=('reviews', 'customers'))
    )
