# src/infrastructure/llm_adapter.py
import logging
import torch
import re
import threading
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.domain.ports import LLMPort

logger = logging.getLogger(__name__)

import os

class QwenLocalAdapter(LLMPort):
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("MODEL_NAME", "Qwen/Qwen3-0.6B")
        self._is_ready = False
        self.tokenizer = None
        self.model = None
        
        # Tải trong background để không block API chính
        threading.Thread(target=self._load_model, daemon=True).start()

    def _load_model(self):
        try:
            logger.info(f"Đang tải model {self.model_name}...")
            
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
            self._is_ready = True
            logger.info(f"Đã tải xong model {self.model_name}")
        except Exception as e:
            logger.error(f"Lỗi tải model Qwen: {e}")

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        if not self._is_ready:
            return "Hệ thống đang tải mô hình ngôn ngữ, vui lòng đợi trong giây lát..."
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

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
            
            think_match = re.search(r'<think>(.*?)</think>', raw_content, re.DOTALL)
            if think_match:
                thinking_process = think_match.group(1).strip()
                logger.info(f"Model Thinking: {thinking_process[:200]}...") 
            
            clean_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
            
            return clean_content

        except Exception as e:
            logger.error(f"Qwen 3 Error: {e}")
            return "Xin lỗi, hệ thống đang gặp sự cố xử lý."