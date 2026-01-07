import re
import uuid
from src.domain.models import LegalChunk

class SimpleRecursiveSplitter:
    # ... (Giữ nguyên code Class Splitter cũ của bạn ở đây) ...
    def __init__(self, chunk_size=1000, chunk_overlap=200, separators=None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", "; ", " ", ""]

    def split_text(self, text):
        return self._recursive_split(text, self.separators)

    def _recursive_split(self, text, separators):
        final_chunks = []
        if not separators:
            for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                final_chunks.append(text[i:i + self.chunk_size])
            return final_chunks

        separator = separators[0]
        next_separators = separators[1:]
        
        if len(text) <= self.chunk_size:
            return [text]
            
        if separator not in text:
            return self._recursive_split(text, next_separators)
            
        splits = text.split(separator)
        current_chunk = ""
        
        for split in splits:
            if not split.strip(): continue
            temp_chunk = current_chunk + (separator if current_chunk else "") + split
            if len(temp_chunk) <= self.chunk_size:
                current_chunk = temp_chunk
            else:
                if current_chunk:
                    final_chunks.append(current_chunk)
                if len(split) > self.chunk_size:
                    sub_chunks = self._recursive_split(split, next_separators)
                    final_chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = split
                    
        if current_chunk:
            final_chunks.append(current_chunk)
        return final_chunks

class LegalDocProcessor:
    def __init__(self):
        self.text_splitter = SimpleRecursiveSplitter(chunk_size=1000, chunk_overlap=200)
        self.table_separator_pattern = re.compile(r"\|[- :]{3,}\|")

    def parse_and_chunk(self, markdown_text: str, source_name: str) -> list[LegalChunk]:
        raw_chunks = self._parse_structure(markdown_text)
        return self._refine_chunks(raw_chunks, source_name)

    def _parse_structure(self, text):
        # ... (Copy logic parse_legal_structure cũ của bạn vào đây) ...
        chunks = []
        lines = text.split('\n')
        current_chapter = "QUY ĐỊNH CHUNG"
        current_article_title = ""
        current_article_content = []
        
        chapter_regex = re.compile(r"^(?:[\#*]+\s*)?(Chương\s+[IVXLCDM]+\b.*)", re.IGNORECASE)
        article_regex = re.compile(r"^(?:[\#*]+\s*)?(Điều\s+\d+\..*)", re.IGNORECASE)

        for line in lines:
            line = line.strip()
            if not line: continue
            
            chap_match = chapter_regex.match(line)
            if chap_match:
                current_chapter = chap_match.group(1).replace('*', '').strip()
                continue
                
            art_match = article_regex.match(line)
            if art_match:
                if current_article_title:
                    full_content = "\n".join(current_article_content)
                    chunks.append({
                        "chapter": current_chapter,
                        "article_title": current_article_title,
                        "full_text": f"{current_chapter}\n{current_article_title}\n{full_content}",
                        "content": full_content
                    })
                current_article_title = art_match.group(1).replace('*', '').strip()
                current_article_content = []
            else:
                current_article_content.append(line)
                
        if current_article_title and current_article_content:
            full_content = "\n".join(current_article_content)
            chunks.append({
                "chapter": current_chapter,
                "article_title": current_article_title,
                "full_text": f"{current_chapter}\n{current_article_title}\n{full_content}",
                "content": full_content
            })
        return chunks

    def _refine_chunks(self, raw_chunks, source_name) -> list[LegalChunk]:
        final_output = []
        for chunk in raw_chunks:
            content = chunk['content']
            has_table = bool(self.table_separator_pattern.search(content))
            
            if len(content) < 1000:
                final_output.append(LegalChunk(
                    text=chunk['full_text'],
                    metadata={
                        "chapter": chunk['chapter'],
                        "article": chunk['article_title'],
                        "source": source_name,
                        "part": 1,
                        "has_table": has_table
                    }
                ))
            else:
                sub_texts = self.text_splitter.split_text(content)
                for i, sub_text in enumerate(sub_texts):
                    combined_text = f"{chunk['chapter']} - {chunk['article_title']} (Phần {i+1})\n{sub_text}"
                    sub_has_table = bool(self.table_separator_pattern.search(sub_text))
                    final_output.append(LegalChunk(
                        text=combined_text,
                        metadata={
                            "chapter": chunk['chapter'],
                            "article": chunk['article_title'],
                            "source": source_name,
                            "part": i + 1,
                            "has_table": sub_has_table
                        }
                    ))
        return final_output