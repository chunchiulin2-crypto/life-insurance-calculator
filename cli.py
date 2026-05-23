#!/usr/bin/env python3
"""Term Life Insurance Premium Calculator — CLI entry point."""

import argparse
import os
import sys
from mortality import load_table, build_life_table
from premium import single_premium, annual_premium
from reserve import reserve_table

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'clt_2010_2013.csv')
LIMIT_AGE = 105


def parse_args():
    p = argparse.ArgumentParser(
        description='定期寿险保费计算器 · Term Life Premium Calculator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python cli.py --age 30 --sum 1000000 --term 20
  python cli.py --age 40 --sum 500000 --term 10 --rate 0.03 --gender F
        ''',
    )
    p.add_argument('--age', type=int, required=True, help='投保年龄')
    p.add_argument('--sum', type=int, required=True, help='保险金额 (元)')
    p.add_argument('--term', type=int, required=True, help='保险期限 (年)')
    p.add_argument('--rate', type=float, default=0.035, help='预定利率 (默认: 0.035)')
    p.add_argument('--gender', choices=['M', 'F'], default='M', help='性别 M/F (默认: M)')
    return p.parse_args()


def validate(args):
    errors = []
    if args.age < 0:
        errors.append('年龄不能为负数')
    if args.age >= LIMIT_AGE:
        errors.append(f'年龄不能超过 {LIMIT_AGE} 岁')
    if args.age + args.term > LIMIT_AGE:
        errors.append(f'年龄 + 保险期限 ({args.age}+{args.term}={args.age+args.term}) 超过极限年龄 {LIMIT_AGE}')
    if args.sum <= 0:
        errors.append('保险金额必须大于 0')
    if args.term <= 0:
        errors.append('保险期限必须大于 0')
    if args.rate < 0:
        errors.append('利率不能为负数')
    if args.rate > 0.5:
        errors.append(f'利率 {args.rate} 异常高，请确认')
    return errors


def fmt_yuan(val):
    """Format as Chinese yuan with comma separators."""
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

    print()
    print('╔══════════════════════════════════════════════╗')
    print('║     定期寿险保费计算器 · Term Life         ║')
    print('╚══════════════════════════════════════════════╝')
    print()
    print(f'  被保险人年龄: {args.age} 岁 ({gender_label})')
    print(f'  保险金额:      {fmt_yuan(args.sum)}')
    print(f'  保险期限:      {args.term} 年')
    print(f'  预定利率:      {args.rate:.2%}')
    print(f'  生命表:        CLT 2010-2013 (非养老类)')
    print()

    df = load_table(DATA_PATH)
    lt = build_life_table(df, args.gender)

    sp = single_premium(lt, args.age, args.sum, args.term, args.rate)
    ap = annual_premium(lt, args.age, args.sum, args.term, args.rate)

    print('  ────────────────────────────────────────────')
    print(f'  趸缴纯保费:     {fmt_yuan(sp)}')
    print(f'  年缴纯保费:     {fmt_yuan(ap)}')
    print('  ────────────────────────────────────────────')
    print()

    reserves = reserve_table(lt, args.age, args.sum, args.term, args.rate)

    print('  📊 各年末责任准备金:')
    print(f'  {"Year":<6} {"Reserve":>12}')
    print(f'  {"─────":<6} {"───────────":>12}')
    for year, reserve in reserves:
        print(f'  {year:<6} {fmt_yuan(reserve):>12}')
    print()
    print('  💡 趸缴 = 单次付清 | 年缴 = 每年初支付')
    print(f'  💡 利率 i = {args.rate}')
    print()


if __name__ == '__main__':
    main()
