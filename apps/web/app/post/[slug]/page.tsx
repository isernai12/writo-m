import type { Metadata } from "next";

import HeadingTracker from "../../../components/HeadingTracker";

const apiBaseUrl = process.env.API_INTERNAL_URL || "http://127.0.0.1:8000";
const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

async function fetchPost(slug: string) {
  try {
    const res = await fetch(`${apiBaseUrl}/api/v1/posts/${slug}`, { next: { revalidate: 60 } });
    if (!res.ok) {
      return null;
    }
    return res.json();
  } catch {
    return null;
  }
}

function parseSections(content: string) {
  const lines = content.split("\n");
  const sections: { title: string; body: string[] }[] = [];
  let current: { title: string; body: string[] } | null = null;

  lines.forEach((line) => {
    const match = line.match(/^type:\s*toc\s*<(.+)>/i);
    if (match) {
      if (current) {
        sections.push(current);
      }
      current = { title: match[1].trim(), body: [] };
    } else {
      if (!current) {
        current = { title: "Introduction", body: [] };
      }
      current.body.push(line);
    }
  });
  if (current) {
    sections.push(current);
  }
  return sections;
}

function buildSectionId(title: string, index: number) {
  return `${title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-${index}`;
}

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const post = await fetchPost(params.slug);
  if (!post) {
    return { title: "Post not found - Writo" };
  }
  const canonical = `${siteUrl}/post/${post.slug}`;
  return {
    title: `${post.title} - Writo`,
    description: post.excerpt,
    alternates: { canonical },
    openGraph: {
      title: post.title,
      description: post.excerpt,
      url: canonical,
      type: "article",
      images: post.thumbnail_url ? [post.thumbnail_url] : [],
    },
    twitter: {
      card: "summary_large_image",
      title: post.title,
      description: post.excerpt,
    },
  };
}

export default async function PostPage({ params }: { params: { slug: string } }) {
  const post = await fetchPost(params.slug);
  if (!post) {
    return <div className="glass card">Post not found.</div>;
  }

  const sections = parseSections(post.content);
  const trackerSections = [
    ...sections.map((section, index) => ({
      id: buildSectionId(section.title, index),
      title: section.title,
    })),
    { id: "comments", title: "Comments" },
    { id: "related-posts", title: "Related Posts" },
    { id: "footer", title: "Footer" },
  ];

  return (
    <article className="grid">
      <section className="glass card">
        <h1>{post.title}</h1>
        <p className="muted">{post.excerpt}</p>
        <div className="muted">
          {post.author.full_name} · {post.read_time_minutes} min read ·{" "}
          {new Date(post.created_at).toLocaleDateString()}
        </div>
      </section>

      <HeadingTracker sections={trackerSections} />

      <div className="post-content">
        {sections.map((section, index) => (
          <section
            key={section.title}
            id={buildSectionId(section.title, index)}
            data-track="true"
            data-title={section.title}
          >
            <h2>{section.title}</h2>
            {section.body.map((line, lineIndex) => (
              <p key={`${section.title}-${lineIndex}`}>{line}</p>
            ))}
          </section>
        ))}
      </div>

      <section id="comments" data-track="true" data-title="Comments" className="glass card">
        <h2>Comments</h2>
        <p className="muted">Log in to leave a comment.</p>
      </section>

      <section
        id="related-posts"
        data-track="true"
        data-title="Related Posts"
        className="glass card"
      >
        <h2>Related Posts</h2>
        <p className="muted">Discover similar stories curated for you.</p>
      </section>

      <footer id="footer" data-track="true" data-title="Footer" className="glass card">
        <h2>Stay with Writo</h2>
        <p className="muted">Subscribe for weekly editorial highlights.</p>
      </footer>
    </article>
  );
}
