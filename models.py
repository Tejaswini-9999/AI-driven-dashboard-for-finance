from datetime import datetime
from app import db

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.String(200))
    transaction_type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'

    def __repr__(self):
        return f'<Transaction {self.id}: {self.amount} - {self.category}>'