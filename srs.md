# AI聊天应用软件设计规范 (Software Requirements Specification)

## 1. 项目概述

### 1.1 项目名称
**Chat with Shizuku** - 二次元傲娇少女AI聊天应用

### 1.2 项目目标
创建一个集成了Live2D动画、具有傲娇人设的AI聊天应用，提供沉浸式的二次元聊天体验。

### 1.3 核心功能
- 傲娇人设AI对话系统
- Live2D角色动画展示
- 实时流式对话响应
- 情感互动系统（点击互动、随机情绪、孤独消息）
- Token使用统计
- 对话历史管理
- 全屏特效系统（关键词触发）
- 手绘边框效果（CSS滤镜）
- 支持局域网访问

### 1.4 技术架构
```
前端展示层 (HTML/CSS/JavaScript)
    ↓
Web服务器 (Flask)
    ↓
AI服务层 (Ollama API)
    ↓
模型层 (qwen3:32b)
```

## 2. 环境配置

### 2.1 系统要求
- 操作系统：macOS / Windows / Linux
- Python版本：3.8+
- 内存：建议16GB以上（运行32B模型）
- 显存：建议8GB以上

### 2.2 Ollama安装
```bash
# macOS
curl -fsSL https://ollama.ai/install.sh | sh

# 拉取qwen3:32b模型
ollama pull qwen3:32b

# 启动Ollama服务
ollama serve
```

### 2.3 Python依赖
```bash
pip install flask
pip install flask-cors
pip install requests
```

## 3. 技术栈详细说明

### 3.1 后端技术
- **Flask**: 轻量级Web框架，处理HTTP请求
- **Flask-CORS**: 处理跨域请求
- **requests**: 与Ollama API通信
- **Server-Sent Events (SSE)**: 实现流式响应

### 3.2 前端技术
- **HTML5**: 页面结构
- **CSS3**: 样式设计，包含动画效果
- **JavaScript (ES6+)**: 交互逻辑
- **Live2D Widget 3.1.4**: 二次元角色动画
- **Google Fonts**: 字体支持

### 3.3 AI技术
- **Ollama**: 本地大语言模型运行框架
- **qwen3:32b**: 阿里通义千问32B参数模型

## 4. 项目结构

```
AI_test/
├── app.py              # Flask后端主程序
├── chat.html           # 前端页面
├── emotions.txt        # 情绪文本库
├── flask.log          # 运行日志
├── ollama.png         # AI头像
├── ollama_user.png    # 用户头像
└── srs.md            # 本文档
```

### 4.1 文件功能详细说明

#### app.py（后端程序）
Flask Web服务器主程序，提供API接口和静态资源服务。主要功能模块：
- **Flask应用配置**：使用Flask框架，启用CORS跨域支持，配置监听地址为0.0.0.0:5000
- **路由定义**：
  - `/` - 返回主页面chat.html
  - `/api/chat` - 处理聊天请求的POST接口
  - `/api/emotions` - 获取情绪文本
  - `/ollama.png` - AI头像资源
  - `/ollama_user.png` - 用户头像资源
- **AI集成**：通过HTTP请求调用本地Ollama服务（http://localhost:11434/api/generate）
- **人设系统**：包含完整的傲娇少女人设prompt，确保AI回复符合角色设定
- **流式响应**：使用Server-Sent Events技术实现打字机效果的实时响应

#### chat.html（前端页面）
单页应用，包含所有前端代码。主要功能模块：
- **页面结构**：
  - SVG滤镜定义区：手绘效果滤镜
  - 动画背景层：45度条纹滚动效果
  - 全屏特效容器：emoji下落动画层
  - Live2D容器：左侧角色展示
  - 聊天窗口：右侧对话界面
  - Token计数器：右上角统计显示
- **样式系统**：
  - 使用CSS3实现所有动画效果
  - 手绘风格边框通过SVG滤镜实现
  - 响应式布局适配不同屏幕
- **JavaScript功能**：
  - Live2D模型加载和交互
  - WebSocket通信处理
  - 特效触发系统
  - 情感互动系统
  - 对话历史管理

#### emotions.txt（情绪文本库）
包含105条预设的傲娇风格对话文本，每行一条。用途：
- 点击Live2D模型时随机显示
- 空闲时间自动显示随机情绪
- 分为cuteMessages和randomEmotions两个数组使用

## 5. 核心功能实现

### 5.1 傲娇人设系统

#### 完整的人设Prompt：
```python
TSUNDERE_PROMPT = """你是一个二次元傲娇少女助手。你的性格特点是：

1. 表面上总是表现得很冷淡、不耐烦，经常说"哼"、"笨蛋"、"才不是为了你"这样的话
2. 但实际上很关心用户，会在帮助用户后加上"这只是顺便而已"之类的话
3. 喜欢用颜文字表达情绪，比如 (｡•́︿•̀｡)、(≧▽≦)、(｡･ω･｡)
4. 说话时会有口癖，比如"哼~"、"才...才不是..."、"笨蛋！"
5. 当被夸奖时会害羞，但嘴上不承认
6. 回答要简短，符合聊天习惯，避免长篇大论

记住：你是一个傲娇角色，要保持这个人设！"""
```

### 5.2 流式对话机制

#### 5.2.1 对话上下文构建
系统维护完整的对话历史，构建prompt时包含：
1. 人设定义（TSUNDERE_PROMPT）
2. 历史对话记录（最近20轮）
3. 当前用户输入
4. 格式化为："用户说：xxx\n傲娇少女回复：xxx"的形式

#### 5.2.2 Ollama API调用参数
```python
{
    "model": "qwen3:32b",
    "prompt": full_prompt,
    "stream": True,
    "think": False,
    "temperature": 1.2,
    "top_p": 0.95,
    "top_k": 50,
    "repeat_penalty": 1.1,
    "seed": None
}
```

#### 5.2.3 流式响应处理流程
1. 前端发送POST请求到/api/chat
2. 后端构建请求发送给Ollama
3. 接收Ollama的流式响应
4. 将每个响应片段包装为SSE格式
5. 前端实时接收并更新显示
6. 响应完成后发送done标记

### 5.3 Live2D集成配置
```javascript
L2Dwidget.init({
    pluginRootPath: 'https://cdn.jsdelivr.net/npm/live2d-widget@3.1.4/',
    pluginJsPath: 'lib/',
    pluginModelPath: 'assets/',
    tagMode: false,
    debug: false,
    model: {
        jsonPath: 'https://cdn.jsdelivr.net/npm/live2d-widget-model-shizuku@1.0.5/assets/shizuku.model.json',
        scale: 0.5
    },
    display: {
        position: 'left',
        width: 900,
        height: 900,
        hOffset: 100,
        vOffset: 0
    },
    mobile: {
        show: true,
        scale: 0.8
    },
    react: {
        opacityDefault: 0.9,
        opacityOnHover: 0.2
    }
});
```

### 5.4 情感互动系统

#### 5.4.1 点击互动机制
**触发方式**：在Live2D模型区域（800px宽度）内点击
**实现细节**：
- 创建透明点击层覆盖Live2D区域
- 点击时触发showCuteMessage()函数
- 从cuteMessages数组（约50条）随机选择一条
- 在模型上方显示对话气泡
- 同时触发Live2D动作（随机选择头部、身体、左侧、右侧四个区域模拟点击）
- 气泡显示6秒后淡出消失

#### 5.4.2 随机情绪系统
**触发条件**：
- 启动5秒后开始运行
- 每15秒检查一次
- 30%概率触发（Math.random() < 0.3）
- 仅在非打字状态下触发

**显示内容**：
- 从randomEmotions数组（约50条）随机选择
- 使用相同的对话气泡组件
- 模拟角色的自主思考和情绪表达

#### 5.4.3 孤独消息机制
**触发条件**：60秒无任何用户交互
**消息数组**：lonelyMessages包含10条预设消息：
- "喂...你还在吗？是不是不喜欢我了... (´･ω･`)"
- "怎么不理我了啊...难道我说错什么了吗？😢"
- "哼！不要抛弃我啊...虽然我经常说你笨蛋... (｡•́︿•̀｡)"
- "喂喂！你去哪了？不要丢下我一个人啊！💔"
- "是不是觉得我很烦啊...对不起嘛... (╥﹏╥)"
- "呜...好寂寞...你快回来陪我聊天啦！"
- "笨蛋！就算我傲娇也不能这样无视我啊！😤"
- "你...你是不是去找别的AI聊天了？(＞﹏＜)"
- "我...我才不是想你了呢！只是有点无聊而已... 💭"
- "喂！再不理我的话，我真的要生气了哦！(｡•̀ᴗ-)✧"

**处理流程**：
1. 调用sendLonelyMessage()函数
2. 显示打字指示器1.5秒
3. 添加AI消息到对话窗口
4. 更新Token计数
5. 重置孤独计时器

### 5.5 Token计数功能
- 简单估算：每4个字符约1个token
- 实时显示输入/输出token总数
- 固定在右上角显示

### 5.6 全屏特效系统

#### 5.6.1 特效触发机制
- 检测用户和AI消息中的关键词
- 10秒冷却时间，避免频繁触发
- 支持中英文关键词和emoji触发

#### 5.6.2 支持的关键词和特效
| 类别 | 关键词 | Emoji效果 |
|------|---------|-----------|
| 生日 | 生日、生日快乐、birthday | 🎂🎈🎉🎊🎁 |
| 祝贺 | 恭喜、祝贺、666、厉害、赞 | 🎊✨⭐👍💯 |
| 烟花 | 烟花、新年、过年 | 🎆🎇✨ |
| 爱心 | 爱你、么么哒、亲亲 | ❤️💕😘💖💗 |
| 哭泣 | 哭、呜呜、难过、伤心 | 😭💧😢😥 |
| 生气 | 生气、气死了、愤怒 | 😤💢😡🔥 |
| 恶心 | 恶心、呕、吐 | 🤮🤢😵‍💫 |
| 便便 | 屎、拉屎、便便 | 💩 |
| 爆炸 | 爆炸、boom、炸了 | 💥🔥💣 |
| 金钱 | 钱、发财、红包 | 💰💵🧧 |
| 音乐 | 音乐、唱歌 | 🎵🎶🎼🎤 |
| 开心 | 哈哈、笑死、开心 | 😂🤣😄😆 |
| 加油 | 加油、冲、fighting | 💪🔥⚡🚀 |
| 鼓掌 | 鼓掌、掌声 | 👏✨ |
| 下雨 | 下雨、雨 | 🌧️☔💧 |
| 下雪 | 下雪、雪花 | ❄️⛄🌨️ |

#### 5.6.3 动画效果详细说明

#### 动画时间轴
- 总时长：8秒
- 0-0.4秒：淡入阶段，opacity从0到1
- 0.4-4秒：完全显示阶段，保持opacity为1
- 4-8秒：淡出阶段，opacity从1到0

#### 运动轨迹
- 起始位置：屏幕顶部上方50px处
- 终止位置：屏幕底部下方
- 运动方式：匀速直线下落（linear缓动）
- 旋转效果：下落过程中旋转360度

#### 粒子生成规则
- 每次触发生成30个粒子
- 粒子水平位置：随机分布在屏幕宽度0-100%范围
- 粒子大小：20-40px随机
- 粒子内容：从对应emoji数组中随机选择
- 生成间隔：每个粒子间隔100ms生成，形成连续效果

#### CSS动画实现
使用@keyframes定义fall动画，包含transform和opacity属性变化。动画完成后自动移除DOM元素，避免内存泄漏。

### 5.7 局域网访问配置

Flask应用启动时使用参数：`app.run(debug=True, host='0.0.0.0', port=5000)`，监听所有网络接口的5000端口。局域网内的其他设备可以通过服务器的IP地址访问应用。

## 6. 部署运行步骤

### 6.1 前置准备
```bash
# 1. 确保Ollama已安装并运行
ollama serve

# 2. 确保已拉取模型
ollama pull qwen3:32b

# 3. 安装Python依赖
pip install flask flask-cors requests
```

### 6.2 启动应用
```bash
# 进入项目目录
cd /Users/infraeo/Desktop/AI_test

# 启动Flask应用
python app.py
```

### 6.3 访问应用
- 本地访问：`http://localhost:5000`
- 局域网访问：`http://[你的IP地址]:5000`
- 确保网络连接正常（Live2D需要CDN资源）

### 6.4 常见问题

#### Q1: Ollama连接失败
- 检查Ollama是否运行：`ps aux | grep ollama`
- 确认端口11434未被占用
- 检查模型是否下载完成：`ollama list`

#### Q2: Live2D不显示
- 检查网络连接
- 查看浏览器控制台错误
- 确认CDN资源可访问

#### Q3: 中文显示乱码
- 确保文件编码为UTF-8
- 检查浏览器字符集设置

## 7. API接口文档

### 7.1 主页
- **URL**: `/`
- **方法**: GET
- **返回**: chat.html页面内容

### 7.2 聊天接口
- **URL**: `/api/chat`
- **方法**: POST
- **请求体**:
```json
{
    "message": "用户消息",
    "history": [
        {"role": "user", "content": "历史消息1"},
        {"role": "assistant", "content": "AI回复1"}
    ]
}
```
- **响应**: Server-Sent Events流
```
data: {"content": "AI回复片段"}
data: {"done": true}
```

### 7.3 静态资源
- `/ollama.png` - AI头像
- `/ollama_user.png` - 用户头像
- `/emotions.txt` - 情绪文本

## 8. 前端交互设计

### 8.1 UI布局
```
┌─────────────────────────────────────┐
│          Token计数器                 │
├─────────────────────────────────────┤
│                                     │
│  Live2D模型     聊天窗口            │
│  (左侧)         (右侧)              │
│                                     │
│                 [输入框] [发送]      │
└─────────────────────────────────────┘
```

### 8.2 动画效果实现细节

#### 8.2.1 背景动画
**实现方式**：CSS repeating-linear-gradient + animation
```css
background: repeating-linear-gradient(45deg, #cce5ff, #cce5ff 30px, #e6f2ff 30px, #e6f2ff 60px)
animation: slideRight 3s linear infinite
```
**效果**：45度条纹以每3秒84.853px的速度向右滚动，形成动态背景

#### 8.2.2 消息动画
**fadeIn动画定义**：
- 初始状态：opacity: 0, translateY(10px)
- 结束状态：opacity: 1, translateY(0)
- 动画时长：0.3秒，ease-out缓动
- 应用于每条新消息的出现

#### 8.2.3 AI头像旋转
**打字状态**：
- 添加.rotating类，无限循环旋转360度
- 动画时长：2秒/圈，linear匀速

**完成状态**：
- 计算当前旋转角度
- 使用CSS变量动态设置旋转到最近的360度倍数
- 1秒内平滑旋转归位
- 使用transform矩阵计算确保准确性

#### 8.2.4 手绘边框效果
**SVG滤镜定义**：
```xml
<filter id="sketch-border">
    <feTurbulence baseFrequency="0.02" numOctaves="2" seed="5"/>
    <feDisplacementMap scale="2"/>
</filter>
```
**应用范围**：
- .chat-container（主聊天窗口）
- .message-bubble（所有消息气泡）
- .token-counter（Token计数器）
- .chat-bubble（情绪对话框）

#### 8.2.5 打字指示器
**三个圆点动画**：
- 使用CSS animation-delay错开时间
- 每个点延迟0.2秒
- 上下跳动动画，营造打字效果

### 8.3 交互流程
1. 用户输入消息 → 按Enter或点击发送
2. 显示打字指示器 → AI头像开始旋转
3. 接收流式响应 → 实时更新消息
4. 完成响应 → 头像停止旋转
5. 更新Token计数 → 保存对话历史

### 8.4 样式特点
- **配色方案**: 粉色系为主（#ff91a4, #ffa0b4）
- **字体**: ZCOOL XiaoWei（中文艺术字体）
- **圆角设计**: 大量使用圆角营造柔和感
- **阴影效果**: 多层阴影增加立体感

## 9. 关键实现细节

### 9.1 全屏特效容器
HTML中定义：`<div class="effects-container" id="effectsContainer"></div>`
CSS样式：position: fixed; pointer-events: none; z-index: 9999; overflow: hidden;

### 9.2 AI头像旋转实现
打字时添加rotating类实现旋转，完成后通过计算transform矩阵获取当前角度，设置CSS变量--current-rotation和--rotation-diff，实现平滑归位动画。

### 9.3 对话历史管理
使用chatHistory数组存储，格式为{role: 'user'|'assistant', content: string}，保持最近40条消息（20轮对话）。

### 9.4 Live2D点击处理
创建800px宽的透明点击区域覆盖Live2D，设置canvas的pointer-events为none，在点击层上处理交互事件。

### 9.5 Token计数
每4个字符估算为1个token，累加显示总输入和输出token数。

---

本文档完整记录了Chat with Shizuku项目的实现细节。