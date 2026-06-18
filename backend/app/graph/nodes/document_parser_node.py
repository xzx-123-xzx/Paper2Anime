from typing import Dict, Any
from common.logger import my_logger as logger
from ...services.document_parser import DocumentParser

document_parser = DocumentParser()

def document_parser_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("执行文档解析节点")
    
    document_path = state.get("document_path", "")
    
    try:
        parsed = document_parser.parse(document_path)
        
        state["parsed_document"] = parsed.get("content", {})
        state["document_metadata"] = parsed.get("metadata", {})
        state["raw_document"] = parsed.get("raw_text", "")
        state["node_statuses"]["document_parser"] = "completed"
        state["progress"] = 5.0
        state["updated_at"] = __import__("datetime").datetime.now().isoformat()
        logger.info(f"文档解析完成，提取章节数: {len(parsed.get('content', {}).get('chapters', []))}")
    except Exception as e:
        logger.error(f"文档解析失败: {e}")
        state["node_statuses"]["document_parser"] = "failed"
        state["error_message"] = str(e)
    
    return state
