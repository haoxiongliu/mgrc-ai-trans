from mgrc_ai_trans.main import trans_single_openai
import inspect

# 获取函数的默认参数
print("检查trans_single_openai函数的默认参数:")
argspec = inspect.signature(trans_single_openai)
print(f"prompt_root默认值: {argspec.parameters['prompt_root'].default}")
print(f"prompt_name默认值: {argspec.parameters['prompt_name'].default}")

# 测试构建提示文件路径
print("\n测试提示文件路径构建:")
try:
    # 模拟trans_single_openai函数中的路径构建逻辑
    from importlib.resources import files
    prompt_name = "sakura_v8.4.md"
    prompt_path = files('mgrc_ai_trans.prompts').joinpath(prompt_name)
    print(f"构建的提示文件路径: {prompt_path}")
    print(f"文件是否存在: {prompt_path.exists()}")
    
    if prompt_path.exists():
        with open(prompt_path, encoding='utf-8') as f:
            content = f.read()
            print(f"提示文件内容长度: {len(content)} 字符")
            print(f"提示文件前几行: {content.splitlines()[:3]}...")
    else:
        print("提示文件不存在!")
        
    print("\n测试成功完成!")
except Exception as e:
    print(f"测试失败: {e}")
