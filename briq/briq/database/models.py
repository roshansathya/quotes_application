import mongoengine
import uuid
from datetime import datetime
from briq.utils import process_quote

class User(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    created_at = mongoengine.DateTimeField(default=datetime.utcnow)

    meta = {
        'db_alias': 'core'
    }


class QuotesRatedByUser(mongoengine.Document):
    user_id = mongoengine.ObjectIdField(primary_key=True)
    quotes = mongoengine.ListField()

    meta = {
        'db_alias': 'core'
    }
    

class QuoteRating(mongoengine.EmbeddedDocument):
    user_id = mongoengine.ObjectIdField(required=True)
    rating = mongoengine.IntField(required=True)
    created_at = mongoengine.DateTimeField(default=datetime.utcnow)

class Quote(mongoengine.Document):
    quote = mongoengine.StringField(required=True)
    author = mongoengine.StringField(required=True)
    source = mongoengine.StringField()
    ratings = mongoengine.EmbeddedDocumentListField(QuoteRating)
    ratings_avg = mongoengine.FloatField(default=0.0)
    added_by = mongoengine.ObjectIdField(required=True)
    created_at = mongoengine.DateTimeField(default=datetime.utcnow)
    processed_quote = mongoengine.StringField()
    last_updated_at = mongoengine.DateTimeField(default=datetime.utcnow)
    is_recommended = mongoengine.BooleanField()
    
    meta = {
        'db_alias': 'core'
    }

    def save(self, *args, **kwargs):
        processed_quote = process_quote(self.quote)
        self.processed_quote = processed_quote
        self.ratings_avg = self.ratings_avg or 0
        self.is_recommended =  self.ratings_avg > 3
        super(Quote, self).save(*args, **kwargs)

    def delele(self, *args, **kwargs):
        quotes_rated = QuotesRatedByUser.objects().filter(user_id=self.added_by).first()
        if quotes_rated:
            quotes_rated.quotes = [quote for quote in quotes_rated.quotes if str(quote.id) != str(self.id)]
            quotes_rated.save()
        super(Quote, self).delete(*args, **kwargs)

