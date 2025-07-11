from flask import Flask, redirect, url_for, jsonify
app = Flask(__name__)

#static routing
@app.route("/hello")
def hello_word():
    return "Hello world!"

@app.route("/")
def home():
    return "Welcome to the home page!!"

@app.route("/about")
def about():
    return "This is about page"

# dynamic routing
@app.route("/user/<username>")
def user(username):
    return f"Welcome user {username}!!"

@app.route("/post/<int:post_id>")
def post_number(post_id):
    return f"This is a post number: {post_id}"

# url rule handler
def contact():
    return f"This is a contact page"

app.add_url_rule('/contact', view_func=contact)

@app.route("/new-home")
def new_home():
    return redirect(url_for('home'))

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "404 Not Found",
        "message": "The requested URL was not found on the server."
    }), 404

@app.errorhandler(500)
def internal_server_error(e):
    return f"An internal server error occurred. Please try again later", 500

if __name__ == "__main__":
    app.run(debug=True)