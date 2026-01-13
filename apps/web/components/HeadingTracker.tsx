"use client";

import { useEffect, useMemo, useState } from "react";

type TrackSection = {
  id: string;
  title: string;
};

export default function HeadingTracker({ sections }: { sections: TrackSection[] }) {
  const [current, setCurrent] = useState(sections[0]?.title || "");
  const [progress, setProgress] = useState(0);
  const [open, setOpen] = useState(false);

  const ids = useMemo(() => sections.map((section) => section.id), [sections]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const title = entry.target.getAttribute("data-title");
            if (title) {
              setCurrent(title);
            }
          }
        });
      },
      { rootMargin: "-20% 0px -60% 0px", threshold: 0.1 }
    );

    ids.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [ids]);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.body.scrollHeight - window.innerHeight;
      const pct = docHeight > 0 ? Math.min(100, (scrollTop / docHeight) * 100) : 0;
      setProgress(pct);
    };
    handleScroll();
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="tracker glass">
      <div className="tracker-bar">
        <div className="ring" style={{ ["--progress" as any]: `${progress}%` }}>
          {Math.round(progress)}%
        </div>
        <div>
          <div className="muted">Currently reading</div>
          <strong>{current}</strong>
        </div>
      </div>
      <div className="toc">
        <button className="toc-button" onClick={() => setOpen((prev) => !prev)}>
          Table of contents
        </button>
        {open && (
          <div className="toc-list">
            {sections.map((section) => (
              <button
                key={section.id}
                className="toc-button"
                onClick={() => {
                  setOpen(false);
                  document.getElementById(section.id)?.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                  });
                }}
              >
                {section.title}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
