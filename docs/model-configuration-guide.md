# 统一模型配置指南

## 🎯 概述

为了解决项目中多处硬编码模型名称的问题，我们引入了统一的模型配置管理系统。现在所有LLM模型配置都通过 `src/arxiv_follow/config/models.py` 进行统一管理。

## ✅ 优势

- **统一管理**: 所有模型配置在一个地方
- **环境变量支持**: 可以通过环境变量动态切换模型
- **简化维护**: 修改模型只需改一个地方
- **支持多模型**: 预定义多个常用模型
- **配置一致性**: 确保所有组件使用相同的配置

## 🔧 配置方式

### 1. 默认配置
系统默认使用 `google/gemini-2.0-flash-001` 模型。

### 2. 环境变量配置
```bash
# 使用完整模型名称
export ARXIV_FOLLOW_DEFAULT_MODEL="google/gemini-2.0-flash-001"

# 或使用简短别名
export ARXIV_FOLLOW_DEFAULT_MODEL="gemini-flash"
export ARXIV_FOLLOW_DEFAULT_MODEL="claude-haiku"
export ARXIV_FOLLOW_DEFAULT_MODEL="gpt-4o-mini"
```

### 3. 支持的模型别名
```python
SUPPORTED_MODELS = {
    "gemini-flash": "google/gemini-2.0-flash-001",
    "gemini-flash-lite": "google/gemini-2.0-flash-lite-001", 
    "gemini-flash-exp": "google/gemini-2.0-flash-exp",
    "claude-haiku": "anthropic/claude-3-haiku",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "llama-3.1": "meta-llama/llama-3.1-8b-instruct",
}
```

## 📝 使用方法

### 在代码中获取模型配置
```python
from arxiv_follow.config.models import get_default_model, get_model_config

# 获取默认模型名称
model_name = get_default_model()

# 获取完整的模型配置
config = get_model_config()
# 返回: {"model": "google/gemini-2.0-flash-001", "temperature": 0.3, ...}

# 获取特定模型的配置
config = get_model_config("claude-haiku")
```

### 在服务中使用
```python
from arxiv_follow.services.translation import TranslationService

# 使用默认模型
service = TranslationService()

# 使用指定模型
service = TranslationService(model="claude-haiku")
```

## 🔄 切换模型

### 临时切换（当前会话）
```bash
export ARXIV_FOLLOW_DEFAULT_MODEL="claude-haiku"
uv run python -m arxiv_follow.cli.daily
```

### 永久切换（修改配置）
编辑 `src/arxiv_follow/config/models.py`:
```python
# 修改默认模型
DEFAULT_LLM_MODEL = "anthropic/claude-3-haiku"
```

### CI/CD 环境配置
在 GitHub Actions 中设置环境变量:
```yaml
env:
  ARXIV_FOLLOW_DEFAULT_MODEL: "google/gemini-2.0-flash-001"
```

## 📋 配置检查

### 验证当前配置
```python
from arxiv_follow.config.models import get_default_model, get_model_config

print(f"当前模型: {get_default_model()}")
print(f"配置详情: {get_model_config()}")
```

### 验证环境变量
```bash
echo "当前默认模型: $ARXIV_FOLLOW_DEFAULT_MODEL"
```

## 🛠️ 故障排除

### 问题1: 模型名称不识别
```
KeyError: 'unknown-model'
```
**解决方案**: 检查模型名称是否在 `SUPPORTED_MODELS` 中，或使用完整的模型名称。

### 问题2: 环境变量不生效
**检查事项**:
- 环境变量名称是否正确: `ARXIV_FOLLOW_DEFAULT_MODEL`
- 变量值是否有效（在支持列表中或完整名称）
- 是否重新启动了应用

### 问题3: 配置不一致
如果发现某些组件仍在使用旧的硬编码模型，请检查:
1. 是否正确导入了 `get_default_model()`
2. 是否更新了所有相关文件
3. 运行测试确保配置生效

## 📚 API 参考

### `get_default_model() -> str`
获取默认模型名称，支持环境变量覆盖。

### `get_model_config(model_name: str = None) -> Dict[str, Any]`
获取模型配置，包含模型名称和参数。

### `get_translation_config() -> Dict[str, Any]`
获取翻译服务的完整配置。

### `get_analysis_config() -> Dict[str, Any]`
获取论文分析的完整配置。

## 🔄 迁移指南

### 从硬编码迁移
如果您的代码中还有硬编码的模型名称：

**之前**:
```python
self.model = "google/gemini-2.0-flash-lite-001"
```

**之后**:
```python
from ..config.models import get_default_model
self.model = get_default_model()
```

### 配置统一化
**之前** (在多个文件中重复):
```python
TRANSLATION_CONFIG = {
    "model": "google/gemini-2.0-flash-lite-001",
    "temperature": 0.3,
    # ...
}
```

**之后** (统一配置):
```python
from .models import get_translation_config
TRANSLATION_CONFIG = get_translation_config()
```

## ✅ 最佳实践

1. **始终使用配置函数**: 不要硬编码模型名称
2. **环境变量优先**: 支持运行时配置覆盖
3. **文档同步**: 更新模型时同步更新相关文档
4. **测试验证**: 配置变更后运行测试确保功能正常
5. **向后兼容**: 新增模型时保持现有配置的兼容性

---

通过统一的模型配置管理，我们解决了硬编码问题，提高了系统的可维护性和灵活性。 