import Link from "next/link";
import type { Metadata } from "next";

const apiBaseUrl = process.env.API_INTERNAL_URL || "http://127.0.0.1:8000";
const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

async function fetchWriter(id: string) {
  try {
    const [writerRes, postsRes] = await Promise.all([
      fetch(`${apiBaseUrl}/api/v1/writers/${id}`, { next: { revalidate: 120 } }),
      fetch(`${apiBaseUrl}/api/v1/writers/${id}/posts`, { next: { revalidate: 120 } }),
    ]);
    return {
      writer: writerRes.ok ? await writerRes.json() : null,
      posts: postsRes.ok ? await postsRes.json() : { items: [] },
    };
  } catch {
    return { writer: null, posts: { items: [] } };
  }
}

export async function generateMetadata({ params }: { params: { id: string } }): Promise<Metadata> {
  const canonical = `${siteUrl}/writer/${params.id}`;
  return {
    title: `Writer ${params.id} - Writo`,
    alternates: { canonical },
    description: `Read posts by writer ${params.id}.`,
  };
}

export default async function WriterPage({ params }: { params: { id: string } }) {
  const data = await fetchWriter(params.id);

  if (!data.writer) {
    return <div className="glass card">Writer not found.</div>;
  }

  return (
    <section className="glass card">
      <h1 className="section-title">{data.writer.full_name}</h1>
      <p className="muted">@{data.writer.username}</p>
      {data.writer.bio && <p className="muted">{data.writer.bio}</p>}

      <div className="grid">
        {data.posts.items.map((post: any) => (
          <Link key={post.id} href={`/post/${post.slug}`} className="glass card">
            <h3>{post.title}</h3>
            <p className="muted">{post.excerpt}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
