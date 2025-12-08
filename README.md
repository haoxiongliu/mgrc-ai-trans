# mgrc-ai-trans

一个用于Magireco游戏数据翻译的AI翻译工具。

## 安装

本项目使用`uv`进行依赖管理。请先安装`uv`：

```bash
pip install uv
```

然后克隆项目并安装依赖：

```bash
# 克隆项目
cd mgrc-ai-trans

# 创建虚拟环境
uv venv

# 安装依赖
uv pip install -e .
```

## 使用

### 基本命令

```bash
# 运行主程序
uv run python main.py

# 查看帮助
uv run python main.py --help
```

### 主要功能

1. **批量翻译**：使用`trans_glob`函数批量翻译源文件
2. **单文件翻译**：使用`trans_single_openai`函数翻译单个文件
3. **构建训练数据集**：使用`build_train_ds`函数构建训练数据集

## 项目结构

- `magireco-source/`：源文件目录
- `output/`：翻译输出目录
- `log/`：日志目录
- `prompts/`：提示词模板目录
- `utils/`：工具函数目录
- `main.py`：主程序入口
- `pyproject.toml`：项目配置文件

