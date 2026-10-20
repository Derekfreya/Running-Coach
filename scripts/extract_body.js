(() => {
  // 精确定位正文容器，剔除结尾的参考链接/相关文章
  const root = document.querySelector('article .entry-content') || document.querySelector('article');
  if (!root) return JSON.stringify({error: 'no container'});

  const clone = root.cloneNode(true);

  // 剔除常见噪音块
  const junk = [
    '.sharedaddy', '.jp-relatedposts', '.related-posts', '.post-navigation',
    '.author-box', '.comments-area', '#comments', '.wpcnt', '.adsbygoogle',
    '.gb-query-loop-wrapper', '.gb-grid-wrapper',
    'script', 'style', 'noscript', 'iframe', 'figure.wp-block-embed'
  ];
  junk.forEach(s => clone.querySelectorAll(s).forEach(e => e.remove()));

  // 精确切除"Related articles"标题及其后续全部内容
  [...clone.querySelectorAll('h1,h2,h3,h4')].forEach(h => {
    if (/^\s*(Related articles?|Related posts?|You might also like|Further reading|Recommended)\s*$/i.test(h.innerText.trim())) {
      let n = h;
      while (n) { const nx = n.nextElementSibling; n.remove(); n = nx; }
      h.remove();
    }
  });
  // 兜底：整块 grid 容器
  clone.querySelectorAll('[class*="gb-query-loop"],[class*="related-posts"],[class*="jp-relatedposts"]')
       .forEach(e => e.remove());

  // 标题
  const h1 = document.querySelector('article h1') || document.querySelector('h1');

  // 逐块提取，保留结构语义
  const blocks = [];
  const walk = (node) => {
    node.childNodes.forEach(n => {
      if (n.nodeType !== 1) return;
      const tag = n.tagName.toLowerCase();
      if (/^h[1-6]$/.test(tag)) {
        blocks.push(`\n${'#'.repeat(+tag[1])} ${n.innerText.trim()}\n`);
      } else if (tag === 'ul' || tag === 'ol') {
        blocks.push('');
        n.querySelectorAll(':scope > li').forEach(li => {
          blocks.push(`- ${li.innerText.trim().replace(/\s+/g, ' ')}`);
        });
        blocks.push('');
      } else if (tag === 'table') {
        blocks.push('\n[表格]');
        n.querySelectorAll('tr').forEach(tr => {
          const cells = [...tr.querySelectorAll('th,td')].map(c => c.innerText.trim().replace(/\s+/g, ' '));
          blocks.push('| ' + cells.join(' | ') + ' |');
        });
        blocks.push('');
      } else if (tag === 'blockquote') {
        blocks.push('\n> ' + n.innerText.trim().replace(/\n/g, '\n> ') + '\n');
      } else if (tag === 'figure') {
        const cap = n.querySelector('figcaption');
        const img = n.querySelector('img');
        blocks.push(`\n[图片] ${img ? img.alt || img.src : ''} ${cap ? '— ' + cap.innerText.trim() : ''}\n`);
      } else if (['p', 'div', 'section'].includes(tag)) {
        // 递归，但避免 div 包裹导致重复
        const hasBlockChild = [...n.children].some(c => /^(P|DIV|SECTION|UL|OL|H[1-6]|TABLE|BLOCKQUOTE|FIGURE)$/.test(c.tagName));
        if (hasBlockChild) { walk(n); }
        else {
          const t = n.innerText.trim();
          if (t) blocks.push(t + '\n');
        }
      }
    });
  };
  walk(clone);

  let body = blocks.join('\n').replace(/\n{3,}/g, '\n\n').trim();

  // 截断结尾的"相关文章/推荐文章"区块
  // 特征：出现形如 "Read more" 的推荐摘要，或 "## 标题 \n 日期 \n 摘要"
  const cutMarkers = [
    /\n#{2,3}\s*Related\s+Posts?\b/i,
    /\n#{2,3}\s*You\s+Might\s+Also\s+Like\b/i,
    /\n#{2,3}\s*Further\s+Reading\b/i,
    /\n#{2,3}\s*References?\b\s*\n/i,
    /\n#{2,3}\s*Sources?\b\s*\n/i,
    /\nRead more\s*$/im
  ];
  let cutAt = -1;
  for (const m of cutMarkers) {
    const idx = body.search(m);
    if (idx > body.length * 0.5 && (cutAt === -1 || idx < cutAt)) cutAt = idx;
  }
  // 兜底：若结尾 15% 内出现连续 "Read more" 推荐块
  if (cutAt === -1) {
    const tail = body.slice(Math.floor(body.length * 0.85));
    const rm = tail.search(/\n[A-Z][^\n]{10,120}\n\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\s*\n/);
    if (rm !== -1) cutAt = Math.floor(body.length * 0.85) + rm;
  }
  if (cutAt > 0) body = body.slice(0, cutAt).trim();

  // 抓取所有内部文章链接（用于枚举语料，不写入正文）
  const links = [...document.querySelectorAll('article .entry-content a[href*="runningwritings.com"]')]
    .map(a => a.href.split('#')[0])
    .filter(h => /\/(19|20)\d\d\/\d\d\/[^\/]+\.html$/.test(h));

  return JSON.stringify({
    title: h1 ? h1.innerText.trim() : document.title,
    url: location.href,
    chars: body.length,
    links: [...new Set(links)],
    body: body
  });
})()
