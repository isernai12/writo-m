import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import auth, models
from .config import settings


DEFAULT_CATEGORIES = [
    ("Technology", "technology"),
    ("Productivity", "productivity"),
    ("Design", "design"),
    ("Culture", "culture"),
]


def seed_defaults(db: Session) -> None:
    if not db.scalar(select(models.SiteSettings)):
        db.add(models.SiteSettings(maintenance_mode=False))

    for name, slug in DEFAULT_CATEGORIES:
        if not db.scalar(select(models.Category).where(models.Category.slug == slug)):
            db.add(models.Category(name=name, slug=slug))

    if settings.admin_seed_key:
        existing_admin = db.scalar(select(models.User).where(models.User.email == settings.admin_email))
        if not existing_admin:
            admin = models.User(
                email=settings.admin_email,
                username="admin",
                full_name=settings.admin_full_name,
                hashed_password=auth.hash_password(settings.admin_password),
                is_admin=True,
                created_at=dt.datetime.utcnow(),
            )
            db.add(admin)

    db.commit()
