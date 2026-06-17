from importlib.resources import files

# 测试访问包内的提示文件
prompt_path = files('mgrc_ai_trans.prompts').joinpath('sakura_v8.4.md')
print(f'Prompt file path: {prompt_path}')
print(f'File exists: {prompt_path.exists()}')

# 尝试读取文件内容
if prompt_path.exists():
    with open(prompt_path, encoding='utf-8') as f:
        content = f.read()
        print(f'File content length: {len(content)} characters')
        print(f'First 50 characters: {content[:50]}...')
else:
    print('File does not exist!')
