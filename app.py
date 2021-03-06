from flask import (Flask, render_template, request, url_for, make_response)
from fastco import (query_articles, search_articles, insert_article,
                    validate_submission, InvalidSubmission)
from settings import (STATIC, MIN)
import json

app = Flask(__name__)

opts = {"STATIC": STATIC, "MIN": MIN}

@app.route('/')
def index():
    articles = query_articles()
    return render_template('list.jinja2.html', 
                           page_type="listing",
                           articles=articles,
                           list_active="active",
                           **opts)

@app.route('/search/')
def search():
    query = request.args["query"]
    articles = search_articles(query)
    return render_template('list.jinja2.html', 
                           page_type="search",
                           query=query, 
                           articles=articles,
                           list_active="active",
                           **opts)

@app.route('/since/<int:days_ago>/')
def since(days_ago):
    articles = query_articles(days_ago=days_ago)
    return render_template('list.jinja2.html',
                           page_type="since",
                           days_ago=days_ago,
                           articles=articles,
                           list_active="active",
                           **opts)

@app.route('/submit/', methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        return do_submit()
    else:
        return render_template('submit.jinja2.html', 
                               submit_active="active",
                               **opts)

def do_submit():
    def error_page(errors):
        return render_template('submit.jinja2.html',
                               submit_active="active",
                               errors=errors,
                               **opts)
    def success_page():
        return render_template("list.jinja2.html", 
                            articles=[article],
                            page_type="success",
                            **opts)

    # fetch parameters from form
    form = request.form
    submission = dict(
        title=form["title"],
        link=form["link"],
        pub_date=form["pub_date"]
    )

    # validate form submission
    try:
        article = validate_submission(submission)
    except InvalidSubmission as ex:
        return error_page(ex.errors)

    insert_article(article)

    # all went well, render success page
    return success_page()

@app.route('/articles.json')
def articles_json():
    # fetch articles
    articles = query_articles()
    # convert into dictionaries
    records = [vars(article) for article in articles]
    # dump list of dictionaries as JSON
    resp = json.dumps(records)
    # make a JSON HTTP response
    resp = make_response(resp)
    resp.headers["Content-Type"] = "application/json"
    return resp

def run_devserver():
    app.run(debug=True)

if __name__ == "__main__":
    run_devserver()
