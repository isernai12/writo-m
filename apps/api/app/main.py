import datetime as dt
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from . import auth, models, schemas
from .config import settings
from .db import get_db

app = FastAPI(title="Writo API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> models.User:
    try:
        user_id = int(auth.decode_token(token, settings.jwt_secret))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from exc
    user = db.get(models.User, user_id)
    if not user or user.is_banned:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/settings/public", response_model=schemas.SiteSettingsOut)
def public_settings(db: Session = Depends(get_db)):
    settings_row = db.scalar(select(models.SiteSettings))
    if not settings_row:
        return schemas.SiteSettingsOut(maintenance_mode=False)
    return schemas.SiteSettingsOut(maintenance_mode=settings_row.maintenance_mode)


@app.get("/api/v1/home")
def home(db: Session = Depends(get_db)):
    posts = db.scalars(select(models.Post).limit(6)).all()
    latest = db.scalars(select(models.Post).order_by(models.Post.created_at.desc()).limit(5)).all()
    writers = db.scalars(select(models.User).limit(5)).all()
    categories = db.scalars(select(models.Category).limit(2)).all()
    return {
        "trending": [serialize_post(post) for post in posts],
        "latest": [serialize_post(post) for post in latest],
        "top_writers": [serialize_user(writer) for writer in writers],
        "featured_categories": [serialize_category(category) for category in categories],
    }


@app.get("/api/v1/posts", response_model=schemas.PostList)
def list_posts(db: Session = Depends(get_db), page: int = 1):
    page_size = 20
    offset = (page - 1) * page_size
    posts = db.scalars(select(models.Post).offset(offset).limit(page_size)).all()
    total = db.scalar(select(func.count()).select_from(models.Post))
    return {"items": [serialize_post(post) for post in posts], "total": total or 0}


@app.get("/api/v1/posts/trending", response_model=schemas.PostList)
def trending_posts(db: Session = Depends(get_db)):
    posts = db.scalars(select(models.Post).order_by(models.Post.love_count.desc()).limit(6)).all()
    return {"items": [serialize_post(post) for post in posts], "total": len(posts)}


@app.get("/api/v1/posts/latest", response_model=schemas.PostList)
def latest_posts(db: Session = Depends(get_db)):
    posts = db.scalars(select(models.Post).order_by(models.Post.created_at.desc()).limit(5)).all()
    return {"items": [serialize_post(post) for post in posts], "total": len(posts)}


@app.get("/api/v1/posts/{slug}", response_model=schemas.PostOut)
def post_detail(slug: str, db: Session = Depends(get_db)):
    post = db.scalar(select(models.Post).where(models.Post.slug == slug))
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return serialize_post(post)


@app.get("/api/v1/categories", response_model=list[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    categories = db.scalars(select(models.Category)).all()
    return [serialize_category(category) for category in categories]


@app.get("/api/v1/categories/{slug}/posts", response_model=schemas.PostList)
def category_posts(slug: str, db: Session = Depends(get_db)):
    category = db.scalar(select(models.Category).where(models.Category.slug == slug))
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    posts = db.scalars(select(models.Post).where(models.Post.category_id == category.id)).all()
    return {"items": [serialize_post(post) for post in posts], "total": len(posts)}


@app.get("/api/v1/writers/top")
def top_writers(db: Session = Depends(get_db)):
    writers = db.scalars(select(models.User).limit(5)).all()
    return [serialize_user(writer) for writer in writers]


@app.get("/api/v1/writers/{user_id}")
def writer_detail(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Writer not found")
    return serialize_user(user, include_bio=True)


@app.get("/api/v1/writers/{user_id}/posts", response_model=schemas.PostList)
def writer_posts(user_id: int, db: Session = Depends(get_db)):
    posts = db.scalars(select(models.Post).where(models.Post.author_id == user_id)).all()
    return {"items": [serialize_post(post) for post in posts], "total": len(posts)}


@app.get("/api/v1/search")
def search(q: str, db: Session = Depends(get_db)):
    if not q:
        return {"items": []}
    term = f"%{q.lower()}%"
    posts = db.scalars(
        select(models.Post).where(
            or_(
                func.lower(models.Post.title).like(term),
                func.lower(models.Post.excerpt).like(term),
            )
        )
    ).all()
    return {"items": [serialize_post(post) for post in posts]}


@app.post("/api/v1/auth/signup", response_model=schemas.TokenOut)
def signup(payload: schemas.SignupIn, db: Session = Depends(get_db)):
    if db.scalar(select(models.User).where(models.User.email == payload.email)):
        raise HTTPException(status_code=400, detail="Email already used")
    user = models.User(
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=auth.hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return schemas.TokenOut(
        access_token=auth.create_access_token(user.id),
        refresh_token=auth.create_refresh_token(user.id),
    )


@app.post("/api/v1/auth/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.email == payload.email))
    if not user or not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return schemas.TokenOut(
        access_token=auth.create_access_token(user.id),
        refresh_token=auth.create_refresh_token(user.id),
    )


@app.post("/api/v1/auth/refresh", response_model=schemas.TokenOut)
def refresh(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    try:
        user_id = int(auth.decode_token(token, settings.refresh_secret))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return schemas.TokenOut(
        access_token=auth.create_access_token(user.id),
        refresh_token=auth.create_refresh_token(user.id),
    )


@app.post("/api/v1/auth/logout")
def logout():
    return {"status": "ok"}


@app.get("/api/v1/me")
def me(user: models.User = Depends(get_current_user)):
    return serialize_user(user, include_bio=True)


@app.patch("/api/v1/me/profile")
def update_profile(
    payload: dict,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user.full_name = payload.get("full_name", user.full_name)
    user.bio = payload.get("bio", user.bio)
    user.avatar_url = payload.get("avatar_url", user.avatar_url)
    db.commit()
    return serialize_user(user, include_bio=True)


@app.get("/api/v1/me/bookmarks")
def my_bookmarks(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookmarks = db.scalars(select(models.Bookmark).where(models.Bookmark.user_id == user.id)).all()
    posts = [db.get(models.Post, bookmark.post_id) for bookmark in bookmarks]
    return [serialize_post(post) for post in posts if post]


@app.post("/api/v1/posts/{post_id}/bookmark")
def bookmark_post(
    post_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if db.scalar(
        select(models.Bookmark).where(
            models.Bookmark.user_id == user.id,
            models.Bookmark.post_id == post_id,
        )
    ):
        return {"status": "exists"}
    db.add(models.Bookmark(user_id=user.id, post_id=post_id))
    db.commit()
    return {"status": "ok"}


@app.delete("/api/v1/posts/{post_id}/bookmark")
def unbookmark_post(
    post_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmark = db.scalar(
        select(models.Bookmark).where(
            models.Bookmark.user_id == user.id,
            models.Bookmark.post_id == post_id,
        )
    )
    if bookmark:
        db.delete(bookmark)
        db.commit()
    return {"status": "ok"}


@app.post("/api/v1/posts/{post_id}/react")
def react_post(
    post_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if db.scalar(
        select(models.Reaction).where(
            models.Reaction.user_id == user.id,
            models.Reaction.post_id == post_id,
        )
    ):
        return {"status": "exists"}
    db.add(models.Reaction(user_id=user.id, post_id=post_id))
    post = db.get(models.Post, post_id)
    if post:
        post.love_count += 1
    db.commit()
    return {"status": "ok"}


@app.delete("/api/v1/posts/{post_id}/react")
def unreact_post(
    post_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reaction = db.scalar(
        select(models.Reaction).where(
            models.Reaction.user_id == user.id,
            models.Reaction.post_id == post_id,
        )
    )
    post = db.get(models.Post, post_id)
    if reaction and post:
        post.love_count = max(0, post.love_count - 1)
        db.delete(reaction)
        db.commit()
    return {"status": "ok"}


@app.get("/api/v1/posts/{post_id}/comments")
def list_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.scalars(select(models.Comment).where(models.Comment.post_id == post_id)).all()
    return [
        {"id": comment.id, "body": comment.body, "created_at": comment.created_at}
        for comment in comments
    ]


@app.post("/api/v1/posts/{post_id}/comments")
def add_comment(
    post_id: int,
    payload: schemas.CommentIn,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = models.Comment(body=payload.body, user_id=user.id, post_id=post_id)
    db.add(comment)
    post = db.get(models.Post, post_id)
    if post:
        post.comment_count += 1
    db.commit()
    return {"status": "ok"}


@app.patch("/api/v1/comments/{comment_id}")
def update_comment(
    comment_id: int,
    payload: schemas.CommentIn,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.get(models.Comment, comment_id)
    if not comment or comment.user_id != user.id:
        raise HTTPException(status_code=404, detail="Comment not found")
    comment.body = payload.body
    db.commit()
    return {"status": "ok"}


@app.delete("/api/v1/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.get(models.Comment, comment_id)
    if not comment or comment.user_id != user.id:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.commit()
    return {"status": "ok"}


@app.post("/api/v1/reports")
def report(payload: dict, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    report_row = models.Report(
        reason=payload.get("reason", "unspecified"),
        details=payload.get("details"),
        post_id=payload.get("post_id"),
        comment_id=payload.get("comment_id"),
        reporter_id=user.id,
    )
    db.add(report_row)
    db.commit()
    return {"status": "ok"}


@app.post("/api/v1/track/page-view")
@app.post("/api/v1/track/time-spent")
@app.post("/api/v1/track/post-view")
def track():
    return {"status": "ok"}


@app.get("/api/v1/me/posts")
def my_posts(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    posts = db.scalars(select(models.Post).where(models.Post.author_id == user.id)).all()
    return [serialize_post(post) for post in posts]


@app.post("/api/v1/me/posts")
def create_post(
    payload: schemas.PostCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.is_admin:
        raise HTTPException(status_code=403, detail="Admins cannot write posts")
    slug = payload.title.lower().replace(" ", "-")
    post = models.Post(
        title=payload.title,
        slug=slug,
        excerpt=payload.excerpt,
        content=payload.content,
        category_id=payload.category_id,
        author_id=user.id,
        thumbnail_url=payload.thumbnail_url,
        trending_thumbnail_url=payload.trending_thumbnail_url,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return serialize_post(post)


@app.patch("/api/v1/me/posts/{post_id}")
def update_post(
    post_id: int,
    payload: schemas.PostUpdate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.is_admin:
        raise HTTPException(status_code=403, detail="Admins cannot edit posts")
    post = db.get(models.Post, post_id)
    if not post or post.author_id != user.id:
        raise HTTPException(status_code=404, detail="Post not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post)
    return serialize_post(post)


@app.delete("/api/v1/me/posts/{post_id}")
def delete_post(
    post_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.is_admin:
        raise HTTPException(status_code=403, detail="Admins cannot delete posts")
    post = db.get(models.Post, post_id)
    if not post or post.author_id != user.id:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"status": "ok"}


@app.post("/api/v1/me/posts/{post_id}/submit")
def submit_post(
    post_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.is_admin:
        raise HTTPException(status_code=403, detail="Admins cannot submit posts")
    post = db.get(models.Post, post_id)
    if not post or post.author_id != user.id:
        raise HTTPException(status_code=404, detail="Post not found")
    post.status = "pending"
    db.commit()
    return {"status": "ok"}


@app.get("/api/v1/admin/stats/overview")
def admin_stats(user: models.User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {
        "uptime": "24h",
        "views_24h": 1200,
        "top_pages": ["/", "/post/sample"],
        "avg_time_on_site": "3m 42s",
        "avg_post_read_time": "5m 20s",
        "top_post": "Sample Post",
    }


@app.patch("/api/v1/admin/settings")
def admin_settings(
    payload: dict,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    settings_row = db.scalar(select(models.SiteSettings))
    settings_row.maintenance_mode = payload.get(
        "maintenance_mode", settings_row.maintenance_mode
    )
    db.commit()
    return {"status": "ok"}


@app.get("/api/v1/admin/review/posts")
def review_posts(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    posts = db.scalars(select(models.Post).where(models.Post.status == "pending")).all()
    return [serialize_post(post) for post in posts]


@app.post("/api/v1/admin/review/posts/{post_id}/approve")
def approve_post(
    post_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    post = db.get(models.Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.status = "published"
    post.published_at = dt.datetime.utcnow()
    db.commit()
    return {"status": "ok"}


@app.post("/api/v1/admin/review/posts/{post_id}/reject")
def reject_post(
    post_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    post = db.get(models.Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.status = "rejected"
    db.commit()
    return {"status": "ok"}


@app.get("/api/v1/admin/reports")
def admin_reports(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    reports = db.scalars(select(models.Report)).all()
    return [
        {"id": report.id, "reason": report.reason, "details": report.details}
        for report in reports
    ]


@app.patch("/api/v1/admin/users/{user_id}/ban")
def ban_user(
    user_id: int,
    payload: dict,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    target = db.get(models.User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.is_banned = bool(payload.get("is_banned", True))
    db.commit()
    return {"status": "ok"}


@app.delete("/api/v1/admin/posts/{post_id}")
def admin_delete_post(
    post_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    post = db.get(models.Post, post_id)
    if post:
        db.delete(post)
        db.commit()
    return {"status": "ok"}


@app.delete("/api/v1/admin/comments/{comment_id}")
def admin_delete_comment(
    comment_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    comment = db.get(models.Comment, comment_id)
    if comment:
        db.delete(comment)
        db.commit()
    return {"status": "ok"}


def serialize_user(user: models.User, include_bio: bool = False) -> dict:
    data = {
        "id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "avatar_url": user.avatar_url,
    }
    if include_bio:
        data["bio"] = user.bio
    return data


def serialize_category(category: models.Category) -> dict:
    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
    }


def serialize_post(post: models.Post) -> dict:
    return {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "excerpt": post.excerpt,
        "content": post.content,
        "thumbnail_url": post.thumbnail_url,
        "trending_thumbnail_url": post.trending_thumbnail_url,
        "status": post.status,
        "read_time_minutes": post.read_time_minutes,
        "love_count": post.love_count,
        "comment_count": post.comment_count,
        "created_at": post.created_at,
        "published_at": post.published_at,
        "author": serialize_user(post.author),
        "category": serialize_category(post.category),
    }
