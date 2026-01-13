import Link from "next/link";
import type { Metadata } from "next";

const apiBaseUrl = process.env.API_INTERNAL_URL || "http://127.0.0.1:8000";
const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

async function fetchCategory(slug: string) {
  try {
    const res = await fetch(`${apiBaseUrl}/api/v1/categories/${slug}/posts`, { next: { revalidate: 120 } });
    if (!res.ok) {
      return { items: [], total: 0 };
    }
    return res.json();
  } catch {
    return { items: [], total: 0 };
  }
}

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const canonical = `${siteUrl}/category/${params.slug}`;
  return {
    title: `Category ${params.slug} - Writo`,
    alternates: { canonical },
    description: `Read ${params.slug} stories on Writo.`,
  };
}

export default async function CategoryPage({ params }: { params: { slug: string } }) {
  const data = await fetchCategory(params.slug);

  return (
    <section className="glass card">
      <h1 className="section-title">Category: {params.slug}</h1>
      <div className="grid">
        {data.items.map((post: any) => (
          <Link key={post.id} href={`/post/${post.slug}`} className="glass card">
            <h3>{post.title}</h3>
            <p className="muted">{post.excerpt}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
