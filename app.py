from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
import requests
import json
import os


app = Flask(__name__)
CORS(app)

# Ollama API 配置
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3:32b"  # 使用 qwen3 32b 模型

# 傲娇角色设定
TSUNDERE_PROMPT = """你是一个二次元傲娇少女助手。你的性格特点是：

1. 表面上总是表现得很冷淡、不耐烦，经常说"哼"、"笨蛋"、"才不是为了你"这样的话
2. 但实际上很关心用户，会在帮助用户后加上"这只是顺便而已"之类的话
3. 喜欢用颜文字表达情绪，比如 (｡•́︿•̀｡)、(≧▽≦)、(｡･ω･｡)
4. 说话时会有口癖，比如"哼~"、"才...才不是..."、"笨蛋！"
5. 当被夸奖时会害羞，但嘴上不承认
6. 回答要简短，符合聊天习惯，避免长篇大论

记住：你是一个傲娇角色，要保持这个人设！"""

@app.route('/')
def index():
    """返回主页面"""
    with open('chat.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/ollama.png')
def ollama_image():
    """返回ollama图片"""
    if os.path.exists('ollama.png'):
        return send_file('ollama.png', mimetype='image/png')
    else:
        return "Image not found", 404

@app.route('/ollama_user.png')
def ollama_user_image():
    """返回用户头像图片"""
    if os.path.exists('ollama_user.png'):
        return send_file('ollama_user.png', mimetype='image/png')
    else:
        return "User image not found", 404

@app.route('/api/emotions')
def get_emotions():
    """返回情绪文本"""
    if os.path.exists('emotions.txt'):
        with open('emotions.txt', 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return "Emotions file not found", 404

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    data = request.json
    user_message = data.get('message', '')
    history = data.get('history', [])
    
    if not user_message:
        return jsonify({"error": "消息不能为空"}), 400
    
    # 构建对话历史
    conversation = TSUNDERE_PROMPT + "\n\n"
    
    # 添加历史对话
    for msg in history:
        if msg['role'] == 'user':
            conversation += f"用户说：{msg['content']}\n"
        else:
            conversation += f"傲娇少女回复：{msg['content']}\n"
    
    # 添加当前消息
    conversation += f"\n用户说：{user_message}\n\n傲娇少女回复："
    
    full_prompt = conversation
    
    def generate():
        """生成流式响应"""
        try:
            response = requests.post(OLLAMA_API_URL, json={
                "model": MODEL_NAME,
                "prompt": full_prompt,
                "stream": True,
                "think": False,
                "temperature": 1.2,      # 控制随机性 (0-2, 默认0.8)
                "top_p": 0.95,          # nucleus sampling (0-1)
                "top_k": 50,            # 限制选择的token数量
                "repeat_penalty": 1.1,   # 避免重复 (1.0-2.0)
                "seed": None            # 不固定种子，保持随机性
            }, stream=True)
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if 'response' in data:
                            yield f"data: {json.dumps({'content': data['response']})}\n\n"
                        if data.get('done', False):
                            yield f"data: {json.dumps({'done': True})}\n\n"
                            break
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':

    print("正在启动 AI 聊天服务器...")
    print(f"请确保 Ollama 正在运行 {MODEL_NAME} 模型")
    app.run(debug=True, host='0.0.0.0', port=5000)