"""NLP intent parser for insurance queries — rule-based, no external API needed.

Handles Chinese and English natural language queries about insurance products.
Extracts: product type, age, sum insured, term, gender, rate, payment frequency.
"""

import re

# ── Product keywords ────────────────────────────────────────────────

PRODUCTS = {
    'term_life': {
        'zh': ['定期寿险', '定期', 'term life', 'term'],
        'en': ['term life', 'term'],
    },
    'whole_life': {
        'zh': ['终身寿险', '终身', 'whole life'],
        'en': ['whole life'],
    },
    'annuity': {
        'zh': ['生存年金', '年金', 'annuity', '领钱', '领取'],
        'en': ['annuity', 'life annuity', 'payout'],
    },
    'endowment': {
        'zh': ['两全保险', '两全', 'endowment', '返还', '到期'],
        'en': ['endowment'],
    },
    'deferred_annuity': {
        'zh': ['递延年金', '递延领取', '退休', '养老'],
        'en': ['deferred annuity', 'retirement'],
    },
    'deferred_assurance': {
        'zh': ['递延寿险'],
        'en': ['deferred assurance', 'deferred life'],
    },
    'pure_endowment': {
        'zh': ['纯生存', 'pure endowment', '存活给付'],
        'en': ['pure endowment', 'survival benefit'],
    },
}


def detect_product(text):
    """Detect which insurance product the user is asking about."""
    text_lower = text.lower()
    scores = {}
    for product, keywords in PRODUCTS.items():
        score = 0
        for kw in keywords['zh'] + keywords['en']:
            if kw.lower() in text_lower:
                score += 1
        if score > 0:
            scores[product] = score
    if not scores:
        return 'term_life'
    return max(scores, key=scores.get)


def extract_params(text):
    """Extract numeric parameters from natural language text.

    Handles:
    - "30岁" → age=30
    - "100万" → 1,000,000
    - "200万元" → 2,000,000
    - "20年" → term=20
    - "男/女" → gender
    - "3.5%" → rate
    - "月缴/年缴" → frequency
    """
    params = {}

    # Age: "30岁", "age 30", "age:30"
    age_match = re.search(r'(\d+)\s*岁|age\s*:?\s*(\d+)', text, re.IGNORECASE)
    if age_match:
        params['age'] = int(age_match.group(1) or age_match.group(2))

    # Sum insured: "100万", "200万元", "保额100万", "1000000"
    si_match = re.search(r'(\d+)\s*万\s*(元)?|保额\s*(\d+)(万|万元)|sum\s*:?\s*(\d[\d,]*)', text, re.IGNORECASE)
    if si_match:
        if si_match.group(1):
            params['sum_insured'] = int(si_match.group(1)) * 10000
        elif si_match.group(3):
            params['sum_insured'] = int(si_match.group(3)) * 10000
        elif si_match.group(5):
            params['sum_insured'] = int(si_match.group(5).replace(',', ''))

    # Term: "20年", "term 20", "期限20"
    term_match = re.search(r'(\d+)\s*年|term\s*:?\s*(\d+)|期限\s*(\d+)', text, re.IGNORECASE)
    if term_match:
        params['term'] = int(term_match.group(1) or term_match.group(2) or term_match.group(3))

    # Gender
    if re.search(r'男|male', text, re.IGNORECASE):
        params['gender'] = 'M'
    elif re.search(r'女|female', text, re.IGNORECASE):
        params['gender'] = 'F'

    # Interest rate: "3.5%", "利率3.5"
    rate_match = re.search(r'(\d+\.?\d*)\s*%|利率\s*(\d+\.?\d*)', text)
    if rate_match:
        params['rate'] = float(rate_match.group(1) or rate_match.group(2)) / 100

    # Payment frequency
    if re.search(r'月缴|monthly|月', text, re.IGNORECASE):
        params['freq'] = 'monthly'
    elif re.search(r'季缴|quarterly|季', text, re.IGNORECASE):
        params['freq'] = 'quarterly'
    elif re.search(r'半年|semi', text, re.IGNORECASE):
        params['freq'] = 'semi'
    elif re.search(r'年缴|annual|年', text, re.IGNORECASE):
        params['freq'] = 'annual'

    # Maturity age (for deferred/pure endowment)
    mat_match = re.search(r'(\d+)\s*岁.*领|领.*?(\d+)\s*岁|maturity\s*(\d+)', text, re.IGNORECASE)
    if mat_match:
        params['maturity_age'] = int(mat_match.group(1) or mat_match.group(2) or mat_match.group(3))

    return params


def parse_query(text):
    """Full query parser: detect intent + extract params."""
    product = detect_product(text)
    params = extract_params(text)
    return product, params


def format_response(product, params, lang='zh'):
    """Generate a human-readable response confirming what was understood."""
    pname = {
        'term_life': '定期寿险', 'whole_life': '终身寿险', 'annuity': '生存年金',
        'endowment': '两全保险', 'deferred_annuity': '递延年金',
        'deferred_assurance': '递延寿险', 'pure_endowment': '纯生存保险',
    }

    lines = []
    if lang == 'zh':
        lines.append(f'📋 识别产品: {pname.get(product, product)}')
        if 'age' in params:
            lines.append(f'   年龄: {params["age"]} 岁')
        if 'sum_insured' in params:
            lines.append(f'   保额: ¥{params["sum_insured"]:,}')
        if 'term' in params:
            lines.append(f'   期限: {params["term"]} 年')
        if 'gender' in params:
            lines.append(f'   性别: {"男" if params["gender"]=="M" else "女"}')
        if 'rate' in params:
            lines.append(f'   利率: {params["rate"]*100:.1f}%')
        if 'freq' in params:
            fmap = {'annual': '年缴', 'semi': '半年缴', 'quarterly': '季缴', 'monthly': '月缴'}
            lines.append(f'   缴费: {fmap.get(params["freq"], params["freq"])}')
        if 'maturity_age' in params:
            lines.append(f'   领取年龄: {params["maturity_age"]} 岁')
    else:
        lines.append(f'📋 Product: {product}')
        for k, v in params.items():
            lines.append(f'   {k}: {v}')

    if not params:
        lines.append('   (未提取到参数，请提供更多信息)')
        lines.append('   示例: "30岁男买100万定期寿险20年"')

    return '\n'.join(lines)
