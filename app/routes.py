import os
from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, send_from_directory
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, UploadForm
from app.models import User, Post, Track, Video


def allowed_audio_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['AUDIO_EXTENSIONS']


def allowed_video_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['VIDEO_EXTENSIONS']


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Post Successful")
        return redirect(url_for('index'))

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for("index", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("index", page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title='Home Chamber', form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/popular')
def popular():
    return "In dev"


@app.route('/new_music')
@login_required
def new_music():
    page = request.args.get('page', 1, type=int)
    tracks = current_user.followed_tracks().paginate(
        page, app.config['TRACKS_PER_PAGE'], False)

    next_url = url_for('new_music', page=tracks.next_num) if tracks.has_next else None
    prev_url = url_for('new_music', page=tracks.prev_num) if tracks.has_prev else None

    return render_template('explore_music.html', title='New Music', tracks=tracks.items, next_url=next_url, prev_url=prev_url)



@app.route('/new_videos')
@login_required
def new_videos():
    page = request.args.get('page', 1, type=int)
    videos = current_user.followed_videos().paginate(
        page, app.config['TRACKS_PER_PAGE'], False)

    next_url = url_for("new_videos", page=videos.next_num) if videos.has_next else None
    prev_url = url_for('new_videos', page=videos.prev_num) if videos.has_prev else None

    return render_template('explore_videos.html', title="New Videos", videos=videos.items, next_url=next_url, prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("Already logged in.")
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)

    return render_template('login.html', title="Sign In", form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You are now no longer logged in.")
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("Already logged in.")
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash("Success. You may now log in.")
        return redirect(url_for('login'))

    return render_template('register.html', title="Register", form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None

    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/music/<username>')
def music(username):
    user = User.query.filter_by(username=username).first_or_404()

    page = request.args.get('page', 1, type=int)
    tracks = user.tracks.order_by(Track.timestamp.desc()).paginate(page, app.config['TRACKS_PER_PAGE'], False)

    next_url = url_for('music', username=user.username, page=tracks.next_num) if tracks.has_next else None
    prev_url = url_for('music', username=user.username, page=tracks.prev_num) if tracks.has_prev else None

    return render_template('music.html', user=user, tracks=tracks.items, next_url=next_url, prev_url=prev_url)


@app.route('/videos/<username>')
def videos(username):
    user = User.query.filter_by(username=username).first_or_404()

    page = request.args.get('page', 1, type=int)
    videos = user.videos.order_by(Video.timestamp.desc()).paginate(page, app.config['TRACKS_PER_PAGE'], False)

    next_url = url_for('videos', username=user.username, page=videos.next_num) if videos.has_next else None
    prev_url = url_for('videos', username=user.username, page=videos.prev_num) if videos.has_prev else None

    return render_template('videos.html', user=user, videos=videos.items, next_url=next_url, prev_url=prev_url)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data

        db.session.commit()

        flash("Your changes have been saved.")
        return redirect(url_for('edit_profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me


    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash("User '{}' not found.".format(username))
        return redirect(url_for('index'))

    if user == current_user:
        flash("You cannot follow yourself.")
        return redirect(url_for('user', username=current_user.username))

    current_user.follow(user)
    db.session.commit()
    flash("You are now following '{}'".format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash("User '{}' not found.".format(username))
        return redirect(url_for('index'))

    if user == current_user:
        flash("You cannot unfollow yourself.")
        return redirect(url_for('user', username=username))

    current_user.unfollow(user)
    db.session.commit()

    flash("You are no longer following '{}'".format(username))
    return redirect(url_for('user', username=username))


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()

    if form.validate_on_submit():

        f = form.upload.data
        if not allowed_audio_file(f.filename):
            flash("Invalid file type.")
            return redirect(url_for('upload'))

        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], 'audio', filename))
        track = Track(title=form.title.data, description=form.description.data, filename=filename, artist=current_user)
        db.session.add(track)
        db.session.commit()
        flash("Upload Successful.")
        return redirect(url_for('music', username=current_user.username))
    return render_template('upload.html', title='Upload Music', form=form)


@app.route('/upload_video', methods=['GET', 'POST'])
@login_required
def upload_video():
    form = UploadForm()

    if form.validate_on_submit():

        f = form.upload.data
        if not allowed_video_file(f.filename):
            flash("Invalid file type.")
            return redirect(url_for('upload_video'))

        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], 'videos', filename))
        video = Video(title=form.title.data, description=form.description.data, filename=filename, artist=current_user)
        db.session.add(video)
        db.session.commit()
        flash("Upload Successful")
        return redirect(url_for('upload_video'))
    return render_template('upload.html', title='Upload Video', form=form)


@app.route('/listen/<tracktitle>')
def listen(tracktitle):
    track = Track.query.filter_by(title=tracktitle).first_or_404()
    if current_user != track.artist:
        track.listens += 1
        db.session.commit()

    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'audio'), track.filename)


@app.route('/watch/<videotitle>')
def watch(videotitle):
    video = Video.query.filter_by(title=videotitle).first_or_404()
    if current_user != video.artist:
        video.views += 1
        db.session.commit()

    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), video.filename)



@app.route('/delete_video/<videotitle>')
@login_required
def delete_video(videotitle):
    video = Video.query.filter_by(title=videotitle).first()
    if video is None:
        flash("Video '{}' does not exist.".format(videotitle))
        return redirect(url_for('index'))

    if current_user.username != video.artist.username:
        flash("You cannot delete another user's video.")
        return redirect(url_for('index'))

    db.session.delete(video)
    db.session.commit()
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], 'videos', video.filename))
    flash("Video Successfully Deleted.")
    return redirect(url_for('videos', username=current_user.username))


@app.route('/delete/<tracktitle>')
@login_required
def delete(tracktitle):
    track = Track.query.filter_by(title=tracktitle).first()
    if track is None:
        flash("Track '{}' does not exist.".format(tracktitle))
        return redirect(url_for('index'))

    if current_user.username != track.artist.username:
        flash("You cannot delete another user's track.")
        return redirect(url_for('index'))

    db.session.delete(track)
    db.session.commit()
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], 'audio', track.filename))
    flash("Track successfully Deleted.")
    return redirect(url_for('music', username=current_user.username))
