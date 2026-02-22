import torch
import re
from typing import Tuple
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.domains.analysis_kr.interfaces.abstract_analyst import LocalAnalyst
from src.domains.analysis_kr.entities.analysis import WONAnalysisResult

class WONReasoningAdapter(LocalAnalyst):
    def __init__(self, model_name: str = "KRX-Data/WON-Reasoning"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None

    def load_model(self):
        if self.model is not None:
            return

        print(f"Loading WON-Reasoning model: {self.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        device_map = "auto" if torch.cuda.is_available() else "cpu"

        from transformers import BitsAndBytesConfig
        
        # Windows/RTX4070TiS 최적화: 4-bit 양자화 설정
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )

        # 모델 로드
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map=device_map,
            quantization_config=bnb_config,
            low_cpu_mem_usage=True
        )
        print("Model loaded successfully.")

    async def analyze(self, ticker: str, context: str) -> WONAnalysisResult:
        if self.model is None:
            self.load_model()

        prompt = f"다음 기업/시장 상황을 한국 금융 전문가의 시각에서 분석해줘:\n\n{context}"
        
        messages = [
            {"role": "system", "content": "당신은 한국 금융 시장 분석에 특화된 수석 애널리스트 AI입니다. 추론 과정(<think>)은 성능 극대화를 위해 '영어(English)'로 진행해도 좋으나, 최종 분석 결과(<solution>)는 반드시 '현대적인 자연스러운 한글(한자 제외)'로만 작성하세요. 전문적이면서도 가독성 좋은 한국어 리포트를 제공하는 것이 최종 목표입니다."},
            {"role": "user", "content": prompt}
        ]
        
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=1024,
            temperature=0.3,
            do_sample=True
        )
        
        # 입력 부분 제외하고 생성된 토큰만 디코딩
        input_len = model_inputs.input_ids.shape[1]
        response = self.tokenizer.decode(generated_ids[0][input_len:], skip_special_tokens=True)
        
        # <think>와 <solution> 태그 파싱
        thought = self._extract_tag(response, "think")
        solution = self._extract_tag(response, "solution")
        
        # 태그가 없을 경우를 대비한 가공
        if not thought and not solution:
            solution = response # 통째로 결과로 취급
            
        return WONAnalysisResult(
            ticker=ticker,
            thought=thought or "Internal reasoning not explicitly tagged.",
            solution=solution or response
        )

    def _extract_tag(self, text: str, tag: str) -> str:
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""
