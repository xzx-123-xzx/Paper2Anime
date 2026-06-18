import os
from typing import Dict, Any

import pdfplumber
from docx import Document
from common.logger import my_logger as logger

class DocumentParser:
    def parse(self, file_path: str) -> Dict[str, Any]:
        ext = os.path.splitext(file_path)[-1].lower()
        
        if ext == ".pdf":
            return self._parse_pdf(file_path)
        elif ext == ".docx":
            return self._parse_docx(file_path)
        elif ext == ".txt":
            return self._parse_txt(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
    
    def _parse_pdf(self, file_path: str) -> Dict[str, Any]:
        logger.info(f"解析 PDF: {file_path}")
        
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        
        raw_text = "\n\n".join(text_parts)
        chapters = self._detect_chapters(raw_text)
        
        return {
            "raw_text": raw_text,
            "content": {
                "text": raw_text,
                "chapters": chapters
            },
            "metadata": {
                "file_name": os.path.basename(file_path),
                "file_type": "pdf",
                "page_count": len(text_parts),
                "chapter_count": len(chapters)
            }
        }
    
    def _parse_docx(self, file_path: str) -> Dict[str, Any]:
        logger.info(f"解析 DOCX: {file_path}")
        
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        raw_text = "\n\n".join(paragraphs)
        chapters = self._detect_chapters(raw_text)
        
        return {
            "raw_text": raw_text,
            "content": {
                "text": raw_text,
                "chapters": chapters
            },
            "metadata": {
                "file_name": os.path.basename(file_path),
                "file_type": "docx",
                "paragraph_count": len(paragraphs),
                "chapter_count": len(chapters)
            }
        }
    
    def _parse_txt(self, file_path: str) -> Dict[str, Any]:
        logger.info(f"解析 TXT: {file_path}")
        
        encodings = ['utf-8', 'gbk', 'gb2312']
        raw_text = ""
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    raw_text = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        chapters = self._detect_chapters(raw_text)
        
        return {
            "raw_text": raw_text,
            "content": {
                "text": raw_text,
                "chapters": chapters
            },
            "metadata": {
                "file_name": os.path.basename(file_path),
                "file_type": "txt",
                "char_count": len(raw_text),
                "chapter_count": len(chapters)
            }
        }
    
    def _detect_chapters(self, text: str) -> list:
        import re
        
        chapter_patterns = [
            r'^第[一二三四五六七八九十百千\d]+[章节部篇卷]',
            r'^[一二三四五六七八九十百千]+[.、]\s*\S+',
            r'^\d+[.、]\s*\S+',
            r'^第\d+章',
            r'^Chapter\s+\d+',
            r'^CHAPTER\s+\d+',
            r'^[Pp]art\s+\d+',
            r'^卷[一二三四五六七八九十\d]+',
        ]
        
        chapters = []
        lines = text.split('\n')
        current_chapter = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            matched = False
            for pattern in chapter_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    if current_chapter:
                        chapters.append(current_chapter)
                    current_chapter = {"title": line, "content": ""}
                    matched = True
                    break
            
            if not matched and current_chapter:
                current_chapter["content"] += line + "\n"
        
        if current_chapter:
            chapters.append(current_chapter)
        
        # 如果没有检测到章节，将整个文本作为一章
        if not chapters and text.strip():
            chapters.append({
                "title": "全文",
                "content": text.strip()
            })
        
        return chapters[:50]
