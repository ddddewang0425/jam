# server.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

# 1) 실제 LLM 추론 로직이 들어 있는 모듈에서 import
#    mangae.py 안의 클래스/함수 이름을 확인해서 바꿔주세요.
from LLMClass import ChefBot

import config

# 2) 요청 바디 스키마 정의
class Prompt(BaseModel):
    text: str

# 3) 시스템 프롬프트(대화 컨텍스트) 로드
try:
    with open("ChefBotSystemPrompt.txt", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    logging.error("ChefBotSystemPrompt.txt 파일을 찾을 수 없습니다.")
    SYSTEM_PROMPT = ""

# 4) FastAPI 앱 생성
app = FastAPI(
    title="ChefVision LLM API",
    description="Unity에서 호출할 수 있는 LLM 추론 서버",
    version="1.0"
)

# 5) 상태 확인용(건강체크) 엔드포인트
@app.get("/health")
async def health():
    return {"status": "ok"}

# 6) LLM 추론용 메인 엔드포인트
@app.post("/generate")
async def generate(prompt: Prompt):
    if not SYSTEM_PROMPT:
        raise HTTPException(status_code=500, detail="시스템 프롬프트 로딩 실패")

    try:
        bot = ChefBot(model_name="gpt-4o", temperature=1.0, key=config.get_gptapi(), uuid=config.get_myuuid())
        # 실제 추론 호출 (메서드 이름 확인)
        answer = bot.chat(prompt.text)
        return {"output": answer}

    except Exception as e:
        logging.exception("LLM 추론 중 에러")
        raise HTTPException(status_code=500, detail=str(e))

# 7) 직접 실행할 때 Uvicorn 서버 띄우기
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
