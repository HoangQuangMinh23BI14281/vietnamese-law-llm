# src/infrastructure/llm_adapter.py
import logging
import torch
import re  # <--- Quan trọng: Dùng để xử lý chuỗi
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.domain.ports import LLMPort

logger = logging.getLogger(__name__)

class QwenLocalAdapter(LLMPort):
    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B"):
        logger.info(f" Đang tải model {model_name}...")
        self.model_name = model_name
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True 
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        logger.info(f"Đã tải xong model")

    def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # Bật chế độ Thinking
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=True 
            )
            
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

            with torch.no_grad():
                generated_ids = self.model.generate(
                    **model_inputs,
                    max_new_tokens=32768, 
                    temperature=0.6,
                    top_p=0.95
                )

            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
            raw_content = self.tokenizer.decode(output_ids, skip_special_tokens=True)
            
            # --- XỬ LÝ PHẦN THINKING ---
            
            # 1. In phần suy nghĩ ra LOG để bạn theo dõi (Debug)
            think_match = re.search(r'<think>(.*?)</think>', raw_content, re.DOTALL)
            if think_match:
                thinking_process = think_match.group(1).strip()
                logger.info(f" [Model Thinking]: {thinking_process[:200]}...") # Chỉ log 200 ký tự đầu cho gọn
            
            # 2. Xóa phần <think> để lấy câu trả lời sạch
            clean_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
            
            return clean_content

        except Exception as e:
            logger.error(f" Qwen 3 Error: {e}")
            return "Xin lỗi, hệ thống đang gặp sự cố xử lý."