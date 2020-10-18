from briq import app
from flask import request, Response, json, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from briq.database.models import User, Quote, QuotesRatedByUser, QuoteRating
from briq.utils import process_quote
vectorizer = TfidfVectorizer()

#CREATE AN ACCOUNT
@app.route("/create_account", methods=['POST'])
def create_account():  
    name = request.args.get('name')
    if not name:
        return Response(
            response=json.dumps({"message": "[core-view - create_account] Name not found"}),
            status=500
        )

    user = User.objects().filter(name=name).first()
    if not user:
        user = User(name=name)
    user.save()

    return Response(
        response=json.dumps({"message": "[core-view - create_account] Success", "id": str(user.id)}),
        status=200
    )

#ADD A USER TO QUOTES FROM CSV
@app.route("/process_quotes", methods=['POST'])
def initial_quote_processing():
    user_id = request.args.get('user_id')

    quotes = Quote.objects()
    for quote in quotes:
        quote.added_by = user_id
        quote.save()

    return Response(
        response=json.dumps({"message": "[core-view - process_quotes] Success"}),
        status=200
    )

#GET ALL QUOTES
@app.route("/quotes", methods=['GET'])
def quotes():
    quotes = Quote.objects()
    all_quotes = []
    for quote in quotes:
        quote = quote._data
        quote['id'] = str(quote['id'])
        quote['added_by'] = str(quote['added_by'])
        all_quotes.append(quote)

    return Response(
        response=json.dumps({"message": "[core-view - quotes] Success", "quotes": all_quotes}),
        status=200
    )

#GET AND POST A QUOTE
@app.route("/quote", methods=['GET','POST'])
def quote():
    if request.method == 'POST':
        quote = request.args.get('quote')
        author = request.args.get('author')
        user_id = request.args.get('user_id')

        if not quote or not author or not user_id:
            return Response(
                response=json.dumps({"message": "[core-view - quote - GET] Insufficient information"}),
                status=500
            )

        quote_obj = Quote(quote=quote, author=author, added_by=user_id)
        quote_obj.save()
        
        return Response(
            response=json.dumps({"message": "[core-view - quote]", "quote_id":str(quote_obj.id)}),
            status= 200
        )

    if request.method == "GET":
        user_id = request.args.get('user_id')
        if not user_id:
            return Response(
                response=json.dumps({"message": "[core-view-quote-POST] Insufficient information"}),
                status=500
            )
        
        quotes = Quote.objects().filter(added_by=user_id)
        all_quotes = [quote._data() for quote in quotes]
        return Response(
            response=json.dumps({"message": "[core-view-quote-GET] Success", "quote": all_quotes}),
            status=200
        )

#GET RELATED_QUOTES
@app.route("/get_related_quotes", methods=['GET'])
def get_related_quotes():
    quote_id = request.args.get('quote_id')
    quote = request.args.get('quote')
    
    if not quote_id and not quote:
        return Response(
            response=json.dumps({"message": "[core-view-get_related_quotes-GET] Insufficient information"}),
            status=500
        )

    if not quote:
        quote_obj = Quote.objects().filter(id=quote_id).first()
        if not quote:
            return Response(
                response=json.dumps({"message": "[core-view-get_related_quotes-GET] Insufficient information"}),
                status=500
            )
        quote = quote_obj.processed_quote
    else:
        quote = process_quote(quote)
    
    related_quotes = []
    quotes_objs = Quote.objects()

    for current_quote in quotes_objs:    
        tfidf = vectorizer.fit_transform([quote, current_quote.processed_quote])
        output = ((tfidf * tfidf.T).A)[0,1]
        if output >= 0.3:
            related_quotes.append(current_quote.quote)

    return Response(
        response=json.dumps({"message": "[core-view-get_related_quotes-GET] Success", "quotes": related_quotes}),
        status=200
    )

#GET AND POST A RATING FROM A USER
@app.route("/rate_by_user", methods=['GET', 'POST'])
def get_quotes_rated_by_user():
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if not user_id:
            return Response(
                response=json.dumps({"message": "[core-view-rate_by_user-GET] Insufficient information"}),
                status=500
            )
        
        quotes_by_user = QuotesRatedByUser.objects().filter(user_id=user_id).first()
        formatted_quotes = []
        for quote in quotes_by_user.quotes:
            current_quote = quote
            del current_quote['ratings']
            formatted_quotes.append(current_quote)

        return Response(
            response=json.dumps({"message": "[core-view-rate_by_user-GET] Success", "quotes": current_quote}),
            status=200
        )

    if request.method == 'POST':
        quote_id = request.args.get('quote_id')
        rating = request.args.get('rating')
        user_id = request.args.get('user_id')
        
        quote = Quote.objects().filter(id=quote_id).first()
        if not quote_id:
            return Response(
                response=json.dumps({"message": "[core-view-rate_by_user-POST] Insufficient information"}),
                status=500
            )
        
        quote_rating_obj = QuoteRating(user_id=user_id, rating=float(rating))
        quote.ratings = quote.ratings + [quote_rating_obj]

        total_ratings = len(quote.ratings) 
        ratings_avg = (total_ratings * quote.ratings_avg) + float(rating)
        quote.ratings_avg = ratings_avg / (total_ratings+1)
        quote.is_recommended = quote.ratings_avg > 3
        quote.save()

        quotes_rated_by_user = QuotesRatedByUser.objects().filter(user_id=user_id).first()
        current_quotes = quotes_rated_by_user.quotes if quotes_rated_by_user else []
        if not quotes_rated_by_user:
            quotes_rated_by_user = QuotesRatedByUser(user_id=user_id)
            
        quote_dict = quote._data
        quote_dict['id'] = str(quote_dict['id'])
        quote_dict['added_by'] = str(quote_dict['added_by'])
        current_quotes.append(quote_dict)

        quotes_rated_by_user.quotes = current_quotes
        quotes_rated_by_user.save()

        return Response(
            response=json.dumps({"message": "[core-view-rate_by_user-POST] Success"}),
            status=200
        )

@app.route("/delete_quote", methods=['POST'])
def delete_quote():
    quote_id = request.args.get('quote_id')
    quote_obj = Quote.objects().filter(id=quote_id).first()
    if not quote_obj:
        return Response(
            response=json.dumps({"message": "[core-view-delete_quote-POST] Insufficient information"}),
            status=500
        )
    quote_obj.delete()

    return Response(
        response=json.dumps({"message": "[core-view-delete_quote-POST] Success"}),
        status=200
    )