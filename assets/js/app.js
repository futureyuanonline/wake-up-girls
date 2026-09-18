/* ===== Wake Up Girls 共用脚本：三语切换 + 站内渲染 ===== */
var state = { lang: null };
try { state.lang = localStorage.getItem('wug-lang') || 'zh-CN'; } catch (e) { state.lang = 'zh-CN'; }

/* ---------- 界面文案字典 ---------- */
var UI = {
  'zh-CN': {
    'nav.latest': '最新', 'nav.archive': '往期', 'nav.works': '作品检索',
    'nav.about': '关于', 'nav.subscribe': '订阅', 'nav.submit': '投稿',
    'nav.cta': '订阅周刊',
    'brand.tag': '全球女性议题周报',
    'hero.label': 'VOL. 001 · 2026年9月第三周',
    'hero.line1': '视角在她，',
    'hero.line2': '规则由她。',
    'hero.mission': '记录女性正在经历的世界，也记录女性正在创造的世界。',
    'note.label': '策展人手记',
    'note.week': '第 {n} 周',
    'hero.lead': '每周，我们为你筛选来自全球的女性权益、性别平等与社会变革重要新闻；建立女性电影、图书、艺术作品检索库——让每一位女性创作者被看见、被找到。',
    'hero.img_caption': '配图 · 示意图',
    'hero.btn.read': '阅读本期 →',
    'hero.btn.works': '进入作品检索库',
    'hero.btn.subscribe': '免费订阅',
    'sec.digest_label': 'The Digest · 本期精选',
    'sec.digest_title': '第 001 期 · 本周要闻',
    'sec.more_archive': '往期全部 →',
    'sec.featured_label': 'Featured · 她的作品',
    'sec.featured_title': '本周推荐',
    'sec.more_works': '进入完整检索库 →',
    'home.read_full': '阅读完整本期 →',
    'footer.tagline': '全球女性议题周报 · 每周五更新',
    'footer.col1': '栏目', 'footer.col2': '关于', 'footer.col3': '使命',
    'footer.mission1': '视角在她，规则由她。',
    'footer.mission2': '记录女性正在经历的世界，也记录女性正在创造的世界。',
    'footer.contact': '联系：futureyuan39@gmail.com',
    'footer.copyright': '© 2026 Wake Up Girls',
    'footer.note': '内容仅供参考 · 欢迎勘误与投稿',
    'footer.images': '图片来源：作品封面与部分配图来自豆瓣、维基共享资源等公开渠道，版权归原作者及权利方所有；本站仅用于作品介绍与资讯检索，不作商业用途。如涉侵权或异议请联系：',
    'archive.label': 'Archive · 往期周报',
    'archive.title': '往期周报',
    'archive.empty': '暂无往期内容。',
    'issue.notfound': '未找到该期',
    'issue.back': '← 返回往期列表',
    'issue.src': '来源',
    'item.why': '为什么值得关注　',
    'issue.read_more': '阅读完整报道 →',
    'news.notfound': '未找到该报道',
    'news.origin': '本文由 Wake Up Girls 编辑部综合整理。原文来源：',
    'news.disclaimer': '内容仅供参考，版权归原作者及原媒体所有。',
    'news.img_caption': '题图 · 示意图',
    'news.img_note': '配图为示意图，非事件现场照片。',
    'news.back_issue': '← 返回本期周报',
    'news.back_home': '回首页',
    'works.label': 'Directory · 她的作品',
    'works.title': '作品检索库',
    'works.intro': '收录女性导演的电影、女性作家的图书与女性艺术家的创作。点击卡片进入站内详情页。',
    'works.placeholder': '搜索：作品名 / 创作者 / 国家 / 关键词…',
    'works.all': '全部', 'works.film': '电影', 'works.book': '图书', 'works.art': '艺术', 'works.theme': '女性题材',
    'works.sort_label': '排序', 'works.sort_default': '默认', 'works.sort_year': '年代', 'works.sort_country': '国家', 'works.sort_alpha': '字母',
    'works.region_all': '全部地区',
    'works.f_country': '国家', 'works.f_decade': '年代', 'works.f_letter': '字母', 'works.f_sort': '排序',
    'works.all_countries': '全部国家', 'works.all_decades': '全部年代', 'works.all_letters': '全部字母',
    'works.sort_new': '年代（新→旧）', 'works.sort_az': '字母 A–Z', 'works.sort_country': '按国家',
    'works.sort_default': '默认顺序',
    'works.count': '共找到 {n} 项',
    'works.keyword': '（关键词：{k}）',
    'works.empty': '没有匹配的作品，换个关键词试试。',
    'work.notfound': '未找到该作品',
    'err.label': '404 · 页面不存在',
    'err.title': '这一页走丢了',
    'err.desc': '你访问的链接可能已失效、或地址输错了。可以回首页看本周精选，或去作品检索库逛逛。',
    'err.home': '回首页',
    'err.works': '作品检索库',
    'work.label': 'Directory · 作品详情',
    'work.coverSrc': '封面图片来自豆瓣 / 维基共享资源等公开渠道，版权归权利人所有，此处仅用于作品介绍。',
    'work.ownPoster': '海报为本站原创设计。',
    'work.award': '荣誉',
    'work.tags': '标签',
    'work.links': '相关链接',
    'work.douban': '在豆瓣检索',
    'work.baike': '在百科检索',
    'work.pd': '免费下载 / 在线阅读（公有领域）',
    'work.pd_note': '该作品已进入公有领域，可合法免费获取。',
    'work.back': '← 返回作品检索库',
    'about.label': '关于我们',
    'about.why_title': '为什么需要 Wake Up Girls',
    'about.why_text': '在信息过载的时代，全球每天都有关于女性权益、性别平等与社会变革的重要新闻发生。但这些声音，往往被淹没在噪音之中。Wake Up Girls 存在的意义，就是让这些声音被听见。',
    'about.mission_label': '我们的使命',
    'about.mission_text': '每周，为中文读者筛选、整理并呈现全球最重要的女性议题新闻——让更多人了解、关注、并参与推动性别平等。',
    'about.v1_t': '独立', 'about.v1_d': '我们不接受任何商业广告或政治赞助。我们的立场只服务于事实与女性权益。',
    'about.v2_t': '全球视野', 'about.v2_d': '从亚洲到非洲，从欧洲到拉丁美洲，我们关注每一个角落的女性故事。',
    'about.v3_t': '公益精神', 'about.v3_d': 'Wake Up Girls 是一个完全公益的项目，所有内容免费开放，永远如此。',
    'about.v4_t': '行动导向', 'about.v4_d': '我们不只报道，我们希望每一篇内容都能激发读者的思考与行动。',
    'about.story_label': '从一个人的阅读习惯，到一份公益周报',
    'about.s1': 'Wake Up Girls 诞生于一个简单的习惯：每周花几个小时，阅读来自全球的女性议题新闻，然后把最重要的内容整理出来，分享给身边的朋友。',
    'about.s2': '慢慢地，这份分享变成了一份周报。周报的读者越来越多，我们意识到，这不只是个人爱好，而是一种需要——中文世界需要一个专注于全球女性议题的独立媒体窗口。',
    'about.s3': '我们没有大团队，没有风险投资，只有一群相信性别平等的人，用业余时间做着这件事。这是我们的选择，也是我们的骄傲。',
    'about.team_label': '我们是谁',
    'about.team_text': 'Wake Up Girls 由一群分布在世界各地的志愿者共同维护。我们来自不同背景，但共同相信：信息是改变的起点。',
    'about.member1_n': '袁秀中', 'about.member1_r': '创始人 & 主编',
    'about.member1_d': '长期关注女性议题与媒体生态，相信每一个被记录的故事都有改变世界的力量。',
    'about.member2_n': '志愿编辑团队', 'about.member2_r': '内容编辑',
    'about.member2_d': '来自全球各地的志愿者，每周共同筛选、翻译并整理新闻内容。',
    'about.join_t': '加入我们',
    'about.join_d': '如果你也相信性别平等，欢迎订阅我们的周报，或者联系我们成为志愿编辑。',
    'about.join_btn': '联系我们',
    'about.subscribe_label': '订阅周报',
    'about.subscribe_text': '每周五，一封邮件，带你了解全球女性议题最新动态。免费订阅，随时退订。',
    'about.contact_label': '联系我们',
    'about.contact_text': '欢迎投稿、勘误，或申请成为志愿编辑。',
    'about.contact_line': '联系与投稿：futureyuan39@gmail.com',
    'subscribe.label': 'Subscribe · 订阅',
    'subscribe.title': '不错过每一个她的故事',
    'subscribe.p': '每周五，一封邮件，带你了解全球女性议题最新动态。免费订阅，随时退订。',
    'subscribe.placeholder': '你的邮箱地址',
    'subscribe.btn': '订阅（发送订阅邮件）',
    'subscribe.note': '当前为本地演示版：点击按钮会打开你的邮件程序，向 futureyuan39@gmail.com 发送一封含你邮箱的订阅申请。正式上线后将接入邮件订阅服务，自动每周推送。',
    'submit.label': 'Submit · 投稿与勘误',
    'submit.title': '把她的故事交给我们',
    'submit.p': '欢迎投稿：新闻线索、选题建议、作品条目（女性创作者的电影 / 图书 / 艺术作品），以及内容勘误。',
    'submit.name': '你的称呼（可不填）',
    'submit.topic': '主题（新闻线索 / 作品条目 / 勘误）',
    'submit.content': '写下内容与来源链接…',
    'submit.btn': '发送投稿邮件',
    'submit.note': '当前为本地演示版：点击按钮会打开你的邮件程序，把内容发送至 futureyuan39@gmail.com。'
  },
  'zh-Hant': {
    'nav.latest': '最新', 'nav.archive': '往期', 'nav.works': '作品檢索',
    'nav.about': '關於', 'nav.subscribe': '訂閱', 'nav.submit': '投稿',
    'nav.cta': '訂閱週刊',
    'brand.tag': '全球女性議題週報',
    'hero.label': 'VOL. 001 · 2026年9月第三週',
    'hero.line1': '視角在她，',
    'hero.line2': '規則由她。',
    'hero.mission': '記錄女性正在經歷的世界，也記錄女性正在創造的世界。',
    'note.label': '策展人手記',
    'note.week': '第 {n} 週',
    'hero.lead': '每週，我們為你篩選來自全球的女性權益、性別平等與社會變革重要新聞；建立女性電影、圖書、藝術作品檢索庫——讓每一位女性創作者被看見、被找到。',
    'hero.img_caption': '配圖 · 示意圖',
    'hero.btn.read': '閱讀本期 →',
    'hero.btn.works': '進入作品檢索庫',
    'hero.btn.subscribe': '免費訂閱',
    'sec.digest_label': 'The Digest · 本期精選',
    'sec.digest_title': '第 001 期 · 本週要聞',
    'sec.more_archive': '往期全部 →',
    'sec.featured_label': 'Featured · 她的作品',
    'sec.featured_title': '本週推薦',
    'sec.more_works': '進入完整檢索庫 →',
    'home.read_full': '閱讀完整本期 →',
    'footer.tagline': '全球女性議題週報 · 每週五更新',
    'footer.col1': '欄目', 'footer.col2': '關於', 'footer.col3': '使命',
    'footer.mission1': '視角在她，規則由她。',
    'footer.mission2': '記錄女性正在經歷的世界，也記錄女性正在創造的世界。',
    'footer.contact': '聯繫：futureyuan39@gmail.com',
    'footer.copyright': '© 2026 Wake Up Girls',
    'footer.note': '內容僅供參考 · 歡迎勘誤與投稿',
    'footer.images': '圖片來源：作品封面與部分配圖來自豆瓣、維基共享資源等公開渠道，版權歸原作者及權利方所有；本站僅用於作品介紹與資訊檢索，不作商業用途。如涉侵權或異議請聯繫：',
    'archive.label': 'Archive · 往期週報',
    'archive.title': '往期週報',
    'archive.empty': '暫無往期內容。',
    'issue.notfound': '未找到該期',
    'issue.back': '← 返回往期列表',
    'issue.src': '來源',
    'item.why': '為什麼值得關注　',
    'issue.read_more': '閱讀完整報導 →',
    'news.notfound': '未找到該報導',
    'news.origin': '本文由 Wake Up Girls 編輯部綜合整理。原文來源：',
    'news.disclaimer': '內容僅供參考，版權歸原作者及原媒體所有。',
    'news.img_caption': '題圖 · 示意圖',
    'news.img_note': '配圖為示意圖，非事件現場照片。',
    'news.back_issue': '← 返回本期週報',
    'news.back_home': '回首頁',
    'works.label': 'Directory · 她的作品',
    'works.title': '作品檢索庫',
    'works.intro': '收錄女性導演的電影、女性作家的圖書與女性藝術家的創作。點擊卡片進入站內詳情頁。',
    'works.placeholder': '搜索：作品名 / 創作者 / 國家 / 關鍵詞…',
    'works.all': '全部', 'works.film': '電影', 'works.book': '圖書', 'works.art': '藝術', 'works.theme': '女性題材',
    'works.sort_label': '排序', 'works.sort_default': '預設', 'works.sort_year': '年代', 'works.sort_country': '國家', 'works.sort_alpha': '字母',
    'works.region_all': '全部地區',
    'works.f_country': '國家', 'works.f_decade': '年代', 'works.f_letter': '字母', 'works.f_sort': '排序',
    'works.all_countries': '全部國家', 'works.all_decades': '全部年代', 'works.all_letters': '全部字母',
    'works.sort_new': '年代（新→舊）', 'works.sort_az': '字母 A–Z', 'works.sort_country': '按國家',
    'works.sort_default': '預設順序',
    'works.count': '共找到 {n} 項',
    'works.keyword': '（關鍵詞：{k}）',
    'works.empty': '沒有匹配的作品，換個關鍵詞試試。',
    'work.notfound': '未找到該作品',
    'err.label': '404 · 頁面不存在',
    'err.title': '這一頁走丟了',
    'err.desc': '你訪問的連結可能已失效、或地址輸錯了。可以回首頁看本週精選，或去作品檢索庫逛逛。',
    'err.home': '回首頁',
    'err.works': '作品檢索庫',
    'work.label': 'Directory · 作品詳情',
    'work.coverSrc': '封面圖片來自豆瓣／維基共享資源等公開渠道，版權歸權利人所有，此處僅用於作品介紹。',
    'work.ownPoster': '海報為本站原創設計。',
    'work.award': '榮譽',
    'work.tags': '標籤',
    'work.links': '相關連結',
    'work.douban': '在豆瓣檢索',
    'work.baike': '在百科檢索',
    'work.pd': '免費下載 / 線上閱讀（公有領域）',
    'work.pd_note': '該作品已進入公有領域，可合法免費獲取。',
    'work.back': '← 返回作品檢索庫',
    'about.label': '關於我們',
    'about.why_title': '為什麼需要 Wake Up Girls',
    'about.why_text': '在資訊過載的時代，全球每天都有關於女性權益、性別平等與社會變革的重要新聞發生。但這些聲音，往往被淹沒在噪音之中。Wake Up Girls 存在的意義，就是讓這些聲音被聽見。',
    'about.mission_label': '我們的使命',
    'about.mission_text': '每週，為中文讀者篩選、整理並呈現全球最重要的女性議題新聞——讓更多人了解、關注、並參與推動性別平等。',
    'about.v1_t': '獨立', 'about.v1_d': '我們不接受任何商業廣告或政治贊助。我們的立場只服務於事實與女性權益。',
    'about.v2_t': '全球視野', 'about.v2_d': '從亞洲到非洲，從歐洲到拉丁美洲，我們關注每一個角落的女性故事。',
    'about.v3_t': '公益精神', 'about.v3_d': 'Wake Up Girls 是一個完全公益的項目，所有內容免費開放，永遠如此。',
    'about.v4_t': '行動導向', 'about.v4_d': '我們不只報導，我們希望每一篇內容都能激發讀者的思考與行動。',
    'about.story_label': '從一個人的閱讀習慣，到一份公益週報',
    'about.s1': 'Wake Up Girls 誕生於一個簡單的習慣：每週花幾個小時，閱讀來自全球的女性議題新聞，然後把最重要的內容整理出來，分享給身邊的朋友。',
    'about.s2': '慢慢地，這份分享變成了一份週報。週報的讀者越來越多，我們意識到，這不只是個人愛好，而是一種需要——中文世界需要一個專注於全球女性議題的獨立媒體窗口。',
    'about.s3': '我們沒有大團隊，沒有風險投資，只有一群相信性別平等的人，用業餘時間做著這件事。這是我們的選擇，也是我們的驕傲。',
    'about.team_label': '我們是誰',
    'about.team_text': 'Wake Up Girls 由一群分佈在世界各地的志願者共同維護。我們來自不同背景，但共同相信：資訊是改變的起點。',
    'about.member1_n': '袁秀中', 'about.member1_r': '創始人 & 主編',
    'about.member1_d': '長期關注女性議題與媒體生態，相信每一個被記錄的故事都有改變世界的力量。',
    'about.member2_n': '志願編輯團隊', 'about.member2_r': '內容編輯',
    'about.member2_d': '來自全球各地的志願者，每週共同篩選、翻譯並整理新聞內容。',
    'about.join_t': '加入我們',
    'about.join_d': '如果你也相信性別平等，歡迎訂閱我們的週報，或者聯繫我們成為志願編輯。',
    'about.join_btn': '聯繫我們',
    'about.subscribe_label': '訂閱週報',
    'about.subscribe_text': '每週五，一封郵件，帶你了解全球女性議題最新動態。免費訂閱，隨時退訂。',
    'about.contact_label': '聯繫我們',
    'about.contact_text': '歡迎投稿、勘誤，或申請成為志願編輯。',
    'about.contact_line': '聯繫與投稿：futureyuan39@gmail.com',
    'subscribe.label': 'Subscribe · 訂閱',
    'subscribe.title': '不錯過每一個她的故事',
    'subscribe.p': '每週五，一封郵件，帶你了解全球女性議題最新動態。免費訂閱，隨時退訂。',
    'subscribe.placeholder': '你的郵箱地址',
    'subscribe.btn': '訂閱（發送訂閱郵件）',
    'subscribe.note': '當前為本地演示版：點擊按鈕會打開你的郵件程式，向 futureyuan39@gmail.com 發送一封含你郵箱的訂閱申請。正式上線後將接入郵件訂閱服務，自動每週推送。',
    'submit.label': 'Submit · 投稿與勘誤',
    'submit.title': '把她的故事交給我們',
    'submit.p': '歡迎投稿：新聞線索、選題建議、作品條目（女性創作者的電影 / 圖書 / 藝術作品），以及內容勘誤。',
    'submit.name': '你的稱呼（可不填）',
    'submit.topic': '主題（新聞線索 / 作品條目 / 勘誤）',
    'submit.content': '寫下內容與來源連結…',
    'submit.btn': '發送投稿郵件',
    'submit.note': '當前為本地演示版：點擊按鈕會打開你的郵件程式，把內容發送至 futureyuan39@gmail.com。'
  },
  en: {
    'nav.latest': 'Latest', 'nav.archive': 'Archive', 'nav.works': 'Directory',
    'nav.about': 'About', 'nav.subscribe': 'Subscribe', 'nav.submit': 'Submit',
    'nav.cta': 'Subscribe',
    'brand.tag': 'Global Women\'s Issues Weekly',
    'hero.label': 'VOL. 001 · THIRD WEEK OF SEPTEMBER 2026',
    'hero.line1': 'Her lens.',
    'hero.line2': 'Her rules.',
    'hero.mission': 'Recording the world women are living through — and the world women are creating.',
    'note.label': "Curator's Note",
    'note.week': 'Week {n}',
    'hero.lead': 'Every week we curate the world\'s most important news on women\'s rights, gender equality and social change — and build a searchable directory of films, books and art by women, so every woman creator can be seen and found.',
    'hero.img_caption': 'Illustrative image',
    'hero.btn.read': 'Read this issue →',
    'hero.btn.works': 'Browse the directory',
    'hero.btn.subscribe': 'Subscribe free',
    'sec.digest_label': 'The Digest · This Week',
    'sec.digest_title': 'Issue 001 · Top Stories',
    'sec.more_archive': 'All issues →',
    'sec.featured_label': 'Featured · Her Works',
    'sec.featured_title': 'This Week\'s Picks',
    'sec.more_works': 'Full directory →',
    'home.read_full': 'Read the full issue →',
    'footer.tagline': 'Global Women\'s Issues Weekly · Every Friday',
    'footer.col1': 'Sections', 'footer.col2': 'About', 'footer.col3': 'Mission',
    'footer.mission1': 'Her lens. Her rules.',
    'footer.mission2': 'Recording the world women are living through — and the world women are creating.',
    'footer.contact': 'Contact: futureyuan39@gmail.com',
    'footer.copyright': '© 2026 Wake Up Girls',
    'footer.note': 'For reference only · Corrections & submissions welcome',
    'footer.images': 'Image credits: covers and some illustrations come from public sources such as Douban and Wikimedia Commons; all rights remain with their original owners. They are shown here for reference and discovery only, not for commercial use. Takedown or objections:',
    'archive.label': 'Archive · Past Issues',
    'archive.title': 'Past Issues',
    'archive.empty': 'No past issues yet.',
    'issue.notfound': 'Issue not found',
    'issue.back': '← Back to archive',
    'issue.src': 'Source',
    'item.why': 'Why it matters　',
    'issue.read_more': 'Read the full story →',
    'news.notfound': 'Story not found',
    'news.origin': 'This article was compiled by the Wake Up Girls editorial team. Original source: ',
    'news.disclaimer': 'For reference only. Copyright belongs to the original author and outlet.',
    'news.img_caption': 'Illustrative image',
    'news.img_note': 'This is an illustrative image, not a photo of the event.',
    'news.back_issue': '← Back to this issue',
    'news.back_home': 'Home',
    'works.label': 'Directory · Her Works',
    'works.title': 'Works Directory',
    'works.intro': 'Films by women directors, books by women writers, and art by women artists. Click a card to open its on-site detail page.',
    'works.placeholder': 'Search: title / creator / country / keyword…',
    'works.all': 'All', 'works.film': 'Films', 'works.book': 'Books', 'works.art': 'Art', 'works.theme': 'Women-themed',
    'works.sort_label': 'Sort', 'works.sort_default': 'Default', 'works.sort_year': 'Year', 'works.sort_country': 'Country', 'works.sort_alpha': 'A–Z',
    'works.region_all': 'All regions',
    'works.f_country': 'Country', 'works.f_decade': 'Decade', 'works.f_letter': 'Letter', 'works.f_sort': 'Sort',
    'works.all_countries': 'All countries', 'works.all_decades': 'All decades', 'works.all_letters': 'All letters',
    'works.sort_new': 'Newest first', 'works.sort_az': 'A–Z', 'works.sort_country': 'By country',
    'works.sort_default': 'Default',
    'works.count': '{n} item(s) found',
    'works.keyword': ' (keyword: {k})',
    'works.empty': 'No matches. Try another keyword.',
    'work.notfound': 'Work not found',
    'err.label': '404 · Page not found',
    'err.title': 'This page went missing',
    'err.desc': "The link may have expired, or the address was mistyped. Head back home for this week's picks, or browse the directory.",
    'err.home': 'Back home',
    'err.works': 'Directory',
    'work.label': 'Directory · Detail',
    'work.coverSrc': 'Cover image sourced from public channels such as Douban / Wikimedia Commons; rights belong to their owners. Shown here for reference only.',
    'work.ownPoster': 'Poster designed by Wake Up Girls.',
    'work.award': 'Recognition',
    'work.tags': 'Tags',
    'work.links': 'Links',
    'work.douban': 'Search on Douban',
    'work.baike': 'Search on Baidu Baike',
    'work.pd': 'Free download / read online (public domain)',
    'work.pd_note': 'This work is in the public domain and can be obtained legally for free.',
    'work.back': '← Back to the directory',
    'about.label': 'About Us',
    'about.why_title': 'Why Wake Up Girls Exists',
    'about.why_text': 'In an age of information overload, important news about women\'s rights, gender equality and social change happens somewhere in the world every single day. Too often, those voices drown in the noise. Wake Up Girls exists to make them heard.',
    'about.mission_label': 'Our Mission',
    'about.mission_text': 'Every week we select, organise and present the world\'s most important stories on women\'s issues for Chinese-language readers — so more people understand, care, and take part in advancing gender equality.',
    'about.v1_t': 'Independent', 'about.v1_d': 'We accept no commercial advertising or political sponsorship. Our only allegiance is to facts and to women\'s rights.',
    'about.v2_t': 'Global Perspective', 'about.v2_d': 'From Asia to Africa, from Europe to Latin America, we follow women\'s stories in every corner of the world.',
    'about.v3_t': 'Non-profit Spirit', 'about.v3_d': 'Wake Up Girls is a fully non-profit project. All content is free and open, always.',
    'about.v4_t': 'Action-oriented', 'about.v4_d': 'We don\'t just report — we hope every piece sparks reflection and action in our readers.',
    'about.story_label': 'From a Personal Reading Habit to a Non-profit Weekly',
    'about.s1': 'Wake Up Girls began with a simple habit: spending a few hours each week reading news about women\'s issues from around the world, then sorting out the most important parts and sharing them with friends.',
    'about.s2': 'Gradually the sharing turned into a weekly newsletter. As its readers grew, we realised this was not just a personal hobby but a need — the Chinese-speaking world needs an independent window focused on global women\'s issues.',
    'about.s3': 'We have no big team and no venture capital — just a group of people who believe in gender equality, doing this in their spare time. It is our choice, and our pride.',
    'about.team_label': 'Who We Are',
    'about.team_text': 'Wake Up Girls is maintained by a group of volunteers around the world. We come from different backgrounds, but share one belief: information is where change begins.',
    'about.member1_n': 'Yuan Xiuzhong', 'about.member1_r': 'Founder & Editor-in-Chief',
    'about.member1_d': 'Long focused on women\'s issues and the media landscape, believing every recorded story has the power to change the world.',
    'about.member2_n': 'Volunteer Editors', 'about.member2_r': 'Content Editors',
    'about.member2_d': 'Volunteers from around the world who every week help select, translate and organise news content.',
    'about.join_t': 'Join Us',
    'about.join_d': 'If you also believe in gender equality, subscribe to our weekly — or contact us to become a volunteer editor.',
    'about.join_btn': 'Contact Us',
    'about.subscribe_label': 'Subscribe to the Weekly',
    'about.subscribe_text': 'One email every Friday, bringing you the latest on global women\'s issues. Free to subscribe, unsubscribe anytime.',
    'about.contact_label': 'Contact Us',
    'about.contact_text': 'Submissions, corrections and volunteer applications are all welcome.',
    'about.contact_line': 'Contact & submissions: futureyuan39@gmail.com',
    'subscribe.label': 'Subscribe · Weekly Email',
    'subscribe.title': 'Never Miss Her Story',
    'subscribe.p': 'One email every Friday, bringing you the latest on global women\'s issues. Free to subscribe, unsubscribe anytime.',
    'subscribe.placeholder': 'Your email address',
    'subscribe.btn': 'Subscribe (send email)',
    'subscribe.note': 'Local demo: the button opens your mail app and sends a subscription request to futureyuan39@gmail.com. After launch, an email service will deliver the weekly issue automatically.',
    'submit.label': 'Submit · Tips & Corrections',
    'submit.title': 'Send Us Her Story',
    'submit.p': 'Welcome: news tips, story ideas, directory entries (films / books / art by women), and corrections.',
    'submit.name': 'Your name (optional)',
    'submit.topic': 'Topic (news tip / directory entry / correction)',
    'submit.content': 'Write your content and source links…',
    'submit.btn': 'Send submission email',
    'submit.note': 'Local demo: the button opens your mail app and sends the content to futureyuan39@gmail.com.'
  }
};

var REGION_EN = { '全球': 'Global', '欧洲': 'Europe', '北美': 'North America', '拉美': 'Latin America',
  '中东': 'Middle East', '非洲': 'Africa', '南亚': 'South Asia', '东亚': 'East Asia',
  '大洋洲': 'Oceania', '中国': 'China' };
var COUNTRY_EN = { '美国': 'USA', '英国': 'UK', '法国': 'France', '中国': 'China', '丹麦': 'Denmark',
  '意大利': 'Italy', '加拿大': 'Canada', '新西兰': 'New Zealand', '日本': 'Japan', '韩国': 'South Korea',
  '中国香港': 'Hong Kong, China', '中国台湾': 'Taiwan, China', '墨西哥': 'Mexico', '北马其顿': 'North Macedonia',
  '尼日利亚': 'Nigeria', '塞尔维亚': 'Serbia', '法国/美国': 'France/USA', '日本/美国': 'Japan/USA',
  '加拿大/美国': 'Canada/USA' };

function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
function isEn() { return state.lang === 'en'; }
function t(key) {
  var d = UI[state.lang] || UI['zh-CN'];
  if (d[key] !== undefined) return d[key];
  return UI['zh-CN'][key] !== undefined ? UI['zh-CN'][key] : key;
}
function L(obj, field) {
  if (!obj) return '';
  if (isEn() && obj.en && obj.en[field] !== undefined) return obj.en[field];
  return obj[field] !== undefined ? obj[field] : '';
}
function fmt(str, map) {
  return String(str).replace(/\{(\w+)\}/g, function (m, k) { return map[k] !== undefined ? map[k] : m; });
}
function dataIssues() { return state.lang === 'zh-Hant' ? (window.ISSUES_HANT || window.ISSUES) : window.ISSUES; }
function dataWorks() { return state.lang === 'zh-Hant' ? (window.WORKS_HANT || window.WORKS) : window.WORKS; }
function regionName(r) { return isEn() ? (REGION_EN[r] || r) : r; }
function catName(sec) { return isEn() ? (sec.en_cat || sec.cat) : sec.cat; }
function countryName(c) { return isEn() ? (COUNTRY_EN[c] || c) : c; }
function workTitle(w) {
  if (isEn()) { var e = window.WORKS_EN && window.WORKS_EN[w.title]; if (e && e.t) return e.t; }
  return w.title;
}
function workCreator(w) {
  if (isEn()) { var e = window.WORKS_EN && window.WORKS_EN[w.title]; if (e && e.c) return e.c; }
  return w.creator;
}
function typeName(c) {
  if (isEn()) return { film: 'Film', book: 'Book', art: 'Art', theme: 'Women-themed' }[c] || c;
  return { film: '电影', book: '图书', art: '艺术', theme: '女性题材' }[c] || c;
}
function workLink(w) {
  var q = encodeURIComponent(w.title.replace(/[《》]/g, ""));
  if (w.c === "film") return "https://search.douban.com/movie/subject_search?search_text=" + q;
  if (w.c === "book") return "https://search.douban.com/book/subject_search?search_text=" + q;
  return "https://www.baidu.com/s?wd=" + encodeURIComponent(w.creator + " " + w.title);
}

/* ---------- 导航高亮 / 语言切换 / 移动菜单 ---------- */
(function () {
  var page = document.body.getAttribute("data-page");
  if (page) {
    document.querySelectorAll("nav.menu a[data-nav]").forEach(function (a) {
      if (a.getAttribute("data-nav") === page) a.classList.add("active");
    });
  }
  var sw = document.getElementById("langSwitch");
  if (sw) {
    sw.querySelectorAll("button").forEach(function (b) {
      b.addEventListener("click", function () {
        state.lang = b.getAttribute("data-lang");
        try { localStorage.setItem("wug-lang", state.lang); } catch (e) {}
        applyLang();
      });
    });
  }
  /* 移动端菜单：点汉堡展开；点链接 / 点空白 / 按 ESC / 转桌面宽度 均收起 */
  var burger = document.getElementById("navBurger");
  var menu = document.getElementById("navMenu");
  if (burger && menu) {
    function setMenu(open) {
      menu.classList.toggle("open", open);
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    }
    burger.setAttribute("aria-expanded", "false");
    burger.setAttribute("aria-controls", "navMenu");
    burger.addEventListener("click", function (e) {
      e.stopPropagation();
      setMenu(!menu.classList.contains("open"));
    });
    menu.addEventListener("click", function (e) {
      if (e.target.closest("a")) setMenu(false);
    });
    document.addEventListener("click", function (e) {
      if (!menu.classList.contains("open")) return;
      if (!menu.contains(e.target) && e.target !== burger && !burger.contains(e.target)) setMenu(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setMenu(false);
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 900) setMenu(false);
    });
  }
})();

function applyLang() {
  document.documentElement.lang = state.lang === 'zh-Hant' ? 'zh-Hant' : (state.lang === 'en' ? 'en' : 'zh-CN');
  document.querySelectorAll("[data-i18n]").forEach(function (el) {
    var v = t(el.getAttribute("data-i18n"));
    if (v) el.textContent = v;
  });
  document.querySelectorAll("[data-i18n-ph]").forEach(function (el) {
    el.placeholder = t(el.getAttribute("data-i18n-ph")) || "";
  });
  var te = document.querySelector("title");
  if (te) {
    var base = te.getAttribute("data-zh") || te.textContent;
    if (state.lang === 'en' && te.getAttribute("data-en")) document.title = te.getAttribute("data-en");
    else if (state.lang === 'zh-Hant' && te.getAttribute("data-hant")) document.title = te.getAttribute("data-hant");
    else document.title = base;
  }
  var hl = document.getElementById("heroLabel");
  if (hl) hl.textContent = t('hero.label');
  var sw = document.getElementById("langSwitch");
  if (sw) sw.querySelectorAll("button").forEach(function (b) {
    b.classList.toggle("on", b.getAttribute("data-lang") === state.lang);
  });
  renderAll();
  afterRender();
}

/* ---------- 配图 ---------- */
function imgBlock(item, catLabel, cls) {
  if (item && item.img) {
    return '<div class="' + cls + '"><img src="' + esc(item.img) + '" alt="' + esc(L(item, 't')) + '" loading="lazy" /></div>';
  }
  return '<div class="' + cls + ' ph-img"><span>' + esc(catLabel || 'Wake Up Girls') + "</span></div>";
}

/* ---------- 滚动动效 / 页面过渡 / 跑马灯 ---------- */
function initChrome() {
  if (!document.querySelector(".atmosphere")) {
    var atmo = document.createElement("div");
    atmo.className = "atmosphere";
    atmo.setAttribute("aria-hidden", "true");
    atmo.innerHTML =
      '<span class="wave w1"></span><span class="wave w2"></span><span class="wave w3"></span>' +
      '<span class="caustic c1"></span><span class="caustic c2"></span>';
    document.body.insertBefore(atmo, document.body.firstChild);
  }
  if (!document.getElementById("scrollBar")) {
    var bar = document.createElement("div");
    bar.id = "scrollBar"; bar.className = "scroll-bar";
    document.body.appendChild(bar);
  }
  if (!document.getElementById("toTop")) {
    var bt = document.createElement("button");
    bt.id = "toTop"; bt.className = "to-top"; bt.type = "button";
    bt.setAttribute("aria-label", "Back to top"); bt.innerHTML = "↑";
    bt.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
    document.body.appendChild(bt);
  }
  if (!document.getElementById("pageVeil")) {
    var veil = document.createElement("div");
    veil.id = "pageVeil"; veil.className = "page-veil leaving";
    document.body.appendChild(veil);
    // 入场：遮罩由不透明渐隐，形成柔和过渡
    requestAnimationFrame(function () {
      setTimeout(function () {
        veil.classList.remove("leaving");
        veil.classList.add("gone");
      }, 60);
    });
  }
}

function initScrollFX() {
  var bar = document.getElementById("scrollBar");
  var header = document.querySelector("header.site");
  var toTop = document.getElementById("toTop");
  var hero = document.querySelector(".hero-ed");
  function onScroll() {
    var y = window.scrollY || document.documentElement.scrollTop || 0;
    var h = document.documentElement.scrollHeight - window.innerHeight;
    if (bar) bar.style.transform = "scaleX(" + (h > 0 ? Math.min(y / h, 1) : 0) + ")";
    if (header) header.classList.toggle("scrolled", y > 10);
    if (toTop) toTop.classList.toggle("show", y > 600);
    if (hero) {
      var hh = hero.offsetHeight || 1;
      var p = Math.min(y / hh, 1);
      hero.style.setProperty("--hero-shift", (y * 0.12) + "px");
      hero.style.setProperty("--hero-fade", (1 - p * 0.8).toFixed(3));
      hero.style.setProperty("--hero-glow", p.toFixed(3));
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}

function initReveal() {
  var els = document.querySelectorAll(".reveal:not(.in)");
  if (!els.length) return;
  if (!("IntersectionObserver" in window)) {
    els.forEach(function (e) { e.classList.add("in"); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
    });
  }, { threshold: 0.1, rootMargin: "0px 0px -60px 0px" });
  els.forEach(function (e) { io.observe(e); });
}

function initTransitions() {
  document.body.classList.add("page-in");
  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest ? e.target.closest("a") : null;
    if (!a) return;
    var href = a.getAttribute("href");
    if (!href || a.target === "_blank" || a.hasAttribute("download")) return;
    if (/^(https?:|mailto:|tel:|#)/.test(href)) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
    e.preventDefault();
    var veil = document.getElementById("pageVeil");
    var go = function () { location.href = href; };
    if (veil) {
      veil.classList.remove("gone");
      veil.classList.add("entering");
      document.body.classList.add("page-out");
      setTimeout(go, 320);
    } else {
      document.body.classList.add("page-out");
      setTimeout(go, 260);
    }
  });
}

function renderTicker() {
  var el = document.getElementById("regionTicker");
  if (!el) return;
  var regions = ["全球", "欧洲", "北美", "拉美", "中东", "非洲", "南亚", "东亚", "大洋洲", "中国"];
  var one = regions.map(function (r) {
    return '<span class="tick">' + esc(regionName(r)) + '</span><span class="tick-dot">◆</span>';
  }).join("");
  el.innerHTML = '<div class="ticker-track">' + one + one + "</div>";
}

function afterRender() {
  initReveal();
  renderTicker();
}

/* ---------- 卡片 ---------- */
function coverFor(idx) {
  return (window.COVERS && window.COVERS[idx]) || (window.POSTERS && window.POSTERS[idx]) || "";
}

function workCard(w, idx) {
  if (idx === undefined || idx === null || (dataWorks()[idx] && dataWorks()[idx].title !== w.title)) {
    var fi = (dataWorks() || []).findIndex(function (x) { return x.title === w.title && x.c === w.c; });
    if (fi >= 0) idx = fi;
  }
  var img = coverFor(idx);
  var meta = [workCreator(w), w.year].filter(Boolean).join(" · ");
  return (
    '<div class="card work-card reveal" style="transition-delay:' + ((idx || 0) % 6) * 50 + 'ms">' +
    '<a href="work.html?i=' + idx + '" class="card-media"><div class="card-img poster">' +
    (img ? '<img src="' + esc(img) + '" alt="' + esc(workTitle(w)) + '" loading="lazy" />' : "") +
    '</div></a>' +
    '<div class="work-meta">' +
    '<div class="card-top"><span class="cat">' + typeName(w.c) + '</span><span class="region">' +
    esc(regionName(w.region) || countryName(w.country)) + "</span></div>" +
    '<h3><a href="work.html?i=' + idx + '">' + esc(workTitle(w)) + "</a></h3>" +
    '<div class="meta">' + esc(meta) + "</div>" +
    (w.a ? '<div class="award">★ ' + esc(w.a) + "</div>" : "") +
    "</div></div>"
  );
}

/* ---------- 首页 ---------- */
function renderLatest() {
  var el = document.getElementById("latest");
  if (!el || !dataIssues() || !dataIssues().length) return;
  var issue = dataIssues()[0];
  // 拉平所有条目（保持分类顺序）
  var flat = [];
  issue.sections.forEach(function (sec) {
    sec.items.forEach(function (it) { flat.push({ it: it, sec: sec }); });
  });
  if (!flat.length) { el.innerHTML = '<p class="muted">…</p>'; return; }

  function metaHtml(o) {
    return '<div class="dg-meta"><span class="dg-cat">' + esc(catName(o.sec)) +
      '</span><span class="dg-region">' + esc(regionName(o.it.region)) + "</span></div>";
  }

  // 大卡（col-span-2）
  var lead = flat[0];
  var html =
    '<article class="dg-lead">' +
      '<a class="dg-media" href="news.html?id=' + esc(lead.it.id) + '">' +
        imgBlock(lead.it, catName(lead.sec), "dg-img") +
      "</a>" +
      '<div class="dg-lead-body">' +
        metaHtml(lead) +
        '<h2><a href="news.html?id=' + esc(lead.it.id) + '">' + esc(L(lead.it, 't')) + "</a></h2>" +
        "<p>" + esc(L(lead.it, 'd')) + "</p>" +
        '<a class="dg-more" href="news.html?id=' + esc(lead.it.id) + '">' + esc(t('issue.read_more')) + "</a>" +
      "</div>" +
    "</article>";

  // 右侧 4 条小条目
  html += '<div class="dg-side">';
  flat.slice(1, 5).forEach(function (o) {
    html +=
      '<article class="dg-item">' +
        '<a class="dg-thumb" href="news.html?id=' + esc(o.it.id) + '">' +
          imgBlock(o.it, catName(o.sec), "dg-timg") +
        "</a>" +
        '<div class="dg-item-body">' +
          metaHtml(o) +
          '<h3><a href="news.html?id=' + esc(o.it.id) + '">' + esc(L(o.it, 't')) + "</a></h3>" +
          "<p>" + esc(L(o.it, 'd')) + "</p>" +
        "</div>" +
      "</article>";
  });
  html += "</div>";
  el.innerHTML = html;
}

function renderFeatured() {
  var el = document.getElementById("featured");
  if (!el || !dataWorks()) return;
  var all = dataWorks();
  var picks = [];
  ["film", "book", "art"].forEach(function (c) {
    var idx = all.findIndex(function (w) { return w.c === c; });
    if (idx >= 0) picks.push({ w: all[idx], i: idx });
  });
  el.innerHTML = picks.map(function (o) {
    var img = coverFor(o.i);
    var meta = [workCreator(o.w), o.w.year].filter(Boolean).join(" · ");
    return '<div class="mini-cell">' +
      '<a class="mini-thumb poster" href="work.html?i=' + o.i + '">' +
      (img ? '<img src="' + esc(img) + '" alt="" loading="lazy" />' : "") + "</a>" +
      '<div class="mini-body">' +
      '<div class="mini-meta"><span class="cat">' + typeName(o.w.c) + '</span><span class="region">' +
      esc(regionName(o.w.region) || countryName(o.w.country)) + "</span></div>" +
      '<h3><a href="work.html?i=' + o.i + '">' + esc(workTitle(o.w)) + "</a></h3>" +
      '<div class="meta">' + esc(meta) + "</div>" +
      (o.w.a ? '<div class="award">★ ' + esc(o.w.a) + "</div>" : "") +
      "</div></div>";
  }).join("");
}

/* ---------- 往期 ---------- */
function renderArchive() {
  var el = document.getElementById("archive-list");
  if (!el || !dataIssues()) return;
  var list = dataIssues();
  if (!list.length) {
    el.innerHTML = '<p class="muted">' + esc(t('archive.empty')) + "</p>";
    return;
  }
  el.innerHTML = list
    .map(function (iss) {
      var items = 0;
      iss.sections.forEach(function (s) { items += s.items.length; });
      return (
        '<a href="issue.html?id=' + esc(iss.id) + '">' +
        '<div class="card reveal" style="margin-bottom:14px;">' +
        '<div class="card-top"><span class="cat">' + (isEn() ? "Issue " : "第 ") + esc(iss.id) + (isEn() ? "" : " 期") + '</span><span class="region">' + esc(iss.period) + "</span></div>" +
        '<h3 style="font-family:var(--serif);font-size:21px;font-weight:700;">' + esc(L(iss, 'title')) + "</h3>" +
        "<p>" + esc(L(iss, 'summary')) + "</p>" +
        '<div class="src">' + items + " " + (isEn() ? "stories" : "条精选") + " · " + (isEn() ? "Read →" : "点击阅读 →") + "</div>" +
        "</div></a>"
      );
    })
    .join("");
}

/* ---------- 单期详情 ---------- */
function renderIssue() {
  var id = new URLSearchParams(location.search).get("id");
  var issue = (dataIssues() || []).find(function (i) { return i.id === id; });
  var el = document.getElementById("issue");
  if (!el) return;
  if (!issue) {
    el.innerHTML = '<div class="panel"><h2>' + esc(t('issue.notfound')) + '</h2><p class="muted"><a href="archive.html">' + esc(t('issue.back')) + "</a></p></div>";
    return;
  }
  document.title = L(issue, 'title') + " | Wake Up Girls";
  var html =
    (issue.img ? '<div class="issue-cover"><img src="' + esc(issue.img) + '" alt="' + esc(L(issue, 'title')) + '" /></div>' : "") +
    '<div class="card" style="margin-bottom:22px;">' +
    '<div class="card-top"><span class="cat">' + (isEn() ? "Issue " : "第 ") + esc(issue.id) + (isEn() ? "" : " 期") + '</span><span class="region">' + esc(issue.period) + "</span></div>" +
    '<h2 style="font-family:var(--serif);font-size:32px;font-weight:800;margin:8px 0;">' + esc(L(issue, 'title')) + "</h2>" +
    '<p class="muted">' + esc(L(issue, 'summary')) + "</p>" +
    "</div>";
  issue.sections.forEach(function (sec) {
    html += '<div class="sec-heading">' + esc(catName(sec)) + "</div>";
    sec.items.forEach(function (it) {
      var thumb = it.img ? '<img class="issue-thumb" src="' + esc(it.img) + '" alt="" loading="lazy" />' : "";
      html +=
        '<div class="issue-item' + (it.img ? ' has-thumb' : '') + '">' + thumb +
        '<h3><a href="news.html?id=' + esc(it.id) + '">' + esc(L(it, 't')) + "</a></h3>" +
        "<p>" + esc(L(it, 'd')) + "</p>" +
        (it.why ? '<p class="why-line"><span class="why-tag">' + esc(t('item.why')) + "</span>" + esc(L(it, 'why')) + "</p>" : "") +
        '<div class="src">' + esc(regionName(it.region)) + " · " + esc(t('issue.src')) + "：" + esc(it.src) + " · " +
        '<a href="news.html?id=' + esc(it.id) + '" style="color:var(--accent);">' + esc(t('issue.read_more')) + "</a></div>" +
        "</div>";
    });
  });
  html +=
    '<p style="margin-top:28px;"><a class="more" href="archive.html" style="color:var(--accent);">' + esc(t('issue.back')) + '</a>　|　<a class="more" href="index.html" style="color:var(--accent);">' + esc(t('news.back_home')) + "</a></p>";
  el.innerHTML = html;
}

/* ---------- 站内报道页 ---------- */
function renderNews() {
  var id = new URLSearchParams(location.search).get("id");
  var el = document.getElementById("news");
  if (!el) return;
  var item = null, issue = null, sec = null;
  (dataIssues() || []).forEach(function (is) {
    (is.sections || []).forEach(function (s) {
      (s.items || []).forEach(function (it) { if (it.id === id) { item = it; issue = is; sec = s; } });
    });
  });
  if (!item) {
    el.innerHTML = '<div class="panel"><h2>' + esc(t('news.notfound')) + '</h2><p class="muted"><a href="index.html">' + esc(t('news.back_home')) + "</a></p></div>";
    return;
  }
  document.title = L(item, 't') + " | Wake Up Girls";
  var body = (L(item, 'body') || []).map(function (p) { return "<p>" + esc(p) + "</p>"; }).join("");
  el.innerHTML =
    '<div class="card" style="margin-bottom:20px;">' +
    '<div class="card-top"><span class="cat">' + esc(catName(sec)) + '</span><span class="region">' + esc(regionName(item.region)) + " · " + esc(issue.period) + "</span></div>" +
    '<h1 class="news-title">' + esc(L(item, 't')) + "</h1>" +
    '<p class="news-lead">' + esc(L(item, 'd')) + "</p>" +
    "</div>" +
    (item.why ? '<div class="why-box"><span class="why-tag">' + esc(t('item.why')) + "</span><p>" + esc(L(item, 'why')) + "</p></div>" : "") +
    '<figure class="news-figure">' + imgBlock(item, catName(sec), "news-img") +
    "<figcaption>" + esc(t('news.img_caption')) + "　·　" + esc(t('news.img_note')) + "</figcaption></figure>" +
    '<div class="news-body">' + body + "</div>" +
    '<div class="news-source">' +
    "<p>" + esc(t('news.origin')) + '<a href="' + esc(item.url) + '" target="_blank" rel="noopener" style="color:var(--accent);">' + esc(item.src) + "</a></p>" +
    '<p class="muted" style="font-size:12.5px;">' + esc(t('news.disclaimer')) + "</p>" +
    "</div>" +
    '<p style="margin-top:24px;"><a class="more" href="issue.html?id=' + esc(issue.id) + '" style="color:var(--accent);">' + esc(t('news.back_issue')) + '</a>　|　<a class="more" href="index.html" style="color:var(--accent);">' + esc(t('news.back_home')) + "</a></p>";
}

/* ---------- 作品检索 ---------- */
function renderWorks() {
  var el = document.getElementById("works");
  if (!el || !dataWorks()) return;
  var all = dataWorks();
  var stateW = { cat: "all", region: "all", country: "all", decade: "all", letter: "all", kw: "", sort: "default" };
  var kwInput = document.getElementById("kw");
  var tabs = document.querySelectorAll("#catTabs button");
  var regionTabs = document.querySelectorAll("#regionTabs button");
  var selCountry = document.getElementById("fCountry");
  var selDecade = document.getElementById("fDecade");
  var selLetter = document.getElementById("fLetter");
  var selSort = document.getElementById("fSort");

  function decadeOf(w) {
    var y = parseInt(w.year, 10);
    if (!y || y < 1000) return "";
    return String(Math.floor(y / 10) * 10);
  }
  function decadeLabel(d) { return isEn() ? d + "s" : d + "年代"; }
  function initialOf(i) { return (window.INITIALS && window.INITIALS[i]) || "其他"; }

  /* 填充下拉（值来自数据本身） */
  function fillSelects() {
    if (!selCountry) return;
    var countries = [];
    all.forEach(function (w) { if (w.country && countries.indexOf(w.country) < 0) countries.push(w.country); });
    countries.sort(function (a, b) { return String(a).localeCompare(String(b), "zh-Hans-CN"); });
    var decades = [];
    all.forEach(function (w) { var d = decadeOf(w); if (d && decades.indexOf(d) < 0) decades.push(d); });
    decades.sort(function (a, b) { return parseInt(b, 10) - parseInt(a, 10); });
    var letters = [];
    all.forEach(function (w, i) { var L = initialOf(i); if (letters.indexOf(L) < 0) letters.push(L); });
    letters.sort();

    selCountry.innerHTML = '<option value="all">' + esc(t('works.all_countries')) + "</option>" +
      countries.map(function (c) { return '<option value="' + esc(c) + '">' + esc(countryName(c)) + "</option>"; }).join("");
    selDecade.innerHTML = '<option value="all">' + esc(t('works.all_decades')) + "</option>" +
      decades.map(function (d) { return '<option value="' + d + '">' + esc(decadeLabel(d)) + "</option>"; }).join("");
    selLetter.innerHTML = '<option value="all">' + esc(t('works.all_letters')) + "</option>" +
      letters.map(function (L) { return '<option value="' + esc(L) + '">' + esc(L) + "</option>"; }).join("");
    if (selSort) {
      selSort.innerHTML =
        '<option value="default">' + esc(t('works.sort_default')) + "</option>" +
        '<option value="year">' + esc(t('works.sort_new')) + "</option>" +
        '<option value="alpha">' + esc(t('works.sort_az')) + "</option>" +
        '<option value="country">' + esc(t('works.sort_country')) + "</option>";
    }
    selCountry.value = stateW.country;
    selDecade.value = stateW.decade;
    selLetter.value = stateW.letter;
    if (selSort) selSort.value = stateW.sort;
  }

  function compare(a, b) {
    var wa = a.w, wb = b.w;
    if (stateW.sort === "year") {
      var ya = parseInt(wa.year, 10) || 0, yb = parseInt(wb.year, 10) || 0;
      if (yb !== ya) return yb - ya;
    } else if (stateW.sort === "alpha") {
      return String(workTitle(wa)).localeCompare(String(workTitle(wb)), "zh-Hans-CN");
    } else if (stateW.sort === "country") {
      var c = String(countryName(wa.country)).localeCompare(String(countryName(wb.country)), "zh-Hans-CN");
      if (c !== 0) return c;
      return (parseInt(wb.year, 10) || 0) - (parseInt(wa.year, 10) || 0);
    }
    return a.i - b.i;
  }

  function apply() {
    var list = all.map(function (w, i) { return { w: w, i: i }; }).filter(function (o) {
      var w = o.w;
      if (stateW.cat !== "all" && w.c !== stateW.cat) return false;
      if (stateW.region !== "all" && w.region !== stateW.region) return false;
      if (stateW.country !== "all" && w.country !== stateW.country) return false;
      if (stateW.decade !== "all" && decadeOf(w) !== stateW.decade) return false;
      if (stateW.letter !== "all" && initialOf(o.i) !== stateW.letter) return false;
      if (!stateW.kw) return true;
      var hay = [workTitle(w), workCreator(w), w.title, w.creator, w.country, w.region, w.d, (w.tags || []).join(" ")].join(" ").toLowerCase();
      return hay.indexOf(stateW.kw.toLowerCase()) >= 0;
    });
    list.sort(compare);
    var cnt = document.getElementById("count");
    if (cnt) cnt.textContent = fmt(t('works.count'), { n: list.length }) + (stateW.kw ? fmt(t('works.keyword'), { k: stateW.kw }) : "");
    el.innerHTML = list.length
      ? list.map(function (o) { return workCard(o.w, o.i); }).join("")
      : '<p class="muted">' + esc(t('works.empty')) + "</p>";
    afterRender();
  }

  if (kwInput) kwInput.addEventListener("input", function () { stateW.kw = kwInput.value.trim(); apply(); });
  tabs.forEach(function (b) {
    b.addEventListener("click", function () {
      tabs.forEach(function (x) { x.classList.remove("on"); });
      b.classList.add("on");
      stateW.cat = b.getAttribute("data-cat");
      apply();
    });
  });
  regionTabs.forEach(function (b) {
    b.addEventListener("click", function () {
      regionTabs.forEach(function (x) { x.classList.remove("on"); });
      b.classList.add("on");
      stateW.region = b.getAttribute("data-region");
      apply();
    });
  });
  if (selCountry) selCountry.addEventListener("change", function () { stateW.country = selCountry.value; apply(); });
  if (selDecade) selDecade.addEventListener("change", function () { stateW.decade = selDecade.value; apply(); });
  if (selLetter) selLetter.addEventListener("change", function () { stateW.letter = selLetter.value; apply(); });
  if (selSort) selSort.addEventListener("change", function () { stateW.sort = selSort.value; apply(); });

  fillSelects();
  apply();
}

/* ---------- 作品详情页 ---------- */
function renderWork() {
  var params = new URLSearchParams(location.search);
  var idxParam = params.get("i");
  var key = params.get("id");
  var el = document.getElementById("work");
  if (!el) return;
  var list = dataWorks() || [];
  var w = null;
  if (idxParam !== null && list[+idxParam]) { w = list[+idxParam]; key = String(encodeURIComponent(w.title)); }
  else if (key) { w = list.find(function (x) { return encodeURIComponent(x.title) === key || x.title === key; }); }
  if (!w) {
    el.innerHTML = '<div class="panel"><h2>' + esc(t('work.notfound')) + '</h2><p class="muted"><a href="works.html">' + esc(t('work.back')) + "</a></p></div>";
    return;
  }
  document.title = workTitle(w) + " | Wake Up Girls";
  var idx = (idxParam !== null && !isNaN(+idxParam)) ? +idxParam : (dataWorks() || []).findIndex(function (x) { return x.title === w.title; });
  var coverImg = (window.COVERS && window.COVERS[idx]) || "";
  var posterImg = coverFor(idx);
  var credit = coverImg ? t('work.coverSrc') : t('work.ownPoster');
  var poster = posterImg
    ? '<div class="work-poster"><img src="' + esc(posterImg) + '" alt="' + esc(workTitle(w)) + '" />' +
      (credit ? '<p class="work-credit">' + esc(credit) + "</p>" : "") + "</div>"
    : "";
  var meta = [workCreator(w), String(w.year), countryName(w.country)].filter(Boolean).join(" · ");
  var links =
    '<div class="work-links"><div class="f-label" data-i18n="work.links">' + esc(t('work.links')) + "</div>" +
    '<a class="work-link" href="' + workLink(w) + '" target="_blank" rel="noopener">' + esc(w.c === 'art' ? t('work.baike') : t('work.douban')) + " ↗</a>";
  var pd = (w.c === 'book' && window.PD_LINKS) ? window.PD_LINKS[w.title] : null;
  if (pd) {
    links +=
      '<a class="work-link pd" href="' + pd + '" target="_blank" rel="noopener">' + esc(t('work.pd')) + " ↗</a>" +
      '<div class="muted" style="font-size:12px;margin-top:4px;">' + esc(t('work.pd_note')) + "</div>";
  }
  links += "</div>";
  var tags = (w.tags || []).length ? '<div class="meta">' + esc(t('work.tags')) + "：" + (w.tags || []).map(function (x) { return esc(x); }).join(" / ") + "</div>" : "";
  el.innerHTML =
    '<div class="card work-detail" style="margin-bottom:20px;">' +
    poster +
    '<div class="work-detail-body">' +
    '<div class="card-top"><span class="cat">' + typeName(w.c) + '</span><span class="region">' +
    esc(regionName(w.region) || countryName(w.country)) + "</span></div>" +
    '<h1 class="news-title">' + esc(workTitle(w)) + "</h1>" +
    '<div class="meta" style="font-size:14px;">' + esc(meta) + "</div>" +
    (w.a ? '<div class="award">★ ' + esc(t('work.award')) + "：" + esc(w.a) + "</div>" : "") +
    '<p class="muted" style="font-size:15px;">' + esc(w.d) + "</p>" +
    tags +
    links +
    "</div></div>" +
    '<p><a class="more" href="works.html" style="color:var(--accent);">' + esc(t('work.back')) + "</a></p>";
}

/* ---------- 策展人手记（首页） ----------
   数据在 data/notes.js：数组为空则整块不显示。
   { id, week, date, title, text, hant:{title,text}, en:{title,text}, by } */
function dataNotes() {
  var list = (state.lang === 'zh-Hant' && window.NOTES_HANT && window.NOTES_HANT.length)
    ? window.NOTES_HANT : (window.NOTES || []);
  return list.slice().sort(function (a, b) { return String(b.id || '').localeCompare(String(a.id || '')); });
}
function noteField(n, k) {
  if (state.lang === 'en') return (n.en && n.en[k]) || n[k] || '';
  if (state.lang === 'zh-Hant') return (n.hant && n.hant[k]) || n[k] || '';
  return n[k] || '';
}
function renderNote() {
  var sec = document.getElementById("noteSec");
  if (!sec) return;
  var list = dataNotes();
  if (!list.length) { sec.hidden = true; return; }
  var n = list[0];                       // 最新一则在最前
  sec.hidden = false;
  var weekEl = document.getElementById("noteWeek");
  if (weekEl) weekEl.textContent = n.week ? t("note.week").replace("{n}", n.week) : (n.date || "");
  var titleEl = document.getElementById("noteTitle");
  if (titleEl) {
    var ti = noteField(n, "title");
    titleEl.textContent = ti;
    titleEl.hidden = !ti;
  }
  var bodyEl = document.getElementById("noteBody");
  if (bodyEl) {
    bodyEl.innerHTML = String(noteField(n, "text") || "")
      .split(/\n{2,}/)
      .filter(function (p) { return p.trim(); })
      .map(function (p) { return "<p>" + esc(p.replace(/\n/g, " ").trim()) + "</p>"; })
      .join("");
  }
  var byEl = document.getElementById("noteBy");
  if (byEl) {
    var by = noteField(n, "by");
    byEl.textContent = by;
    byEl.hidden = !by;
  }
}

/* ---------- 首屏/精选区的期号与链接跟随最新一期 ----------
   这些位置原来写死在 HTML 里，导致每周自动出刊后首页仍显示旧期号。
   （heroLabel 的静态文案只作为无数据时的兜底） */
function syncIssueMeta() {
  var latest = (dataIssues() || [])[0];
  if (!latest) return;
  var isEn = state.lang === 'en';
  var period = latest.period || latest.date || "";
  var hl = document.getElementById("heroLabel");
  if (hl) hl.textContent = (isEn ? "Vol. " : "VOL. ") + latest.id + " · " + period;
  var read = document.querySelector('.hero-btns a[href*="issue.html"]');
  if (read) read.setAttribute("href", "issue.html?id=" + latest.id);
  var vol = document.querySelector(".hero-foot-in .vol");
  if (vol) {
    var ym = String(latest.date || "").slice(0, 7).replace("-", ".");
    vol.textContent = (isEn ? "Vol. " : "VOL. ") + latest.id + (ym ? " — " + ym : "");
  }
  var di = document.querySelector(".digest-issue");
  if (di) di.textContent = isEn ? ("Issue " + latest.id) : ("第 " + latest.id + " 期");
}

/* ---------- 入口 ---------- */
function renderAll() {
  renderNote();
  renderLatest();
  renderFeatured();
  syncIssueMeta();
  renderArchive();
  renderIssue();
  renderNews();
  renderWorks();
  renderWork();
}
document.addEventListener("DOMContentLoaded", function () {
  initChrome();
  initTransitions();
  applyLang();
  initScrollFX();
});
