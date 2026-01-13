import datetime as dt
from pydantic import BaseModel, EmailStr


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None = None


class UserPublic(BaseModel):
    id: int
    full_name: str
    username: str
    avatar_url: str | None = None


class PostOut(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: str
    content: str
    thumbnail_url: str | None = None
    trending_thumbnail_url: str | None = None
    status: str
    read_time_minutes: int
    love_count: int
    comment_count: int
    created_at: dt.datetime
    published_at: dt.datetime | None = None
    author: UserPublic
    category: CategoryOut


class PostList(BaseModel):
    items: list[PostOut]
    total: int


class SiteSettingsOut(BaseModel):
    maintenance_mode: bool


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str


class SignupIn(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class PostCreate(BaseModel):
    title: str
    excerpt: str
    category_id: int
    tags: list[str] = []
    thumbnail_url: str | None = None
    trending_thumbnail_url: str | None = None
    content: str


class PostUpdate(BaseModel):
    title: str | None = None
    excerpt: str | None = None
    content: str | None = None
    status: str | None = None
    thumbnail_url: str | None = None
    trending_thumbnail_url: str | None = None


class CommentIn(BaseModel):
    body: str
