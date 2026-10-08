export async function onRequestGet(context) {
  // Cloudflare Pages Function — proxy NewsAPI agar API key TIDAK terekspos di browser.
  // Cara pakai: set Environment Variable NEWS_API_KEY di dashboard Pages
  // (Settings > Environment variables), JANGAN tulis key di kode/repo.
  const key = context.env.NEWS_API_KEY;
  if (!key) {
    return Response.json({ error: 'NEWS_API_KEY belum diset di Pages > Settings > Environment variables.' }, { status: 500 });
  }
  const url = new URL(context.request.url);
  const cat = url.searchParams.get('cat') || 'health';
  const api = `https://newsapi.org/v2/top-headlines?country=id&category=${encodeURIComponent(cat)}&pageSize=12&apiKey=${encodeURIComponent(key)}`;
  try {
    const r = await fetch(api, { cf: { cacheTtl: 1800, cacheEverything: true } });
    const j = await r.json();
    if (j.status !== 'ok') {
      return Response.json({ error: j.message || 'NewsAPI error' }, { status: 502 });
    }
    const articles = (j.articles || []).map(a => ({
      title: a.title, description: a.description, url: a.url,
      image: a.urlToImage, source: a.source && a.source.name,
      publishedAt: a.publishedAt
    }));
    return Response.json({ articles }, {
      headers: { 'Cache-Control': 'public, max-age=1800', 'Access-Control-Allow-Origin': '*' }
    });
  } catch (e) {
    return Response.json({ error: 'Gagal menghubungi NewsAPI.' }, { status: 502 });
  }
}
