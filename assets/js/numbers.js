/* ===== 「数字」栏目：列表页与单条页渲染 =====
   独立文件，不改 app.js 主体：
   * 加载顺序必须在 app.js 之后；
   * 通过包裹全局 applyLang()，在首次加载与切换语言时重绘；
   * 稳定链接 /n/<id> 由 worker 重写到 number.html?id=<id>，
     列表页内跳转仍用 number.html?id=（本地预览也能用）。 */
(function () {
  var L = {
    'zh-CN': {
      'nav.numbers': '数字',
      'num.label': 'The Number · 数字',
      'num.title': '一个数字，五段说清',
      'num.intro': '每期只讲一个数字：它是什么、谁统计的、口径是什么、它不能推出什么、谁可以拿它做什么。缺任何一段，都不发布。',
      'num.s1': '一 · 它是什么',
      'num.s2': '二 · 谁统计的',
      'num.s3': '三 · 口径',
      'num.s4': '四 · 它不能推出什么',
      'num.s5': '五 · 谁可以拿它做什么',
      'num.source': '原始来源',
      'num.cite': '引用这条',
      'num.empty': '还没有条目。',
      'num.more': '阅读全文 →',
      'num.issue': '第 ',
      'num.issueSuffix': ' 期',
      'num.back': '← 返回数字列表',
      'num.draft': '待核查',
      'num.prev': '上一条',
      'num.next': '下一条'
    },
    'zh-Hant': {
      'nav.numbers': '數字',
      'num.label': 'The Number · 數字',
      'num.title': '一個數字，五段說清',
      'num.intro': '每期只講一個數字：它是什麼、誰統計的、口徑是什麼、它不能推出什麼、誰可以拿它做什麼。缺任何一段，都不發布。',
      'num.s1': '一 · 它是什麼',
      'num.s2': '二 · 誰統計的',
      'num.s3': '三 · 口徑',
      'num.s4': '四 · 它不能推出什麼',
      'num.s5': '五 · 誰可以拿它做什麼',
      'num.source': '原始來源',
      'num.cite': '引用這條',
      'num.empty': '還沒有條目。',
      'num.more': '閱讀全文 →',
      'num.issue': '第 ',
      'num.issueSuffix': ' 期',
      'num.back': '← 返回數字列表',
      'num.draft': '待核查',
      'num.prev': '上一條',
      'num.next': '下一條'
    },
    'en': {
      'nav.numbers': 'The Number',
      'num.label': 'The Number',
      'num.title': 'One number, five questions',
      'num.intro': 'Each issue explains a single number: what it is, who counted it, on what definition, what it cannot support, and who can act on it.',
      'num.s1': '1 · What it is',
      'num.s2': '2 · Who counted it',
      'num.s3': '3 · Definition',
      'num.s4': '4 · What it cannot support',
      'num.s5': '5 · Who can act on it',
      'num.source': 'Primary source',
      'num.cite': 'Cite this entry',
      'num.empty': 'No entries yet.',
      'num.more': 'Read →',
      'num.issue': 'Issue ',
      'num.issueSuffix': '',
      'num.back': '← Back to The Number',
      'num.draft': 'Unverified',
      'num.prev': 'Previous',
      'num.next': 'Next'
    }
  };

  function lang() { try { return (typeof state !== 'undefined' && state.lang) ? state.lang : 'zh-CN'; } catch (e) { return 'zh-CN'; } }
  function numT(k) {
    var d = L[lang()] || L['zh-CN'];
    return d[k] != null ? d[k] : (L['zh-CN'][k] || '');
  }
  function E(s) {
    if (typeof esc === 'function') return esc(s);
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function all() { return (typeof window.NUMBERS !== 'undefined' && window.NUMBERS) ? window.NUMBERS : []; }
  function byId(id) {
    var a = all();
    for (var i = 0; i < a.length; i++) if (String(a[i].id) === String(id)) return a[i];
    return null;
  }
  function sorted() {
    return all().slice().sort(function (a, b) {
      return String(b.date || '').localeCompare(String(a.date || '')) ||
        String(a.id || '').localeCompare(String(b.id || ''));
    });
  }
  function citeLine(n) {
    return 'Wake Up Girls：《数字》第 ' + (n.issue || '—') + ' 期，〈' + n.title + '〉，' +
      (n.date || '') + '，https://yuanxiuzhong.com/n/' + n.id;
  }
  function applyNumLang() {
    var nodes = document.querySelectorAll('[data-numi18n]');
    for (var i = 0; i < nodes.length; i++) {
      var v = numT(nodes[i].getAttribute('data-numi18n'));
      if (v) nodes[i].textContent = v;
    }
  }

  /* ---------- 列表页 ---------- */
  function renderNumbers() {
    var el = document.getElementById('numbers');
    if (!el) return;
    var list = sorted();
    if (!list.length) { el.innerHTML = '<p class="muted">' + E(numT('num.empty')) + '</p>'; return; }
    el.innerHTML = list.map(function (n) {
      var lead = String(n.what || '');
      if (lead.length > 88) lead = lead.slice(0, 88) + '…';
      return '<a class="num-card' + (n.draft ? ' is-draft' : '') + '" href="number.html?id=' + encodeURIComponent(n.id) + '">' +
        '<div class="num-value">' + E(n.value) +
        (n.valueLabel ? ' <small>' + E(n.valueLabel) + '</small>' : '') + '</div>' +
        '<h3 class="num-card-title">' + E(n.title) + '</h3>' +
        '<p class="num-card-lead">' + E(lead) + '</p>' +
        '<div class="num-meta">' + E(numT('num.issue') + (n.issue || '—') + numT('num.issueSuffix')) +
        (n.date ? ' · ' + E(n.date) : '') + (n.topic ? ' · ' + E(n.topic) : '') +
        (n.draft ? ' · <span class="num-flag">' + E(numT('num.draft')) + '</span>' : '') +
        '</div></a>';
    }).join('');
  }

  /* ---------- 单条页 ---------- */
  function renderNumber() {
    var el = document.getElementById('number');
    if (!el) return;
    var id = '';
    try { id = new URLSearchParams(location.search).get('id') || ''; } catch (e) { }
    if (!id) id = (sorted()[0] || {}).id || '';
    var n = byId(id);
    if (!n) {
      el.innerHTML = '<div class="panel"><h2>' + E(numT('num.empty')) + '</h2>' +
        '<p class="muted"><a href="numbers.html">' + E(numT('num.back')) + '</a></p></div>';
      return;
    }
    document.title = n.title + ' | Wake Up Girls';
    var cannot = (n.cannot || []).map(function (c) { return '<li>' + E(c) + '</li>'; }).join('');
    var src = n.source || {};
    el.innerHTML =
      '<article class="num-article">' +
        '<div class="num-hero">' +
          '<div class="num-kicker">' + E(numT('num.label')) + ' · ' +
            E(numT('num.issue') + (n.issue || '—') + numT('num.issueSuffix')) +
            (n.draft ? ' · <span class="num-flag">' + E(numT('num.draft')) + '</span>' : '') + '</div>' +
          '<div class="num-value num-value-lg">' + E(n.value) +
            (n.valueLabel ? ' <small>' + E(n.valueLabel) + '</small>' : '') + '</div>' +
          '<h1 class="num-headline">' + E(n.title) + '</h1>' +
          '<div class="num-meta">' + E(n.date || '') + (n.topic ? ' · ' + E(n.topic) : '') + '</div>' +
        '</div>' +
        (n.claim ? '<div class="num-claim">' +
          '<div class="num-claim-label">' +
            E(({ 'zh-CN': '这一条唯一能支撑的结论', 'zh-Hant': '這一條唯一能支撐的結論',
                 en: 'The one claim this entry supports' })[lang()] || '这一条唯一能支撑的结论') +
          '</div><p>' + E(n.claim) + '</p></div>' : '') +
        '<section class="num-block"><h2>' + E(numT('num.s1')) + '</h2><p>' + E(n.what) + '</p></section>' +
        '<section class="num-block"><h2>' + E(numT('num.s2')) + '</h2><p>' + E(n.who) + '</p>' +
          (src.url ? '<p class="num-src"><a href="' + E(src.url) + '" target="_blank" rel="noopener">' +
            E(numT('num.source')) + '：' + E(src.name || src.url) + '</a></p>' : '') + '</section>' +
        '<section class="num-block"><h2>' + E(numT('num.s3')) + '</h2><p>' + E(n.caliber) + '</p></section>' +
        '<section class="num-block num-cannot"><h2>' + E(numT('num.s4')) + '</h2><ul>' + cannot + '</ul></section>' +
        '<section class="num-block"><h2>' + E(numT('num.s5')) + '</h2><p>' + E(n.action) + '</p></section>' +
        '<div class="num-cite"><div class="num-cite-label">' + E(numT('num.cite')) + '</div>' +
          '<code>' + E(citeLine(n)) + '</code></div>' +
        '<p class="num-nav"><a href="numbers.html">' + E(numT('num.back')) + '</a></p>' +
      '</article>';
  }

  function boot() {
    applyNumLang();
    renderNumbers();
    renderNumber();
  }

  /* 包裹 applyLang：首次加载与切语言都重绘（app.js 里 DOMContentLoaded 会调用它） */
  var _applyLang = (typeof window.applyLang === 'function') ? window.applyLang : null;
  window.applyLang = function () {
    if (_applyLang) { try { _applyLang.apply(window, arguments); } catch (e) { } }
    boot();
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
