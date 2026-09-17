/* ===== 周报数据：每期一个对象 =====
   每条新闻：
   - id：站内报道编号（news.html?id=xxx）
   - t / d / body[]：简体中文（标题 / 摘要 / 正文段落，正文为站内原创整理）
   - en：{ t, d, body[] } 英文版
   - src / url：来源与原文链接（报道页结尾注明）
   - region：全球/欧洲/北美/拉美/中东/非洲/南亚/东亚/大洋洲/中国 */
window.ISSUES = [
  {
    id: "001",
    img: "assets/img/womens-rights.png",
    date: "2026-09-17",
    period: "2026.09.14 – 2026.09.20",
    title: "她照亮历史：金狮、法案与“120年”之问",
    en: {
      title: "She Lights Up History: A Golden Lion, a New Law, and the 120-Year Question",
      summary: "This week's global roundup: May el-Toukhy wins Venice's Golden Lion, France moves to tighten sexual-violence laws, the WEF warns gender parity is still 120 years away, and Mexico's abortion win inspires the US."
    },
    summary: "本期覆盖全球、欧洲、北美、拉美、中东、非洲、东亚、南亚、大洋洲与中国：梅尔·图琪摘金狮，法国推进打击性暴力法案，世经论坛警告全球性别平等还需120年，墨西哥堕胎权胜利启示美国，日本性别平等排名继续G7垫底。",
    sections: [
      {
        cat: "国际",
        en_cat: "International",
        items: [
          {
            id: "001-1",
            img: "assets/img/vote.png",
            t: "世界经济论坛：全球性别平等还需120年",
            d: "世界经济论坛最新报告警告：按当前速度，全球性别平等仍需要约120年才能实现，呼吁各国加快缩小差距。",
            en: { t: "WEF: Global Gender Parity Is Still 120 Years Away", d: "The World Economic Forum's latest report warns that at the current pace, full global gender parity will take about 120 years — and urges governments and business to accelerate." },
            body: [
              "“全球性别平等还需120年。”这是世界经济论坛最新一期全球性别差距报告给出的判断。报告追踪经济参与、教育、健康与政治赋权四大维度，指出全球性别差距虽在缓慢收窄，但速度远不足以让这一代人看到终点。",
              "报告特别指出，经济参与与机会是差距最大的领域之一：同工不同酬、职业天花板与照护劳动的不平等分配，仍在系统性拖慢女性进入关键岗位的速度。教育维度的差距已基本弥合，但并未自动转化为职场与决策层的平等。",
              "报告呼吁各国政府与企业将性别平等纳入核心议程，而不仅是“附加议题”：扩大带薪育儿假、提高女性在董事会与政坛的比例、投资女性健康与数字技能，都被列为加速路径。"
            ],
            en: { t: "WEF: Global Gender Parity Is Still 120 Years Away", d: "The World Economic Forum's latest report warns that at the current pace, full global gender parity will take about 120 years — and urges governments and business to accelerate.", body: [
              "\"Gender parity is still 120 years away.\" That is the sobering headline of the World Economic Forum's latest Global Gender Gap Report, which tracks gaps in economic participation, education, health and political empowerment.",
              "The widest gap remains in economic participation: unequal pay, the leadership ceiling and the unequal distribution of unpaid care work continue to slow women's advancement. Education gaps have largely closed — yet that progress has not automatically translated into equality at work and in decision-making.",
              "The report urges governments and companies to treat gender equality as a core agenda, not a side topic: expanding paid parental leave, raising women's representation on boards and in parliaments, and investing in women's health and digital skills."
            ] },
            src: "TRT中文",
            url: "https://www.trtzhongwen.com/article/1e667f50d109",
            region: "全球"
          },
          {
            id: "001-2",
            img: "assets/img/podium.png",
            t: "联合国妇女署出席第81届联合国大会",
            d: "联合国妇女署在联大期间发声：性别平等议程“从未如此相关”，呼吁以国家领导力与持续伙伴关系推进妇女议题。",
            en: { t: "UN Women at the 81st UN General Assembly", d: "At this year's General Assembly, UN Women declares that the gender-equality mandate has \"never been more relevant\", calling for national leadership and sustained partnership." },
            body: [
              "在第81届联合国大会召开之际，联合国妇女署发布媒体公告与讲话，重申性别平等在全球议程中的优先地位。妇女署指出，从冲突地区的妇女与女童，到经济危机中首当其冲的女性劳动者，性别不平等的代价正在被越来越清晰地看见。",
              "妇女署强调，“你们赋予我们的使命从未如此相关”。在实现2030可持续发展目标（尤其是目标5：性别平等）的进程明显滞后的背景下，妇女署呼吁成员国拿出国家层面的领导力，并以制度与资金的双重投入兑现承诺。",
              "本届联大期间，妇女署将围绕妇女经济赋权、结束针对妇女的暴力、以及妇女在和平与安全中的参与等议题开展系列边会与高级别对话。"
            ],
            en: { t: "UN Women at the 81st UN General Assembly", d: "At this year's General Assembly, UN Women declares that the gender-equality mandate has \"never been more relevant\", calling for national leadership and sustained partnership.", body: [
              "As the 81st session of the UN General Assembly convenes, UN Women has issued a clear message: the gender-equality mandate is more urgent than ever. From women and girls in conflict zones to women workers hit hardest by economic crises, the cost of inequality is increasingly visible.",
              "\"You gave us a mandate that has never been more relevant,\" UN Women said, urging member states to back commitments with national leadership, institutions and sustained funding — especially as progress on Sustainable Development Goal 5 lags.",
              "During the Assembly, UN Women will hold side events and high-level dialogues on women's economic empowerment, ending violence against women, and women's participation in peace and security."
            ] },
            src: "UN Women",
            url: "https://www.unwomen.org/en/news-stories/media-advisory/2026/09/un-women-at-the-81st-session-of-the-un-general-assembly-unga-81",
            region: "全球"
          },
          {
            id: "001-3",
            img: "assets/img/workplace.png",
            t: "利比里亚：300万美元倡议推动女性领导力与和平建设",
            d: "联合国妇女署与合作伙伴启动300万美元倡议，支持利比里亚女性在领导力、司法与和平建设中的参与。",
            en: { t: "Liberia: US$3 Million Initiative to Advance Women's Leadership and Peacebuilding", d: "UN Women and partners roll out a US$3 million initiative to strengthen Liberian women's participation in leadership, justice and peacebuilding." },
            body: [
              "联合国妇女署与合作伙伴宣布，在利比里亚启动一项总额300万美元的新倡议，聚焦三个方向：女性领导力、司法正义与和平建设。利比里亚曾在2006年选出非洲首位民选女总统，但战后的重建进程并未让女性在决策层的占比持续扩大。",
              "倡议将支持基层女性组织的能力建设，帮助女性候选人参与地方治理，并推动司法系统对性别暴力案件的回应。和平建设部分则将女性的声音纳入社区冲突调解与国家对话机制。",
              "妇女署非洲区域办公室表示，在冲突后国家，女性参与和平进程每增加一分，和平协议的可持续性就提高一分——这笔投资因此被看作对“可持续和平”的直接投入。"
            ],
            en: { t: "Liberia: US$3 Million Initiative to Advance Women's Leadership and Peacebuilding", d: "UN Women and partners roll out a US$3 million initiative to strengthen Liberian women's participation in leadership, justice and peacebuilding.", body: [
              "UN Women and partners have launched a US$3 million initiative in Liberia focused on three pillars: women's leadership, justice and peacebuilding. Liberia made history in 2006 by electing Africa's first female head of state, yet women's share of decision-making has not kept growing in the post-war years.",
              "The initiative will build the capacity of grassroots women's organisations, support women candidates in local governance, and improve the justice system's response to gender-based violence. In peacebuilding, women's voices will be woven into community mediation and national dialogue mechanisms.",
              "As UN Women's regional office puts it, in post-conflict countries every additional seat for women in peace processes makes agreements more durable — so this investment is aimed squarely at sustainable peace."
            ] },
            src: "UN Women Africa",
            url: "https://africa.unwomen.org/en/stories/news/2026/09/un-women-and-partners-roll-out-us3-million-initiative-to-advance-womens-leadership-justice-and-peacebuilding-in-liberia",
            region: "非洲"
          }
        ]
      },
      {
        cat: "政策与法律",
        en_cat: "Policy & Law",
        items: [
          {
            id: "001-4",
            img: "assets/img/women-power.png",
            t: "法国：受“莉安娜案”推动，打击性暴力法案10月审议",
            d: "在社会舆论推动下，法国打击性暴力法案将于10月进入审议，强化对性暴力犯罪的追诉与受害者保护。",
            en: { t: "France: Sexual-Violence Bill to Be Reviewed in October, Driven by the 'Liana Case'", d: "Spurred by a high-profile case and public pressure, a French bill strengthening prosecution of sexual violence and victim protection heads to parliamentary review in October." },
            body: [
              "据欧洲时报报道，法国一项旨在加强打击性暴力的法案将于10月进入议会审议。舆论普遍认为，该法案的加速推进与近期引发全国关注的“莉安娜案”直接相关——这起案件让公众对司法系统处理性暴力案件的方式提出强烈质疑。",
              "法案的核心方向包括：降低性暴力案件的举证与追诉门槛、延长部分罪行的追诉时效，以及强化对受害者的程序保护与援助。支持者认为，法国现行的“同意”认定标准与办案流程对受害者过于苛刻。",
              "过去几年，法国围绕“同意年龄”与性暴力定义的立法讨论反复拉锯。此次法案若获通过，将成为该国#MeToo时代以来最重要的性暴力立法进展之一。"
            ],
            en: { t: "France: Sexual-Violence Bill to Be Reviewed in October, Driven by the 'Liana Case'", d: "Spurred by a high-profile case and public pressure, a French bill strengthening prosecution of sexual violence and victim protection heads to parliamentary review in October.", body: [
              "According to Oushinet (European Times), a French bill toughening the fight against sexual violence will enter parliamentary review in October. Its acceleration is widely linked to the nationwide outcry over the \"Liana case\", which cast doubt on how the justice system handles sexual-violence complaints.",
              "The bill aims to lower evidentiary and prosecution thresholds, extend limitation periods for certain offences, and strengthen procedural protection and support for victims. Advocates argue France's current consent standards and procedures place an unreasonable burden on survivors.",
              "After years of back-and-forth over consent age and the legal definition of sexual violence, this bill — if passed — would rank among the most significant French legislative steps of the post-#MeToo era."
            ] },
            src: "欧洲时报",
            url: "https://www.oushinet.com/static/content/france/2026-09-02/1544740884166357230.html",
            region: "欧洲"
          },
          {
            id: "001-5",
            img: "assets/img/womens-rights.png",
            t: "《浙江省妇女权益保障条例》正式落地",
            d: "条例施行后，浙江多地启动普法基层行活动，推动妇女权益保障从纸面走向实践。",
            en: { t: "Zhejiang's Regulation on Women's Rights Protection Takes Effect", d: "With the new regulation in force, Zhejiang launches grassroots legal-awareness campaigns to turn women's rights protection from paper into practice." },
            body: [
              "《浙江省妇女权益保障条例》本月正式施行，成为继国家上位法修订后，地方层面配套落地的又一重要法规。条例细化了妇女在就业、婚姻家庭、人身安全与财产权益等方面的保护条款，并明确了用人单位、基层组织与政府部门的责任分工。",
              "为配合条例落地，浙江多地启动“普法基层行”活动，通过社区宣讲、案例展板与法律咨询，把条款翻译成普通家庭听得懂的语言。活动第二期已在杭州萧山等区县展开。",
              "地方条例的密集出台，被视为中国妇女权益保障“国家立法—地方配套—基层执行”链条补全的信号：法律的生命，正在于落地。"
            ],
            en: { t: "Zhejiang's Regulation on Women's Rights Protection Takes Effect", d: "With the new regulation in force, Zhejiang launches grassroots legal-awareness campaigns to turn women's rights protection from paper into practice.", body: [
              "Zhejiang Province's Regulation on the Protection of Women's Rights and Interests took effect this month, adding local detail to the national law — covering employment, marriage and family, personal safety and property rights, and spelling out the responsibilities of employers, grassroots organisations and government departments.",
              "To support implementation, Zhejiang has launched community-level legal-awareness campaigns — talks, case exhibitions and free legal clinics that translate legal language into everyday terms. A second round is already underway in districts such as Xiaoshan in Hangzhou.",
              "The rollout is seen as part of a chain from national legislation through local regulation to grassroots enforcement — because the life of a law, ultimately, lies in its implementation."
            ] },
            src: "澎湃新闻",
            url: "https://www.thepaper.cn/newsDetail_forward_34031959",
            region: "中国"
          },
          {
            id: "001-6",
            img: "assets/img/body-choice.png",
            t: "美国：联邦上诉法院再次审理米非司酮案",
            d: "针对堕胎药物米非司酮的诉讼再度进入联邦上诉法院，ACLU呼吁驳回“毫无根据”的挑战。",
            en: { t: "US: Federal Appeals Court Hears Mifepristone Challenge — Again", d: "The long-running lawsuit against the abortion pill mifepristone returns to a federal appeals court, with the ACLU urging judges to reject a \"baseless\" challenge." },
            body: [
              "围绕堕胎药物米非司酮的诉讼再次来到联邦上诉法院。这是自美国最高法院2024年驳回原告资格以来，反对堕胎团体对米非司酮发起的又一轮法律挑战，目标直指FDA对该药物二十余年的批准与使用规则。",
              "美国公民自由联盟（ACLU）在声明中称这场挑战“毫无根据”，指出米非司酮的安全性已被数十项研究证实，并警告：若限制令成立，全美药物流产的可及性将受到严重冲击，尤其是在堕胎服务已大幅收缩的州。",
              "药物流产如今占美国人工终止妊娠总数的六成以上。此案的走向，被视为罗诉韦德案被推翻后，美国生育权利博弈的又一个关键观察点。"
            ],
            en: { t: "US: Federal Appeals Court Hears Mifepristone Challenge — Again", d: "The long-running lawsuit against the abortion pill mifepristone returns to a federal appeals court, with the ACLU urging judges to reject a \"baseless\" challenge.", body: [
              "The legal battle over mifepristone has returned to a federal appeals court. Since the Supreme Court dismissed standing in 2024, anti-abortion groups have mounted a fresh challenge targeting the FDA's decades-old approval and regulation of the drug.",
              "The ACLU calls the case \"baseless\", citing decades of research on the drug's safety, and warns that restricting mifepristone would deal a heavy blow to medication abortion nationwide — especially in states where clinic access has already collapsed.",
              "Medication abortion now accounts for more than 60% of abortions in the United States. The case is being watched as a key test of reproductive rights in the post-Roe era."
            ] },
            src: "ACLU",
            url: "https://www.aclu.org/press-releases/federal-appeals-court-hears-baseless-challenge-to-the-abortion-pill-mifepristone-again",
            region: "北美"
          }
        ]
      },
      {
        cat: "健康与权益",
        en_cat: "Health & Rights",
        items: [
          {
            id: "001-7",
            img: "assets/img/womens-rights.png",
            t: "美国：宫外孕死亡人数近翻倍，得州尤甚",
            d: "研究显示美国宫外孕死亡人数几乎翻倍，限制堕胎的州情况更为严峻，引发对孕产妇健康的广泛担忧。",
            en: { t: "US: Ectopic Pregnancy Deaths Have Nearly Doubled — and It's Worse in Texas", d: "New research shows ectopic-pregnancy deaths in the US have nearly doubled, with the sharpest toll in abortion-restrictive states like Texas." },
            body: [
              "美国国家妇女与家庭伙伴关系组织援引的最新研究显示，美国宫外孕死亡人数在近年几乎翻倍，而在堕胎限制最严格的得克萨斯州，情况更为严峻。宫外孕无法继续妊娠且若不及时处理可危及生命，医疗处置的延误是关键风险因素。",
              "研究者指出，在堕胎禁令生效的州，医生出于对法律风险的顾虑，可能推迟对宫外孕等急症的处理，直到患者出现生命危险。这种“延误医疗”正在把本可避免的悲剧变成现实。",
              "报告呼吁各州立法明确急诊例外条款，并建立医疗机构的免责机制，让医生能够“依法救人而不必惧怕诉讼”。孕产妇健康正在成为美国生育权利争论中最沉重的注脚。"
            ],
            en: { t: "US: Ectopic Pregnancy Deaths Have Nearly Doubled — and It's Worse in Texas", d: "New research shows ectopic-pregnancy deaths in the US have nearly doubled, with the sharpest toll in abortion-restrictive states like Texas.", body: [
              "New research cited by the National Partnership for Women & Families shows that ectopic-pregnancy deaths in the United States have nearly doubled in recent years — with the worst outcomes in states with the strictest abortion bans, such as Texas. An ectopic pregnancy is never viable and can be fatal without prompt treatment.",
              "Researchers point to delays in care: in states with bans, doctors fearing legal liability may postpone treatment of emergencies like ectopic pregnancy until a patient's life is visibly at risk — turning preventable tragedies into reality.",
              "The report calls on states to enact clear emergency exceptions and liability shields so clinicians can save lives without fear of prosecution. Maternal health has become the heaviest footnote in America's abortion debate."
            ] },
            src: "National Partnership for Women & Families",
            url: "https://nationalpartnership.org/news-ectopic-pregnancy-deaths-have-nearly-doubled-and-its-worse-in-texas/",
            region: "北美"
          }
        ]
      },
      {
        cat: "职场平等",
        en_cat: "Workplace Equality",
        items: [
          {
            id: "001-8",
            img: "assets/img/workplace.png",
            t: "日本：性别平等排名全球第117位，继续G7垫底",
            d: "最新排名显示日本男女平等指数仅列全球第117位，在七国集团中持续垫底，职场与政界的性别差距仍是焦点。",
            en: { t: "Japan Ranks 117th in Global Gender Equality — Still Last in the G7", d: "The latest index places Japan 117th worldwide for gender equality, again the worst among G7 nations, with workplace and political gaps in the spotlight." },
            body: [
              "据日本华侨报报道，在最新一期全球性别差距指数中，日本位列第117位，继续在七国集团中垫底。这份由世界经济论坛编制的指数显示，日本在政治赋权与企业管理层女性比例上的得分长期徘徊在低位。",
              "日本国会中女性议员的占比、上市公司女性董事的比例，均远低于欧美主要经济体。尽管政府提出“到2030年将女性管理层比例提升至30%”的目标，但批评者指出，缺乏强制力与配套育儿支持的目标更像口号。",
              "人口老龄化与劳动力短缺本应成为推动女性就业的契机，但非正规雇佣中女性占比偏高、同工不同酬等问题，让“女性经济学”始终未能兑现其承诺。"
            ],
            en: { t: "Japan Ranks 117th in Global Gender Equality — Still Last in the G7", d: "The latest index places Japan 117th worldwide for gender equality, again the worst among G7 nations, with workplace and political gaps in the spotlight.", body: [
              "According to Japan's Overseas Chinese News, Japan ranks 117th in the latest Global Gender Gap Index — once again last among the G7. The World Economic Forum index shows Japan scoring persistently low on political empowerment and women in management.",
              "Women's share of parliamentary seats and of corporate boards remains far below major Western economies. Although the government targets 30% of leadership roles for women by 2030, critics say the goal lacks enforcement and adequate childcare support.",
              "Ageing and labour shortages should have made women's participation an economic necessity — but the high share of women in non-regular work and stubborn pay gaps keep the promise of \"womenomics\" unfulfilled."
            ] },
            src: "日本华侨报",
            url: "http://www.jnocnews.co.jp/n161407.html",
            region: "东亚"
          },
          {
            id: "001-9",
            img: "assets/img/workplace.png",
            t: "澳大利亚：男女平等排名创历史新高",
            d: "最新数据显示澳大利亚男女平等程度达到有记录以来的最高水平。",
            en: { t: "Australia: Gender Equality Ranking Hits Record High", d: "New data shows Australian men and women are more equal than ever on record." },
            body: [
              "澳大利亚最新数据显示，该国男女平等程度达到有记录以来的最高水平。这一进展体现在女性就业率、管理层比例与教育获得的持续改善上。",
              "分析人士指出，强制性的性别薪酬差距公示制度、育儿补贴改革与企业多元目标的普及，是推动排名的关键政策组合。不过，矿业与建筑等传统行业的性别隔离依然明显。",
              "在多数发达国家性别平等进展趋缓的背景下，澳大利亚的上升曲线被研究者视为“政策组合拳”可以奏效的例证。"
            ],
            en: { t: "Australia: Gender Equality Ranking Hits Record High", d: "New data shows Australian men and women are more equal than ever on record.", body: [
              "New data shows gender equality in Australia has reached its highest level on record, driven by steady gains in women's employment, leadership representation and educational attainment.",
              "Analysts credit a mix of policies: mandatory publication of gender pay gaps, childcare subsidy reform, and the spread of corporate diversity targets. Yet occupational segregation in sectors such as mining and construction remains visible.",
              "At a time when progress is stalling in many developed economies, Australia's upward curve is being studied as evidence that a well-designed policy mix can work."
            ] },
            src: "AAP",
            url: "https://www.dailymail.com/wires/aap/article-16135631/Aussie-men-women-ranking-equal-ever.html",
            region: "大洋洲"
          }
        ]
      },
      {
        cat: "生育权利",
        en_cat: "Reproductive Rights",
        items: [
          {
            id: "001-10",
            img: "assets/img/women-power.png",
            t: "墨西哥的堕胎权胜利：拉美经验或为美国提供借鉴",
            d: "拉美女性权利组织指出，墨西哥在堕胎去罪化上的胜利，或为正在激烈博弈的美国提供经验与路径。",
            en: { t: "Mexico's Abortion Victory: Latin America's Lessons for the US", d: "Latin American women's rights groups say Mexico's decriminalisation win may hold the key to the US struggle." },
            body: [
              "拉美女性权利组织近期表示，墨西哥在堕胎去罪化上取得的胜利，或能为正在激烈博弈的美国提供经验与路径。过去数年，墨西哥最高法院裁定堕胎入刑违宪，各州相继跟进，形成被称为“绿色浪潮”的运动。",
              "“绿色浪潮”的核心经验在于：把堕胎权从道德争议重构为公共卫生与自由议题，通过司法途径与街头运动双线推进，并以围巾等符号建立跨阶层认同。阿根廷、哥伦比亚的相继去罪化，让拉美成为全球生育权利运动最活跃的地区之一。",
              "活动人士坦言，美国的联邦体制与两党极化使经验移植并不简单，但“去罪化不等于医疗可及”的教训同样深刻：法律胜利之后，如何让偏远地区的女性真正获得服务，是拉美与美国共同的下半场。"
            ],
            en: { t: "Mexico's Abortion Victory: Latin America's Lessons for the US", d: "Latin American women's rights groups say Mexico's decriminalisation win may hold the key to the US struggle.", body: [
              "Latin American women's rights groups argue that Mexico's abortion decriminalisation could offer lessons for the United States. After Mexico's Supreme Court ruled criminalisation unconstitutional, state after state followed — part of the movement known as the \"Green Wave\".",
              "The Green Wave's playbook: reframe abortion from a moral dispute to a question of public health and freedom, advance through both courts and streets, and build cross-class solidarity around simple symbols such as the green scarf. With Argentina and Colombia following suit, Latin America has become one of the world's most dynamic fronts for reproductive rights.",
              "Activists caution that transplanting the playbook to America's federal system and polarised politics is hard — and that the region's own lesson applies equally: decriminalisation is not the same as access, and getting services to women in remote areas is the second half of the fight."
            ] },
            src: "KRGV",
            url: "https://www.krgv.com/news/latin-america-women-s-rights-groups-say-their-abortion-win-in-mexico-may-hold-the-key-to-us-struggle",
            region: "拉美"
          }
        ]
      },
      {
        cat: "社会",
        en_cat: "Society",
        items: [
          {
            id: "001-11",
            img: "assets/img/womens-rights.png",
            t: "穆斯林世界联盟：针对女性的暴力没有伊斯兰合法性",
            d: "穆斯林世界联盟负责人公开表示，暴力侵害女性没有任何伊斯兰教法依据，呼吁穆斯林社会共同反对基于性别的暴力。",
            en: { t: "Muslim World League: Violence Against Women Has No Islamic Legitimacy", d: "The head of the Muslim World League publicly states that violence against women has no basis in Islamic law, urging Muslim societies to reject gender-based violence." },
            body: [
              "穆斯林世界联盟负责人公开发表声明，明确表示“针对女性的暴力没有任何伊斯兰合法性”。这一表态被外界解读为伊斯兰世界权威机构对基于性别暴力的正式划界。",
              "声明指出，对妇女的暴力行为既违背伊斯兰教法的基本原则，也背离伊斯兰文明对女性尊严与权利的长期传统。联盟呼吁各国穆斯林学者、宗教机构与社会组织共同反对家庭暴力与一切形式的性别暴力。",
              "在全球范围内，宗教领袖的立场对改变社群观念具有独特影响力。妇女权利组织对此表示欢迎，同时强调：声明的真正检验，在于它能否转化为各地社区层面的行动与司法实践。"
            ],
            en: { t: "Muslim World League: Violence Against Women Has No Islamic Legitimacy", d: "The head of the Muslim World League publicly states that violence against women has no basis in Islamic law, urging Muslim societies to reject gender-based violence.", body: [
              "The Secretary-General of the Muslim World League has issued a public statement declaring that \"violence against women has no Islamic legitimacy\" — a line widely read as a formal boundary drawn by one of the Islamic world's most authoritative bodies.",
              "The statement stresses that violence against women violates the foundational principles of Islamic law and contradicts a long tradition of honouring women's dignity and rights. It urges Muslim scholars, religious institutions and civil society to stand together against domestic violence and all forms of gender-based violence.",
              "Globally, religious leaders hold unique power to shift community norms. Women's rights groups welcomed the statement — while noting that its real test is whether it translates into action in local communities and courtrooms."
            ] },
            src: "Africa Intelligence",
            url: "https://www.afintl.com/en/202609111386",
            region: "中东"
          }
        ]
      },
      {
        cat: "文化",
        en_cat: "Culture",
        items: [
          {
            id: "001-12",
            img: "assets/img/womens-rights.png",
            t: "第83届威尼斯电影节：梅尔·图琪凭《女人，未知》摘金狮",
            d: "丹麦导演梅尔·图琪成为史上第八位获金狮奖的女性电影人，主演玛蒂尔德·阿塞尔·F.获最佳女演员奖。授奖辞中她呼吁：照亮共同历史中那些不为人知的女性。",
            en: { t: "Venice 83: May el-Toukhy Wins the Golden Lion for 'The Woman, Unknown'", d: "Danish director May el-Toukhy becomes only the eighth woman to win the Golden Lion; star Mathilde Assef F. takes Best Actress." },
            body: [
              "当地时间9月12日晚，第83届威尼斯电影节落下帷幕。由美国电影人玛吉·吉伦哈尔领衔的主竞赛评审团，将最高荣誉金狮奖授予丹麦导演梅尔·图琪（May el-Toukhy）的《女人，未知》（The Woman, Unknown），韩国导演李沧东凭《可能的爱情》获评审团大奖。",
              "《女人，未知》是这位丹麦出生的埃及裔导演的第三部剧情长片，故事设定在“二战”前后的丹麦：怀有秘密的年轻女管家玛丽准备嫁给富有雇主，而战后对“通敌者”的清算让她的秘密逐渐浮出水面。影片主演玛蒂尔德·阿塞尔·F.同时摘得最佳女演员奖。",
              "本届主竞赛21部入围影片中，《女人，未知》是唯一完全出自女性导演之手的作品。梅尔·图琪由此成为继玛格丽特·冯·特罗塔、阿涅斯·瓦尔达、索菲亚·科波拉、赵婷等人之后，第八位获金狮奖的女性电影人。授奖辞中她直言行业对女性电影人机会的不公，并说自己坚持的动力是“一种迫切的需要——去照亮我们共同历史中那些不为人知的女性”。"
            ],
            en: { t: "Venice 83: May el-Toukhy Wins the Golden Lion for 'The Woman, Unknown'", d: "Danish director May el-Toukhy becomes only the eighth woman to win the Golden Lion; star Mathilde Assef F. takes Best Actress.", body: [
              "On the evening of 12 September, the 83rd Venice Film Festival came to a close on the Lido. The main jury, led by American filmmaker Maggie Gyllenhaal, awarded the Golden Lion to Danish director May el-Toukhy's \"The Woman, Unknown\", with Lee Chang-dong's \"Possible Love\" taking the Grand Jury Prize.",
              "\"The Woman, Unknown\" is the third feature from the Danish-born, Egyptian-descended director. Set around World War II, it follows Marie, a young housekeeper carrying a secret, who is about to marry her wealthy employer — until Denmark's post-war reckoning with \"collaborators\" brings her secret to the surface. Star Mathilde Assef F. also won Best Actress.",
              "Among the 21 films in main competition, \"The Woman, Unknown\" was the only one solely directed by a woman. El-Toukhy becomes only the eighth female filmmaker to win the Golden Lion, after Margarethe von Trotta, Agnès Varda, Sofia Coppola, Chloé Zhao and others. In her speech she was blunt about the industry's unequal treatment of women directors, saying she was driven by \"an urgent need — to illuminate the unknown women of our shared history\"."
            ] },
            src: "澎湃新闻",
            url: "https://m.thepaper.cn/detail/34060150",
            region: "欧洲"
          },
          {
            id: "001-13",
            t: "木心美术馆年度特展“回望张爱玲”",
            d: "以手稿、影像与装置，回望这位影响几代读者的女作家。",
            en: { t: "Muxin Art Museum's Annual Exhibition Looks Back at Eileen Chang", d: "Manuscripts, films and installations revisit the woman writer who shaped generations of readers." },
            body: [
              "木心美术馆2026年度特展“回望张爱玲”近日开展。展览以手稿、照片、影像与装置等多种媒介，回望这位影响了几代读者的女作家——从《倾城之恋》《金锁记》的文学世界，到其与上海、香港两座城市的双重羁绊。",
              "策展方试图呈现一个“立体”的张爱玲：不只是冷峻苍凉的小说家，也是敏锐的散文家、译者与电影编剧。展览特别梳理了她1940年代的电影剧本创作，还原一个长期被“小说家”身份遮蔽的张爱玲。",
              "在一个女性书写被重新发现与重估的时代，“回望张爱玲”既是对一位作家的纪念，也是一次对华语文学女性传统的重新确认。"
            ],
            en: { t: "Muxin Art Museum's Annual Exhibition Looks Back at Eileen Chang", d: "Manuscripts, films and installations revisit the woman writer who shaped generations of readers.", body: [
              "The Muxin Art Museum's 2026 annual exhibition, \"Looking Back at Eileen Chang\", has opened. Through manuscripts, photographs, film clips and installations, it revisits the writer who shaped generations of readers — from the literary world of \"Love in a Fallen City\" and \"The Golden Cangue\" to her dual bonds with Shanghai and Hong Kong.",
              "The curators aim to show a three-dimensional Chang: not only the cool, bleak novelist, but a sharp essayist, translator and screenwriter. The exhibition highlights her 1940s film scripts, restoring a dimension long overshadowed by her identity as a novelist.",
              "In an era when women's writing is being rediscovered and revalued, the exhibition is both a tribute to one writer and a reaffirmation of a female tradition in Chinese-language literature."
            ] },
            src: "展讯",
            url: "https://www.sohu.com/a/1074271399_100152450",
            region: "中国"
          }
        ]
      },
      {
        cat: "科技与公益",
        en_cat: "Tech & Philanthropy",
        items: [
          {
            id: "001-14",
            t: "中国妇基会启动“木兰AI健康计划”",
            d: "中国妇女发展基金会发起“木兰AI健康计划”，并参与发布“我们WOMEN·AI”倡议，推动AI技术惠及女性健康。",
            en: { t: "China Women's Development Foundation Launches 'Mulan AI Health Programme'", d: "The foundation launches an AI-driven women's health programme and joins the 'We WOMEN·AI' initiative." },
            body: [
              "中国妇女发展基金会宣布启动“木兰AI健康计划”，并参与发布“我们WOMEN·AI”倡议。计划旨在利用人工智能技术，提升女性尤其是基层与偏远地区女性的健康服务可及性：从健康筛查、疾病科普到就医导引，AI被设计为“最后一公里”的助手。",
              "倡议同时关注两个面向：一是让AI成为女性健康的工具，二是让更多女性进入AI行业、参与技术的定义。主办方认为，缺乏女性参与的技术，天然难以回应女性需求。",
              "在AI应用加速落地的2026年，“技术向善”与“技术向女”的结合，正在成为中国公益领域的新方向之一。"
            ],
            en: { t: "China Women's Development Foundation Launches 'Mulan AI Health Programme'", d: "The foundation launches an AI-driven women's health programme and joins the 'We WOMEN·AI' initiative.", body: [
              "The China Women's Development Foundation has announced the \"Mulan AI Health Programme\" and joined the launch of the \"We WOMEN·AI\" initiative. The programme aims to use artificial intelligence to make health services more accessible for women, especially in grassroots and remote areas — from screening and health literacy to navigation of care.",
              "The initiative also pushes in a second direction: bringing more women into the AI industry itself. Organisers argue that technology built without women's participation can hardly be expected to answer women's needs.",
              "As AI adoption accelerates in 2026, pairing \"tech for good\" with \"tech for women\" is emerging as a new direction in Chinese philanthropy."
            ] },
            src: "澎湃新闻",
            url: "https://m.thepaper.cn/newsDetail_forward_34084972",
            region: "中国"
          }
        ]
      },
      {
        cat: "体育",
        en_cat: "Sports",
        items: [
          {
            id: "001-15",
            t: "女子板球亚洲杯上演印巴对决",
            d: "2026女子板球亚洲杯印度对阵巴基斯坦的焦点战引发广泛关注，女选手表现持续点亮赛场。",
            en: { t: "Women's Asia Cup: India–Pakistan Clash Lights Up the Tournament", d: "The India–Pakistan showdown at the 2026 Women's Asia Cup drew wide attention as women cricketers continue to shine." },
            body: [
              "2026女子板球亚洲杯迎来最受关注的一场较量：印度对阵巴基斯坦。这场焦点战不仅是两队实力的直接对话，更延续了女子板球近年快速升温的热度。",
              "印度队队长哈曼普丽特·考尔等明星球员的号召力，让女子板球的票房与转播数据连创新高。亚洲多国女队的职业化进程，正在把这项运动带向更广阔的观众。",
              "从看台到屏幕，女子体育的商业价值正在被重新定价——而这背后，是无数女孩第一次拥有了“成为职业运动员”的选项。"
            ],
            en: { t: "Women's Asia Cup: India–Pakistan Clash Lights Up the Tournament", d: "The India–Pakistan showdown at the 2026 Women's Asia Cup drew wide attention as women cricketers continue to shine.", body: [
              "The 2026 Women's Asia Cup staged its most-watched fixture: India versus Pakistan. Beyond the rivalry, the match extended the rapid rise of women's cricket across the region.",
              "The star power of players such as Indian captain Harmanpreet Kaur has pushed ticket sales and broadcast numbers to new highs, while the professionalisation of women's teams across Asia is taking the game to wider audiences.",
              "From stands to screens, the commercial value of women's sport is being repriced — and behind it all, countless girls now have the option of becoming professional athletes."
            ] },
            src: "Sandesh",
            url: "https://sandesh.com/cricket/news/india-vs-pakistan-womens-asia-cup-harmanpreet-kaur",
            region: "南亚"
          }
        ]
      }
    ]
  }
];
