import Link from "next/link";

const baseUrl = process.env.API_INTERNAL_URL || "http://127.0.0.1:8000";

async function fetchHome() {
  try {
    const res = await fetch(`${baseUrl}/api/v1/home`, { next: { revalidate: 60 } });
    if (!res.ok) {
      return { trending: [], latest: [], top_writers: [], featured_categories: [] };
    }
    return res.json();
  } catch {
    return { trending: [], latest: [], top_writers: [], featured_categories: [] };
  }
}

export default async function HomePage() {
  const data = await fetchHome();

  return (
    <div className="grid">
      <section className="glass card">
        <h2 className="section-title">Trending Posts</h2>
        <div className="grid">
          {data.trending.slice(0, 6).map((post: any) => (
            <Link key={post.id} href={`/post/${post.slug}`} className="glass card">
              <h3>{post.title}</h3>
              <p className="muted">{post.excerpt}</p>
              <div className="muted">
                {post.author.full_name} · {post.read_time_minutes} min read
              </div>
            </Link>
          ))}
        </div>
        <Link href="/posts" className="muted">
          View All
        </Link>
      </section>

      <section className="glass card">
        <h2 className="section-title">Latest Posts</h2>
        <div className="grid">
          {data.latest.slice(0, 5).map((post: any) => (
            <Link key={post.id} href={`/post/${post.slug}`} className="glass card">
              <h3>{post.title}</h3>
              <p className="muted">{post.excerpt}</p>
              <div className="muted">
                {post.author.full_name} · {post.read_time_minutes} min read
              </div>
            </Link>
          ))}
        </div>
        <Link href="/posts" className="muted">
          View All
        </Link>
      </section>

      <section className="glass card">
        <h2 className="section-title">Top Writers</h2>
        <div className="grid">
          {data.top_writers.slice(0, 5).map((writer: any) => (
            <Link key={writer.id} href={`/writer/${writer.id}`} className="glass card">
              <h3>{writer.full_name}</h3>
              <p className="muted">@{writer.username}</p>
            </Link>
          ))}
        </div>
      </section>

      <section className="glass card">
        <h2 className="section-title">Category Highlights</h2>
        <div className="grid">
          {data.featured_categories.slice(0, 2).map((category: any) => (
            <Link
              key={category.id}
              href={`/category/${category.slug}`}
              className="glass card"
            >
              <h3>{category.name}</h3>
              <p className="muted">Explore stories from {category.name}.</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
