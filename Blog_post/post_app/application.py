from flask import abort, request, jsonify, url_for
from flask_httpauth import HTTPTokenAuth
from post_app.models import User, Post
from post_app import app, db

token_auth = HTTPTokenAuth()


@app.route('/api/user/register', methods=['POST'])
def register_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)
    if User.query.filter_by(username=username).first() is not None:
        abort(400)
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201, {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/user/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/api/token', methods=['POST'])
def get_auth_token():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if user and user.verify_password(password):
        token = user.get_token()
    else:
        abort(400)
    db.session.commit()
    return jsonify({'token': token})


@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None


@app.route('/api/posts', methods=['GET'])
@token_auth.login_required
def get_posts():

    posts = Post.query.all()

    if not posts:
        abort(400)

    return jsonify({'posts': [post.to_dict() for post in posts]})


@app.route('/api/post', methods=['POST'])
@token_auth.login_required
def add_post():
    if not request.json or not 'title' in request.json:
        abort(400)
    title = request.json.get('title')
    content = request.json.get('content')
    category = request.json.get('category')
    post = Post(title=title, content=content, category=category, user_id=token_auth.current_user().id)
    db.session.add(post)
    db.session.commit()
    return jsonify({'post': {'title': post.title}}), 201


@app.route('/api/post/<int:post_id>', methods=['GET'])
@token_auth.login_required
def get_post(post_id):
    post = Post.query.filter_by(
        id=post_id).filter_by(user_id=token_auth.current_user().id).first()
    if not post:
        abort(403)

    return jsonify({'posts': post.to_dict()})


@app.route('/api/post/<int:post_id>', methods=['PUT'])
@token_auth.login_required
def update_post(post_id):
    post = Post.query.filter_by(
        id=post_id).filter_by(user_id=token_auth.current_user().id).first()
    if not post:
        abort(403)

    post.title = request.json.get('title')
    post.content = request.json.get('content')
    post.category = request.json.get('category')

    db.session.commit()

    return jsonify({'post': post.to_dict()})


@app.route('/api/post/<int:post_id>', methods=['DELETE'])
@token_auth.login_required
def delete_posts(post_id):
    post = Post.query.filter_by(
        id=post_id).filter_by(user_id=token_auth.current_user().id).first()
    if not post:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    return jsonify({'result': 'Post Deleted'})


