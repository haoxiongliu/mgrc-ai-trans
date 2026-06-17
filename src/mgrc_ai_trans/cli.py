#!/usr/bin/env python3
"""
Magireco AI Translator CLI

命令行工具，用于翻译Magireco游戏的JSON文件。
支持单个文件翻译和使用glob模式批量翻译。
"""

import argparse
import sys
from mgrc_ai_trans.config import DEFAULT_MODEL, load_env
from mgrc_ai_trans.main import trans_single_openai, trans_glob, build_train_ds


def main():
    load_env()
    parser = argparse.ArgumentParser(description='Magireco AI Translator CLI')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 单个文件翻译命令
    trans_single_parser = subparsers.add_parser('trans-single', help='翻译单个JSON文件')
    trans_single_parser.add_argument('src_fp', type=str, help='源JSON文件路径')
    trans_single_parser.add_argument('--api-key', type=str, default=None, help='OpenAI API密钥')
    trans_single_parser.add_argument('--base-url', type=str, default=None, help='API基础URL')
    trans_single_parser.add_argument('--model', type=str, default=DEFAULT_MODEL, help='使用的模型')
    trans_single_parser.add_argument('--tgt-root', type=str, default='output', help='输出目录根路径')
    trans_single_parser.add_argument('--log-root', type=str, default='log', help='日志目录根路径')
    trans_single_parser.add_argument('--prompt-root', type=str, default='prompts', help='提示模板目录')
    trans_single_parser.add_argument('--prompt-name', type=str, default='sakura_v8.4.md', help='提示模板文件名')
    trans_single_parser.add_argument('--special-fp', type=str, default='output/special_latest.json', help='特殊词汇文件路径')
    trans_single_parser.add_argument('--temperature', type=float, default=0.1, help='温度参数')
    trans_single_parser.add_argument('--top-p', type=float, default=0.95, help='top_p参数')
    trans_single_parser.add_argument('--max-tokens', type=int, default=8192, help='最大token数')
    trans_single_parser.add_argument('--add-line-number', action='store_true', default=True, help='添加行号')
    trans_single_parser.add_argument('--no-line-number', dest='add_line_number', action='store_false', help='不添加行号')
    trans_single_parser.add_argument('--prompt-in-user', action='store_true', default=False, help='在用户消息中包含提示')
    
    # 批量翻译命令
    trans_glob_parser = subparsers.add_parser('trans-glob', help='使用glob模式批量翻译JSON文件')
    trans_glob_parser.add_argument('--src-root', type=str, default='magireco-source', help='源文件目录')
    trans_glob_parser.add_argument('--fn-pattern', type=str, default='5167(10-2|10-9|20-6|20-7)_.*.json', help='文件名匹配模式')
    trans_glob_parser.add_argument('--num-worker', type=int, default=4, help='并行工作进程数')
    # 添加trans_single_openai的所有参数
    trans_glob_parser.add_argument('--api-key', type=str, default=None, help='OpenAI API密钥')
    trans_glob_parser.add_argument('--base-url', type=str, default=None, help='API基础URL')
    trans_glob_parser.add_argument('--model', type=str, default=DEFAULT_MODEL, help='使用的模型')
    trans_glob_parser.add_argument('--tgt-root', type=str, default='output', help='输出目录根路径')
    trans_glob_parser.add_argument('--log-root', type=str, default='log', help='日志目录根路径')
    trans_glob_parser.add_argument('--prompt-root', type=str, default='prompts', help='提示模板目录')
    trans_glob_parser.add_argument('--prompt-name', type=str, default='sakura_v8.4.md', help='提示模板文件名')
    trans_glob_parser.add_argument('--special-fp', type=str, default='output/special_latest.json', help='特殊词汇文件路径')
    trans_glob_parser.add_argument('--temperature', type=float, default=0.1, help='温度参数')
    trans_glob_parser.add_argument('--top-p', type=float, default=0.95, help='top_p参数')
    trans_glob_parser.add_argument('--max-tokens', type=int, default=8192, help='最大token数')
    trans_glob_parser.add_argument('--add-line-number', action='store_true', default=True, help='添加行号')
    trans_glob_parser.add_argument('--no-line-number', dest='add_line_number', action='store_false', help='不添加行号')
    trans_glob_parser.add_argument('--prompt-in-user', action='store_true', default=False, help='在用户消息中包含提示')
    
    # 构建训练数据集命令
    build_ds_parser = subparsers.add_parser('build-train-ds', help='构建训练数据集')
    build_ds_parser.add_argument('--src-root', type=str, default='magireco-source', help='源文件目录')
    build_ds_parser.add_argument('--trans-root', type=str, default='magireco-translate-data', help='翻译文件目录')
    build_ds_parser.add_argument('--output-fp', type=str, default='datasets/debug.jsonl', help='输出JSONL文件路径')
    build_ds_parser.add_argument('--fn-pattern', type=str, default='5167(10-2|10-9|20-6|20-7)_.*.json', help='文件名匹配模式')
    build_ds_parser.add_argument('--special-fp', type=str, default='output/special_latest.json', help='特殊词汇文件路径')
    build_ds_parser.add_argument('--sys-prompt-fp', type=str, default='prompts/sakura_ft_v0.md', help='系统提示模板文件路径')
    build_ds_parser.add_argument('--add-line-number', action='store_true', default=False, help='添加行号')
    build_ds_parser.add_argument('--no-line-number', dest='add_line_number', action='store_false', help='不添加行号')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'trans-single':
            result = trans_single_openai(
                src_fp=args.src_fp,
                api_key=args.api_key,
                base_url=args.base_url,
                model=args.model,
                tgt_root=args.tgt_root,
                log_root=args.log_root,
                prompt_root=args.prompt_root,
                prompt_name=args.prompt_name,
                special_fp=args.special_fp,
                temperature=args.temperature,
                top_p=args.top_p,
                max_tokens=args.max_tokens,
                add_line_number=args.add_line_number,
                prompt_in_user=args.prompt_in_user
            )
            if result:
                print(f"翻译成功: {result}")
        elif args.command == 'trans-glob':
            # 移除num_worker参数，因为它是trans_glob的直接参数
            trans_glob_kwargs = vars(args).copy()
            num_worker = trans_glob_kwargs.pop('num_worker')
            trans_glob_kwargs.pop('command')
            
            result = trans_glob(
                num_worker=num_worker,
                **trans_glob_kwargs
            )
            print(f"批量翻译完成")
        elif args.command == 'build-train-ds':
            build_train_ds(
                src_root=args.src_root,
                trans_root=args.trans_root,
                output_fp=args.output_fp,
                fn_pattern=args.fn_pattern,
                special_fp=args.special_fp,
                sys_prompt_fp=args.sys_prompt_fp,
                add_line_number=args.add_line_number
            )
            print(f"训练数据集构建完成")
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
