"use client";

import { useEffect, useState } from "react";

export default function Header() {
  const [compact, setCompact] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [showBookmarks, setShowBookmarks] = useState(false);

  useEffect(() => {
    const onScroll = () => setCompact(window.scrollY > 40);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <header className={`header glass ${compact ? "header-compact" : ""}`}>
        <div className="header-left">
          <a href="/" className="logo">
            Writo
          </a>
          <nav className="nav">
            <a href="/category/technology">Tech</a>
            <a href="/category/design">Design</a>
            <a href="/category/culture">Culture</a>
          </nav>
        </div>
        <div className="header-actions">
          <button className="icon-btn" onClick={() => setShowSearch(true)}>
            Search
          </button>
          <button className="icon-btn" onClick={() => setShowBookmarks(true)}>
            Bookmarks
          </button>
          <button className="icon-btn">Translate</button>
          <button className="icon-btn">Theme</button>
        </div>
      </header>
      {showSearch && (
        <div className="overlay" onClick={() => setShowSearch(false)}>
          <div className="overlay-card glass" onClick={(event) => event.stopPropagation()}>
            <h3>Search Writo</h3>
            <input className="input" placeholder="Search posts, writers, categories" />
            <p className="muted">Search is available on every page.</p>
          </div>
        </div>
      )}
      {showBookmarks && (
        <div className="overlay" onClick={() => setShowBookmarks(false)}>
          <div className="overlay-card glass" onClick={(event) => event.stopPropagation()}>
            <h3>Bookmarks</h3>
            <p className="muted">
              Log in to view and manage your saved posts.
            </p>
          </div>
        </div>
      )}
    </>
  );
}
