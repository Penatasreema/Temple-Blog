from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
import os

app = Flask(__name__)

# Upload folder config
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure folder exists
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['aptitude_db']
blogs_collection = db['blogs']

# Home page with search
@app.route('/', methods=['GET', 'POST'])
def index():
    query = request.form.get('search')
    if query:
        blogs = list(blogs_collection.find({"title": {"$regex": query, "$options": "i"}}))
    else:
        blogs = list(blogs_collection.find())

    # Convert ObjectId to str for URL generation
    for blog in blogs:
        blog['_id'] = str(blog['_id'])

    return render_template('index.html', blogs=blogs, query=query)

# Blog detail page
@app.route('/blog/<blog_id>')
def blog(blog_id):
    blog = blogs_collection.find_one({"_id": ObjectId(blog_id)})
    if blog:
        return render_template('blog.html', blog=blog)
    return "Blog not found", 404

# Add blog page
@app.route('/add', methods=['GET', 'POST'])
def add_blog():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        image = request.files.get('image')
        image_filename = None

        # Save image if uploaded
        if image and image.filename != '':
            image_filename = image.filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image.save(image_path)

        # Insert blog into MongoDB
        blogs_collection.insert_one({
            "title": title,
            "description": description,
            "image": image_filename
        })
        return redirect(url_for('index'))

    return render_template('add_blog.html')

if __name__ == '__main__':
    app.run(debug=True)
