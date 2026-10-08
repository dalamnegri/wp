export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    // Route API berita — proxy NewsAPI agar key tidak terekspos ke browser.
    // Key dibaca dari Worker Settings > Variables and secrets > NEWS_API_KEY (tipe Secret).
    if (url.pathname === '/api/berita') {
      const key = env.NEWS_API_KEY;
      if (!key) {
        return Response.json(
          { error: 'NEWS_API_KEY belum diisi (Worker wp > Settings > Variables and secrets).',
            debug_vars: Object.keys(env || {}) },
          { status: 500 }
        );
      }
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
    // Selain itu: sajikan file statis blog.
    return env.ASSETS.fetch(request);
  }
};
