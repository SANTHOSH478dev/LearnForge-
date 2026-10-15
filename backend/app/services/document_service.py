import os
import re
import json
from typing import List, Dict, Any, Tuple
from app.config import settings

def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    """Extract pages from PDF using PyMuPDF (fitz) or pypdf fallback."""
    pages_data = []
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        for page_idx, page in enumerate(doc):
            text = page.get_text() or ""
            pages_data.append({
                "page_number": page_idx + 1,
                "text": text.strip()
            })
        doc.close()
        return pages_data
    except Exception as e:
        print(f"PyMuPDF failed ({e}), trying pypdf fallback...")
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages_data.append({
                    "page_number": page_idx + 1,
                    "text": text.strip()
                })
            return pages_data
        except Exception as e2:
            print(f"pypdf fallback failed: {e2}")
            return [{"page_number": 1, "text": f"Error extracting PDF: {e2}"}]

def extract_text_from_docx(file_path: str) -> List[Dict[str, Any]]:
    """Extract paragraphs and sections from DOCX."""
    try:
        import docx
        doc = docx.Document(file_path)
        full_text = []
        for p in doc.paragraphs:
            if p.text.strip():
                full_text.append(p.text.strip())
        
        # Approximate pages (~350 words per page)
        words = " \n ".join(full_text).split()
        chunk_size = 350
        pages_data = []
        if not words:
            return [{"page_number": 1, "text": ""}]
            
        for i in range(0, len(words), chunk_size):
            page_text = " ".join(words[i:i + chunk_size])
            pages_data.append({
                "page_number": (i // chunk_size) + 1,
                "text": page_text
            })
        return pages_data
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return [{"page_number": 1, "text": f"Error extracting DOCX: {e}"}]

def extract_text_from_pptx(file_path: str) -> List[Dict[str, Any]]:
    """Extract slides from PPTX."""
    try:
        import pptx
        prs = pptx.Presentation(file_path)
        pages_data = []
        for slide_idx, slide in enumerate(prs.slides):
            slide_texts = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_texts.append(shape.text.strip())
            pages_data.append({
                "page_number": slide_idx + 1,
                "text": "\n".join(slide_texts)
            })
        return pages_data
    except Exception as e:
        print(f"PPTX extraction error: {e}")
        return [{"page_number": 1, "text": f"Error extracting PPTX: {e}"}]

def extract_text_from_txt(file_path: str) -> List[Dict[str, Any]]:
    """Extract text from plain text file."""
    try:
        for enc in ["utf-8", "latin-1", "cp1252"]:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    content = f.read()
                    break
            except UnicodeDecodeError:
                continue
        else:
            content = ""

        # Break into ~400 word chunks
        words = content.split()
        chunk_size = 400
        pages_data = []
        if not words:
            return [{"page_number": 1, "text": ""}]
        for i in range(0, len(words), chunk_size):
            pages_data.append({
                "page_number": (i // chunk_size) + 1,
                "text": " ".join(words[i:i + chunk_size])
            })
        return pages_data
    except Exception as e:
        return [{"page_number": 1, "text": f"Error extracting TXT: {e}"}]

def extract_document(file_path: str, file_type: str) -> List[Dict[str, Any]]:
    """Dispatcher for extracting text by file type."""
    file_type = file_type.lower().replace(".", "")
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_type in ["docx", "doc"]:
        return extract_text_from_docx(file_path)
    elif file_type in ["pptx", "ppt"]:
        return extract_text_from_pptx(file_path)
    elif file_type in ["txt", "md"]:
        return extract_text_from_txt(file_path)
    else:
        return extract_text_from_txt(file_path)

def chunk_pages_data(pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Chunk extracted pages into semantic units preserving page number and header."""
    chunks = []
    chunk_index = 0

    for item in pages_data:
        page_num = item["page_number"]
        page_text = item["text"]
        
        if not page_text.strip():
            continue

        # Split paragraphs
        paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [p.strip() for p in page_text.split("\n") if p.strip()]

        current_heading = f"Page {page_num} Overview"
        current_buffer = []
        current_len = 0

        for para in paragraphs:
            # Check if this paragraph looks like a heading
            if len(para) < 80 and (para.isupper() or para.endswith(":") or re.match(r"^(#+|[0-9]+\.|\bChapter|\bSection)\s*", para)):
                current_heading = para.strip("# :.")

            current_buffer.append(para)
            current_len += len(para)

            if current_len >= 600:
                content = "\n\n".join(current_buffer)
                chunks.append({
                    "chunk_index": chunk_index,
                    "page_number": page_num,
                    "section_heading": current_heading[:200],
                    "content": content,
                    "token_count": len(content.split())
                })
                chunk_index += 1
                current_buffer = []
                current_len = 0

        if current_buffer:
            content = "\n\n".join(current_buffer)
            chunks.append({
                "chunk_index": chunk_index,
                "page_number": page_num,
                "section_heading": current_heading[:200],
                "content": content,
                "token_count": len(content.split())
            })
            chunk_index += 1

    return chunks

def analyze_document_content(chunks: List[Dict[str, Any]], title: str) -> Dict[str, Any]:
    """Generate summary, key concepts, topics, and question suggestions from chunks."""
    all_text = " ".join([c["content"] for c in chunks])
    
    # Extract topics based on common headings and capitalized phrases
    detected_topics = set()
    for c in chunks:
        h = c["section_heading"]
        if h and not h.startswith("Page "):
            cleaned = re.sub(r"^[0-9\.\s]+", "", h).strip()
            if len(cleaned) > 2 and len(cleaned) < 50:
                detected_topics.add(cleaned)

    # Keyword frequency analysis
    words = re.findall(r"\b[A-Za-z]{4,}\b", all_text)
    stopwords = {"this", "that", "with", "from", "have", "were", "which", "there", "their", "about", "would", "these", "other", "into", "more", "first", "could", "after", "where", "been", "through", "using"}
    freq: Dict[str, int] = {}
    for w in words:
        wl = w.lower()
        if wl not in stopwords and len(wl) > 3:
            freq[wl] = freq.get(wl, 0) + 1

    sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
    for kw, _ in sorted_keywords[:5]:
        detected_topics.add(kw.capitalize())

    topics_list = list(detected_topics)[:8]
    if not topics_list:
        topics_list = ["Foundational Concepts", "Methodology", "Core Principles", "Applications"]

    # Key Concepts extraction
    key_concepts = []
    # Look for definition-like patterns: "X is Y", "X refers to Y", "X: Y"
    for c in chunks:
        sentences = re.split(r"(?<=[.!?])\s+", c["content"])
        for s in sentences:
            m = re.match(r"^([A-Z][A-Za-z\s]{2,30})\s+(?:is|refers to|represents|denotes|means)\s+([^.]+)", s)
            if m:
                term = m.group(1).strip()
                defn = m.group(2).strip()
                if len(term.split()) <= 4 and len(defn) > 10:
                    key_concepts.append({"term": term, "definition": defn[:250]})
                    if len(key_concepts) >= 6:
                        break
        if len(key_concepts) >= 6:
            break

    if not key_concepts and sorted_keywords:
        for kw, _ in sorted_keywords[:4]:
            key_concepts.append({
                "term": kw.capitalize(),
                "definition": f"A primary recurring concept emphasized throughout the document relating to {title}."
            })

    # Summary synthesis
    first_few_chunks = chunks[:3]
    lead_text = " ".join([c["content"] for c in first_few_chunks])[:400]
    summary_text = (
        f"This document '{title}' covers key theoretical and practical frameworks. "
        f"Primary thematic areas include: {', '.join(topics_list[:4])}. "
        f"Core insights emphasize fundamental mechanisms, standard operating definitions, and applied problem-solving principles. "
        f"Contextual overview: {lead_text.strip()}..."
    )

    suggested_questions = [
        {"prompt": f"What is the primary role of {topics_list[0]}?", "difficulty": "medium", "type": "mcq"},
        {"prompt": f"Explain the relationship between {topics_list[0]} and {topics_list[1] if len(topics_list) > 1 else 'applications'}.", "difficulty": "hard", "type": "short_answer"},
        {"prompt": f"Identify the key characteristics of {key_concepts[0]['term'] if key_concepts else 'the system'}.", "difficulty": "easy", "type": "mcq"}
    ]

    return {
        "summary": summary_text,
        "topics": topics_list,
        "key_concepts": key_concepts,
        "suggested_questions": suggested_questions
    }
