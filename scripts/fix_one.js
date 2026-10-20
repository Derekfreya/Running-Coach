(() => {
  const junk = [
    '.sharedaddy', '.jp-relatedposts', '.related-posts', '.post-navigation',
    '.author-box', '.comments-area', '#comments', '.wpcnt', '.adsbygoogle',
    '.gb-query-loop-wrapper', '.gb-grid-wrapper',
    'script', 'style', 'noscript', 'iframe', 'figure.wp-block-embed'
  ];
  const art = document.querySelector('article .entry-content') || document.querySelector('.entry-content');
  if (!art) return JSON.stringify({error: 'no article'});
  const clone = art.cloneNode(true);
  junk.forEach(s => clone.querySelectorAll(s).forEach(e => e.remove()));
  [...clone.querySelectorAll('h1,h2,h3,h4,h5,h6,p,div,span')].forEach(h => {
    const t = (h.innerText || '').trim();
    if (/^(Related articles?|Related posts?|You might also like|Further reading|Recommended)\s*$/i.test(t)) {
      let n = h;
      while (n) { const nx = n.nextElementSibling; n.remove(); n = nx; }
      h.remove();
    }
  });

  const out = [];
  const walk = (node) => {
    for (const ch of node.childNodes) {
      if (ch.nodeType === 3) {
        const t = ch.textContent.trim();
        if (t) out.push(t);
      } else if (ch.nodeType === 1) {
        const tag = ch.tagName.toLowerCase();
        if (tag === 'h1' || tag === 'h2' || tag === 'h3' || tag === 'h4') {
          const lvl = '#'.repeat(+tag[1] + 1);
          out.push('\n' + lvl + ' ' + ch.innerText.trim() + '\n');
        } else if (tag === 'li') {
          out.push('- ' + ch.innerText.trim());
        } else if (tag === 'blockquote') {
          out.push('\n> ' + ch.innerText.trim().replace(/\n+/g, '\n> ') + '\n');
        } else if (tag === 'br') {
          out.push('');
        } else {
          walk(ch);
        }
      }
    }
  };
  walk(clone);
  let body = out.join('\n').replace(/\n{3,}/g, '\n\n').trim();
  // 末尾再兜底切一刀
  body = body.replace(/\s*Related articles?\s*$/i, '').trim();
  return JSON.stringify({title: document.title, url: location.href, chars: body.length, body});
})();
