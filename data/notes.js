/* 策展人手记 —— 首页「本周，我想让你看到」
 *
 * 谁写：主理人本人。这是整个网站的「个人声音」，AI 只做苦力（采集/翻译/排版），不代笔。
 * 篇幅：100–300 字。不要求每期都有观点，记录一件让你停下来想了一下的事就够了。
 * 频率：每周一条，与周报同期。
 *
 * 字段说明（数组为空时，首页不显示手记区块）：
 *   id    期号，如 "001"（用于排序＋归档，新的在前）
 *   week  周数（阿拉伯数字），如 38 → 显示为「第 38 周」
 *   date  日期，如 "2026-09-18"
 *   title 可选小标题（留空则只显示正文）
 *   text  正文，简体，段落之间用 \n\n 分隔
 *   hant  可选繁体版 { title, text }（不写则繁体读者看到简体）
 *   en    可选英文版 { title, text }
 *   by    署名
 */
window.NOTES = [
  {
    id: "001", week: 38, date: "2026-09-18",
    title: '关于她的建筑，报道只有两句话',
    text: '本周我看到一条关于女性建筑师的新闻。她获得了奖项，但报道中用了大量篇幅介绍她的家庭，而对她的建筑作品只有两句话。\n\n我觉得这件事值得被记录下来。',
    hant: {
      title: '關於她的建築，報道只有兩句話',
      text: '本週我看到一條關於女性建築師的新聞。她獲得了獎項，但報道中用了大量篇幅介紹她的家庭，而對她的建築作品只有兩句話。\n\n我覺得這件事值得被記錄下來。'
    },
    en: {
      title: 'Two sentences about her architecture',
      text: 'This week I read a news story about a woman architect. She had won an award, but the report spent a great deal of space on her family, and gave only two sentences to her architectural work.\n\nI think this deserves to be recorded.'
    },
    by: "策展人 · 袁秀中"
  }
];
