"""Simplified -> Traditional (Taiwan characters, no vocabulary changes), length preserving.

jieba segments each text first (inline wait tags and line-break escapes removed so they
cannot split words), every word is converted by OpenCC s2tw on its own so phrase matches
never straddle word boundaries (plain OpenCC turns 不是只有 into 不是隻有, 电影后 into
電影后, 和面试 into 和麵試), then the hand-reviewed overrides below are applied.
"""
import re
import logging
import jieba
import opencc

jieba.setLogLevel(logging.WARNING)
_cc = opencc.OpenCC('s2tw')

# whole jieba tokens (SC) -> TC
WORD_OVERRIDES = {
    '回归': '回歸', '背负': '背負', '背负着': '背負著', '克制': '克制', '克制不住': '克制不住',
    '玩忽职守': '玩忽職守', '好象': '好像', '象是': '像是', '不象话': '不像話', '别着急': '別著急',
    '喂药': '餵藥', '蜡制': '蠟製', '余光中': '餘光中', '十几分钟': '十幾分鐘', '下钟': '下鐘', '钟起': '鐘起',
    '历翻': '曆翻', '海里': '海裡', '里加': '裡加', '卡里': '卡裡', '城大里': '城大裡',
    '周内': '週內', '周前': '週前', '周是': '週是', '周好': '週好',
    '喉咙干': '喉嚨乾', '变干': '變乾', '干雪': '乾雪', '干下杯': '乾下杯', '干重': '幹重',
    '而松': '而鬆', '要松': '要鬆', '里松': '裡鬆', '包松': '包鬆',
    '托杉浦': '託杉浦', '托依绪': '託依緒', '托和纱': '託和紗',
    '很困': '很睏', '困了': '睏了', '困死': '睏死', '犯困': '犯睏',
    '冲个': '沖個', '水冲': '水沖', '签个': '簽個', '制书': '製書', '加注': '加注', '白面': '白面',
    '划着': '劃著', '姜配': '薑配', '娘家': '娘家', '回娘家': '回娘家',
}
# a token that is exactly this single SC char -> TC
CHAR_DEFAULT = {'钟': '鐘', '周': '週', '松': '鬆', '托': '託', '困': '睏', '卷': '捲', '签': '簽',
                '霉': '霉', '游': '游', '赞': '讚', '姜': '薑'}
# TC normalisation to the Taiwan standard form, applied to every converted word
POST = {'絃': '弦', '孃': '娘', '巖': '岩'}
# (SC context, offset of the char inside it, TC char): matched on tag-free text, applied last
CONTEXT = [
    ('干～杯', 0, '乾'), ('干了三杯', 0, '乾'), ('干一杯', 0, '乾'), ('干干巴', 0, '乾'),
    ('弄干', 1, '乾'), ('舔干', 1, '乾'), ('煮干', 1, '乾'), ('口感不是很干', 5, '乾'), ('嘴唇，好干', 4, '乾'),
    ('喝干', 1, '乾'), ('又干又渴', 1, '乾'), ('基本上已经干了', 5, '乾'), ('不知何时已经干了', 6, '乾'),
    ('『干了』', 1, '乾'), ('干的不是喉', 0, '乾'), ('干笑', 0, '乾'),
    ('长直发', 2, '髮'), ('系上安全带', 0, '繫'), ('关系', 1, '係'),
    ('看了一下表', 4, '錶'), ('表的指针', 0, '錶'), ('看看表', 2, '錶'), ('没有看表', 3, '錶'), ('这样看表', 3, '錶'),
    ('冲了个热水澡', 0, '沖'), ('随便冲一下', 2, '沖'),
    ('求了签', 2, '籤'), ('松井', 0, '松'),
    ('意大利面', 3, '麵'), ('炭烧面', 2, '麵'), ('肉酱面', 2, '麵'), ('一口面', 2, '麵'),
    ('借这个机会', 0, '藉'), ('借喧嚣', 0, '藉'), ('借机会', 0, '藉'), ('借松冈', 0, '藉'),
    ('卷进', 0, '捲'), ('卷了', 0, '捲'), ('卷走', 0, '捲'), ('卷入', 0, '捲'), ('卷起', 0, '捲'),
    ('翻卷', 1, '捲'), ('打卷', 1, '捲'), ('蛋卷', 1, '捲'),
    ('一进一出', 3, '出'), ('背着女孩子用药', 0, '背'), ('你背着我', 1, '背'),
]
# exceptions to the rules above, applied after them
CONTEXT_EXCEPT = [('托显', 0, '托'), ('托着腮', 0, '托'), ('入场卷', 2, '卷'), ('整理卷', 2, '卷')]
# a standalone token 只 right after 这/那 is the measure word 隻, except before these
ZHI_EXCEPT = ('属于', '对我', '懂得')

# only standalone wait tags such as <W10>, and \n / \k escapes; wrapper tags like <F14...> hold text
_TAG = re.compile(r'<[A-Za-z]\d+>|\\[nk]')

# cells that keep the original Japanese glyph because file names in the script use them
JIS_FIXED = {817: '井', 918: '煙', 2814: '湯'}
_OPAQUE = ''


def conv_word(w):
    if w in WORD_OVERRIDES:
        t = WORD_OVERRIDES[w]
    elif len(w) == 1 and w in CHAR_DEFAULT:
        t = CHAR_DEFAULT[w]
    else:
        t = _cc.convert(w)
    assert len(t) == len(w), (w, t)
    return ''.join(POST.get(ch, ch) for ch in t)


def conv_text(s):
    keep = [True] * len(s)
    for m in _TAG.finditer(s):
        for i in range(m.start(), m.end()):
            keep[i] = False
    idx = [i for i in range(len(s)) if keep[i]]
    c = ''.join(s[i] for i in idx)
    out = list(s)
    pos = 0
    for w in jieba.cut(c, HMM=True):
        for k, ch in enumerate(conv_word(w)):
            out[idx[pos + k]] = ch
        if w == '只' and pos > 0 and c[pos - 1] in '这那' and not c.startswith(ZHI_EXCEPT, pos + 1):
            out[idx[pos]] = '隻'
        pos += len(w)
    for pat, off, ch in CONTEXT + CONTEXT_EXCEPT:
        start = c.find(pat)
        while start >= 0:
            out[idx[start + off]] = ch
            start = c.find(pat, start + 1)
    return ''.join(out)


def convert_tokens(toks, table):
    """Traditional char for every text cell token (None for everything else)."""
    s = []
    for t in toks:
        if t[0] == 'cell':
            s.append(JIS_FIXED.get(t[1]) or table[t[1]])
        elif t[0] == 'ch' and len(t[1]) == 1 and t[1] != '�':
            s.append(t[1])
        else:
            s.append(_OPAQUE)
    s = ''.join(s)
    out = conv_text(s)
    assert len(out) == len(s)
    res = []
    for t, a, b in zip(toks, s, out):
        if t[0] == 'cell' and t[1] not in JIS_FIXED:
            res.append(b)
        else:
            assert t[0] == 'cell' or a == b or a == _OPAQUE, (a, b)
            res.append(None)
    return res
