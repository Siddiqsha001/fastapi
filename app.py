from flask import Flask,request,jsonify

app=Flask(__name__)

@app.route("/")
def home():
    return "Home page"

# GET->request data from a specified resorce,POST->create a resource,PUT->update a resource,DELETE




if __name__ == "__main__":
    app.run(debug=True)