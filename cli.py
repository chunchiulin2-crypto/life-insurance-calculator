#!/usr/bin/env python3
"""寿险精算计算器 · CLI entry point"""

import argparse
import os
import sys
from mortality import load_table, build_life_table
from premium import (single_premium, annual_premium,
                     whole_life_single_premium, whole_life_annual_premium,
                     endowment_single_premium, endowment_annual_premium,
                     annuity_price,
                     gross_annual_premium, periodic_premium)
from reserve import reserve_table, whole_life_reserve_table, endowment_reserve_table

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'clt_2010_2013.csv')
AM92_PATH = os.path.join(os.path.dirname(__file__), 'data', 'am92.csv')
LIMIT_AGE = 120

PRODUCTS = {
    'term': '定期寿险',
    'whole_life': '终身寿险',
    'annuity': '生存年金',
    'endowment': '两全保险',
}

RISK_CLASSES = {
    'preferred': {'label': '优选体 (Preferred)', 'factor': 0.7},
    'standard': {'label': '标准体 (Standard)', 'factor': 1.0},
    'substandard': {'label': '次标准体 (Substandard)', 'factor': 2.0},
}

TABLES = {
    'clt': {'label': 'CLT 2010-2013', 'path': DATA_PATH, 'gender_based': True},
    'am92ult': {'label': 'AM92 Ultimate', 'path': AM92_PATH, 'gender_based': False},
    'am92sel': {'label': 'AM92 Select', 'path': AM92_PATH, 'gender_based': False},
    'am92sel_plusone': {'label': 'AM92 Select+1', 'path': AM92_PATH, 'gender_based': False},
}


def parse_args():
    p = argparse.ArgumentParser(
        description='寿险精算计算器 · Life Insurance Actuarial Calculator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python cli.py --age 30 --sum 1000000 --term 20
  python cli.py --age 30 --sum 1000000 --term 20 --product whole_life
  python cli.py --age 30 --sum 50000 --term 20 --product annuity
  python cli.py --age 30 --sum 1000000 --term 20 --product endowment
        ''',
    )
    p.add_argument('--age', type=int, required=True, help='投保年龄')
    p.add_argument('--sum', type=int, required=True, help='保险金额 (元) / 年领金额 (年金)')
    p.add_argument('--term', type=int, default=None, help='保险期限 (年, 终身寿险无需指定)')
    p.add_argument('--rate', type=float, default=0.035, help='预定利率 (默认: 0.035)')
    p.add_argument('--gender', choices=['M', 'F'], default='M', help='性别 M/F (默认: M)')
    p.add_argument('--product', choices=list(PRODUCTS.keys()), default='term',
                   help=f'产品类型: {", ".join(f"{k}={v}" for k, v in PRODUCTS.items())} (默认: term)')
    p.add_argument('--risk', choices=list(RISK_CLASSES.keys()), default='standard',
                   help='核保等级: preferred(优选)/standard(标准)/substandard(次标准) (默认: standard)')
    p.add_argument('--table', choices=list(TABLES.keys()), default='clt',
                   help=f'生命表: {", ".join(f"{k}={v["label"]}" for k, v in TABLES.items())} (默认: clt)')
    p.add_argument('--claim-accel', action='store_true', default=False,
                   help='死亡立即付款 (默认: 年末付款, UDD假设下立即付款 = (1+i)^0.5 × 年末付款)')
    p.add_argument('--alpha', type=float, default=0.0, help='获取费 (× 保额, 默认 0)')
    p.add_argument('--beta', type=float, default=0.0, help='维持费 (× 保费, 默认 0)')
    p.add_argument('--gamma', type=float, default=0.0, help='收费费 (× 保额, 默认 0)')
    p.add_argument('--freq', type=int, choices=[1, 2, 4, 12], default=1,
                   help='年缴费次数 1/2/4/12 (默认: 1=年缴)')
    return p.parse_args()


def validate(args):
    errors = []
    if args.product != 'whole_life' and args.term is None:
        args.term = 20  # default for products that need term
    if args.age < 0:
        errors.append('年龄不能为负数')
    if args.age >= LIMIT_AGE:
        errors.append(f'年龄不能超过 {LIMIT_AGE} 岁')
    if args.product != 'whole_life' and args.age + args.term > LIMIT_AGE:
        errors.append(f'年龄 + 保险期限 超过极限年龄 {LIMIT_AGE}')
    if args.sum <= 0:
        errors.append('金额必须大于 0')
    if args.product != 'whole_life' and args.term <= 0:
        errors.append('保险期限必须大于 0')
    if args.rate < 0:
        errors.append('利率不能为负数')
    if args.rate > 0.5:
        errors.append(f'利率 {args.rate} 异常高，请确认')
    return errors


def fmt_yuan(val):
    return f'¥{val:,.2f}'


def main():
    args = parse_args()
    errs = validate(args)
    if errs:
        print('错误:')
        for e in errs:
            print(f'  ✗ {e}')
        sys.exit(1)

    gender_label = '男性' if args.gender == 'M' else '女性'
    product_name = PRODUCTS[args.product]

    print()
    print('╔══════════════════════════════════════════════╗')
    print(f'║   {product_name} · {PRODUCTS[args.product]}   ║')
    print('╚══════════════════════════════════════════════╝')
    print()
    print(f'  产品类型:      {product_name}')
    print(f'  被保险人年龄: {args.age} 岁 ({gender_label})')
    print(f'  保险金额:      {fmt_yuan(args.sum)}')
    if args.product != 'whole_life':
        print(f'  保险期限:      {args.term} 年')
    print(f'  预定利率:      {args.rate:.2%}')
    risk = RISK_CLASSES[args.risk]
    payment_mode = '死亡立即付款 (UDD)' if args.claim_accel else '死亡年末付款'
    print(f'  核保等级:      {risk["label"]} (qx × {risk["factor"]})')
    freq_names = {1: '年缴', 2: '半年缴', 4: '季缴', 12: '月缴'}
    print(f'  赔付时点:      {payment_mode}')
    if args.alpha > 0 or args.beta > 0 or args.gamma > 0:
        print(f'  费用参数:      α={args.alpha:.3f} β={args.beta:.3f} γ={args.gamma:.4f}')
    print(f'  缴费频率:      {freq_names[args.freq]} (m={args.freq})')
    table_info = TABLES[args.table]
    print(f'  生命表:        {table_info["label"]}')
    print()

    df = load_table(table_info['path'])
    col = args.gender if table_info['gender_based'] else args.table
    lt = build_life_table(df, col, risk_factor=risk['factor'])
    ca = args.claim_accel

    # Dispatch by product — use gross premium functions
    if args.product == 'whole_life':
        gap = gross_annual_premium(lt, args.age, args.sum, 105 - args.age, args.rate,
                                   alpha=args.alpha, beta=args.beta, gamma=args.gamma, claim_accel=ca)
        ap = periodic_premium(gap, args.freq)
        net = whole_life_annual_premium(lt, args.age, args.sum, args.rate, claim_accel=ca)
        reserves = whole_life_reserve_table(lt, args.age, args.sum, args.rate)
    elif args.product == 'annuity':
        gap = annuity_price(lt, args.age, args.sum, args.term, args.rate)
        ap = None
        net = None
        reserves = []
    elif args.product == 'endowment':
        gap = gross_annual_premium(lt, args.age, args.sum, args.term, args.rate,
                                   alpha=args.alpha, beta=args.beta, gamma=args.gamma, claim_accel=ca)
        ap = periodic_premium(gap, args.freq)
        net = endowment_annual_premium(lt, args.age, args.sum, args.term, args.rate, claim_accel=ca)
        reserves = endowment_reserve_table(lt, args.age, args.sum, args.term, args.rate)
    else:  # term
        gap = gross_annual_premium(lt, args.age, args.sum, args.term, args.rate,
                                   alpha=args.alpha, beta=args.beta, gamma=args.gamma, claim_accel=ca)
        ap = periodic_premium(gap, args.freq)
        net = annual_premium(lt, args.age, args.sum, args.term, args.rate, claim_accel=ca)
        reserves = reserve_table(lt, args.age, args.sum, args.term, args.rate)

    print('  ────────────────────────────────────────────')
    if args.product == 'annuity':
        print(f'  趸缴购买价格:   {fmt_yuan(gap)}')
    else:
        print(f'  每期保费 ({freq_names[args.freq]}): {fmt_yuan(ap)}')
        print(f'  年毛保费:       {fmt_yuan(gap)}')
        if net:
            print(f'  年纯保费 (净):   {fmt_yuan(net)}')
            print(f'  费用附加:        {fmt_yuan(gap - net)}')
    print('  ────────────────────────────────────────────')
    print()

    if args.product != 'annuity' and reserves:
        print('  📊 各年末责任准备金:')
        print(f'  {"Year":<6} {"Reserve":>12}')
        print(f'  {"─────":<6} {"───────────":>12}')
        for year, reserve in reserves:
            print(f'  {year:<6} {fmt_yuan(reserve):>12}')
        print()
    elif args.product == 'annuity':
        print('  💡 生存年金无责任准备金（保单签发后即开始支付）')
        print()

    if args.product == 'annuity':
        print('  💡 趸缴购买价格 = 年领金额 × äx:n⌉')
    elif args.product == 'endowment':
        print('  💡 两全保险 = 定期寿险 + 纯生存保险')
        print('  💡 到期生存返还全部保额')
    else:
        print('  💡 趸缴 = 单次付清 | 年缴 = 每年初支付')
    print(f'  💡 利率 i = {args.rate}')
    print()


if __name__ == '__main__':
    main()
