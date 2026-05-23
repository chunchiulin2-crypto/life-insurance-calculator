#!/usr/bin/env python3
"""寿险精算计算器 · CLI entry point"""

import argparse
import os
import sys
from mortality import load_table, build_life_table
from premium import (single_premium, annual_premium,
                     whole_life_single_premium, whole_life_annual_premium,
                     endowment_single_premium, endowment_annual_premium,
                     annuity_price)
from reserve import reserve_table, whole_life_reserve_table, endowment_reserve_table

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'clt_2010_2013.csv')
LIMIT_AGE = 105

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
    print(f'  核保等级:      {risk["label"]} (qx × {risk["factor"]})')
    print(f'  生命表:        CLT 2010-2013 (非养老类)')
    print()

    df = load_table(DATA_PATH)
    lt = build_life_table(df, args.gender, risk_factor=risk['factor'])

    # Dispatch by product
    if args.product == 'whole_life':
        sp = whole_life_single_premium(lt, args.age, args.sum, args.rate)
        ap = whole_life_annual_premium(lt, args.age, args.sum, args.rate)
        reserves = whole_life_reserve_table(lt, args.age, args.sum, args.rate)
    elif args.product == 'annuity':
        sp = annuity_price(lt, args.age, args.sum, args.term, args.rate)
        ap = None
        reserves = []
    elif args.product == 'endowment':
        sp = endowment_single_premium(lt, args.age, args.sum, args.term, args.rate)
        ap = endowment_annual_premium(lt, args.age, args.sum, args.term, args.rate)
        reserves = endowment_reserve_table(lt, args.age, args.sum, args.term, args.rate)
    else:  # term
        sp = single_premium(lt, args.age, args.sum, args.term, args.rate)
        ap = annual_premium(lt, args.age, args.sum, args.term, args.rate)
        reserves = reserve_table(lt, args.age, args.sum, args.term, args.rate)

    print('  ────────────────────────────────────────────')
    if args.product == 'annuity':
        print(f'  趸缴购买价格:   {fmt_yuan(sp)}')
    else:
        print(f'  趸缴纯保费:     {fmt_yuan(sp)}')
        print(f'  年缴纯保费:     {fmt_yuan(ap)}')
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
