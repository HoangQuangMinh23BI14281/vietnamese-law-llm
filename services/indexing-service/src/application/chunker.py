import re
import logging
from typing import List, Dict
from src.domain.models import LegalChunk

logger = logging.getLogger(__name__)

class LegalChunker:
    def __init__(self):
        # Regex nhận diện cấu trúc (Giữ nguyên vì đã tốt)
        # ^ : Đảm bảo chỉ bắt ở đầu dòng
        self.part_regex = re.compile(r"^(?:[\#\*]*\s*)?Phần\s+(?:thứ\s+)?([IVXLCDM]+|\w+)", re.IGNORECASE | re.MULTILINE)
        self.chapter_regex = re.compile(r"^(?:[\#\*]*\s*)?Chương\s+([IVXLCDM\d]+)", re.IGNORECASE | re.MULTILINE)
        self.section_regex = re.compile(r"^(?:[\#\*]*\s*)?Mục\s+([IVXLCDM\d]+)", re.IGNORECASE | re.MULTILINE)
        
        # Regex Điều: Bắt buộc đầu dòng + "Điều" + Số + Dấu ngắt (.:-)
        self.article_regex = re.compile(r"^(?:[\#\*]*\s*)?Điều\s+(\d+)[.:-]", re.IGNORECASE | re.MULTILINE)
        
        # [QUAN TRỌNG] Đã sửa garbage_regex: Bỏ \d+/\d+ để không xóa nhầm số hiệu luật
        self.garbage_regex = re.compile(r"^(?:CÔNG BÁO|Page\s+\d+|Trang\s+\d+)$", re.IGNORECASE | re.MULTILINE)

    def chunk(self, markdown_text: str, source_name: str) -> List[LegalChunk]:
        cleaned_text = self._clean_text(markdown_text)
        articles_data = self._parse_structure(cleaned_text)
        
        if not articles_data:
            logger.warning(" Fallback split triggered.")
            return self._fallback_split(cleaned_text, source_name)

        final_chunks = []
        for art in articles_data:
            # Metadata chuẩn cho Weaviate
            full_context = f"{art['header']} > {art['article_title']}".strip(" >")
            full_text = f"{full_context}\n{art['content']}"
            
            # Xử lý số điều (VD: "34") -> "Điều 34"
            article_str = str(art.get('article_number', '')).strip()
            if article_str:
                article_meta = f"Điều {article_str}"
            else:
                article_meta = ""

            final_chunks.append(LegalChunk(
                text=full_text,
                metadata={
                    "source": source_name,
                    "chapter": art['chapter'],
                    "article": article_meta, 
                    "is_full_article": True
                }
            ))
            
        return final_chunks

    def _clean_text(self, text: str) -> str:
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Bỏ dòng trống hoặc chỉ có số trang (theo regex mới)
            if not line: continue
            if self.garbage_regex.search(line): continue
            
            # Fix lỗi dính số thứ tự ở đầu dòng (nếu cần)
            # line = re.sub(r'^\d+\.\s+(?=[a-zđ]\))', '', line) 
            
            cleaned_lines.append(line)
        
        # Join lại
        text = "\n".join(cleaned_lines)
        
        # Nối dòng bị ngắt giữa chừng (Logic cũ của bạn - Giữ nguyên nếu thấy ổn)
        # Regex này giúp nối các câu bị ngắt xuống dòng vô lý, giúp hạn chế việc
        # "Điều XX" bị rớt xuống đầu dòng một cách vô tình.
        text = re.sub(r'(?<=\w)-\n(?=\w)', '', text) 
        text = re.sub(r'(?<=[a-záàảãạăắằẳẵặâấầẩẫậđéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ])\n(?=[a-záàảãạăắằẳẵặâấầẩẫậđéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ])', ' ', text)
        
        return text

    def _parse_structure(self, text: str) -> List[Dict]:
        # ... (Giữ nguyên logic hàm này như code trước tôi gửi) ...
        # (Chỉ cần đảm bảo logic append article_number vào dict là được)
        # Copy lại đoạn _parse_structure từ câu trả lời trước nếu cần
        lines = text.split('\n')
        structure = []
        curr_part, curr_chap, curr_sec = "", "", ""
        curr_art_num, curr_art_title = "", ""
        curr_art_content = []
        
        for line in lines:
            clean_line_start = line.lstrip("#* ")
            if self.part_regex.match(line): curr_part = clean_line_start; continue
            if self.chapter_regex.match(line): curr_chap = clean_line_start; continue
            if self.section_regex.match(line): curr_sec = clean_line_start; continue
                
            if match := self.article_regex.match(line):
                if curr_art_num:
                    structure.append({
                        "header": f"{curr_part} > {curr_chap} > {curr_sec}",
                        "chapter": curr_chap,
                        "article_number": curr_art_num,
                        "article_title": f"{curr_art_num} {curr_art_title}".strip(),
                        "content": "\n".join(curr_art_content)
                    })
                
                raw_match = match.group(0)
                curr_art_num = raw_match.replace('*', '').replace('#', '').replace('Điều', '').strip(' .:-')
                curr_art_title = line[len(raw_match):].strip()
                curr_art_content = []
                if len(curr_art_title) > 0 and len(curr_art_title.split()) > 15:
                      curr_art_content.append(curr_art_title)
                      curr_art_title = ""
            else:
                curr_art_content.append(line)
        
        if curr_art_num:
            structure.append({
                "header": f"{curr_part} > {curr_chap} > {curr_sec}",
                "chapter": curr_chap,
                "article_number": curr_art_num,
                "article_title": f"{curr_art_num} {curr_art_title}".strip(),
                "content": "\n".join(curr_art_content)
            })
            
        return structure

    def _fallback_split(self, text: str, source_name: str) -> List[LegalChunk]:
        # (Giữ nguyên logic fallback)
        chunks = []
        raw_splits = text.split('\n\n')
        for i, split in enumerate(raw_splits):
            if len(split.strip()) > 50:
                chunks.append(LegalChunk(
                    text=split.strip(),
                    metadata={"source": source_name, "is_fallback": True, "index": i}
                ))
        return chunks