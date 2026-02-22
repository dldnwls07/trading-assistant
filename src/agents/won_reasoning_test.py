import argparse
import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "KRX-Data/WON-Reasoning"

def load_model():
    print(f"Loading tokenizer and model: {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    from transformers import BitsAndBytesConfig
    
    # BitsAndBytes 설정 (4-bit가 Windows에서 안정성이 더 높음)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )

    device_map = "auto" if torch.cuda.is_available() else "cpu"

    # RTX 4070 Ti Super 최적화 버전
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map=device_map,
        quantization_config=bnb_config, # 최신 방식 적용
        low_cpu_mem_usage=True
    )
    print("Model loaded successfully.\n")
    return tokenizer, model

def generate_response(tokenizer, model, prompt_text: str):
    # Construct the instruction format (adjust based on WON-Reasoning's expected format, usually ChatML or Qwen-style)
    messages = [
        {"role": "system", "content": "당신은 한국 금융 시장 분석에 특화된 수석 애널리스트 AI입니다. 경제 뉴스와 공시 자료를 바탕으로 논리적으로 추론하여 투자 의견을 제시합니다."},
        {"role": "user", "content": prompt_text}
    ]
    
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    
    start_time = time.time()
    
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=1024,
        temperature=0.3, # Keep low for factual reasoning
        do_sample=True
    )
    
    # Decode only the generated part
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    end_time = time.time()
    print(f"--- Generation Time: {end_time - start_time:.2f} seconds ---")
    
    return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test WON-Reasoning Local LLM")
    parser.add_argument("--prompt", type=str, default="삼성전자의 2024년 1분기 영업이익이 전년 동기 대비 931.87% 증가한 6조 6060억원을 기록했습니다. 이 실적이 한국 증시 반도체 섹터에 미칠 영향을 분석해주세요.", help="입력할 금융 프롬프트")
    args = parser.parse_args()
    
    tokenizer, model = load_model()
    
    print(f"Prompt: {args.prompt}\n")
    print("Generating response... (This may take a while to download the 7B model on first run)")
    
    try:
        response = generate_response(tokenizer, model, args.prompt)
        print("\n=== Model Response ===\n")
        print(response)
    except Exception as e:
        print(f"Error during generation: {e}")
