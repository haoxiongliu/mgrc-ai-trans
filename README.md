# mgrc-ai-trans

一个用于Magireco游戏数据翻译的AI翻译工具。

## 项目特色

- **文件内语境一次性支持**：以单个剧情 JSON 文件为单位抽取全部可翻译文本，一次性提交给模型处理，让模型能参考同一文件内的上下文、角色对话和前后文关系，而不是逐句孤立翻译。
- **专有名词表 Prompt 注入**：支持通过 `special_latest.json` 等专有名词表自动筛选当前文件中出现的术语，并注入到提示词中，帮助统一角色名、地名、组织名和其他游戏内固定译名。
- **结构保真输出**：翻译时保留原 JSON 结构，只替换文本字段；配合行号和 `@` 分段约束，降低对白错位和排版符号丢失的风险。

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
4. **专有名词约束**：通过`special_fp`传入术语表，将当前文件命中的专有名词加入翻译提示词

## 项目结构

- `magireco-source/`：源文件目录
- `output/`：翻译输出目录
- `log/`：日志目录
- `prompts/`：提示词模板目录
- `utils/`：工具函数目录
- `main.py`：主程序入口
- `pyproject.toml`：项目配置文件

