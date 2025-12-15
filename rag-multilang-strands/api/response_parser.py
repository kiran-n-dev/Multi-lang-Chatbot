"""
Response parser: Handles extraction and sanitization of structured content (tables, text) from RAG responses.
Ensures tables are rendered correctly in Streamlit while preserving text formatting.
Removes source citations and metadata before rendering.
"""

import re
from typing import List, Tuple, Dict, Optional


def extract_source_citations(response: str) -> Tuple[str, List[str]]:
    """
    Extract source citations from the response.
    
    Looks for patterns like [source: filename.pdf#page] and removes them from the text.
    
    Args:
        response: The full response text
        
    Returns:
        Tuple of (cleaned_response, list_of_sources)
    """
    sources = []
    
    # Match [source: ...] patterns
    source_pattern = r'\[source:\s*([^\]]+)\]'
    
    for match in re.finditer(source_pattern, response):
        source = match.group(1).strip()
        if source not in sources:
            sources.append(source)
    
    # Remove all source citations from response
    cleaned = re.sub(source_pattern, '', response, flags=re.IGNORECASE)
    
    return cleaned.strip(), sources


def extract_response_blocks(response: str) -> List[Tuple[str, str]]:
    """
    Extract blocks from the response: ('table', html) or ('text', markdown).
    
    Handles three types of table markers:
    1. --TABLE-START-- and --TABLE-END-- delimiters
    2. Raw <table> HTML tags
    3. Text between other content
    
    Also removes source citations before parsing.
    
    Returns:
        List of tuples: [('text', content), ('table', html), ('text', content), ...]
    """
    # First, extract and remove source citations
    response, sources = extract_source_citations(response)
    
    blocks = []
    last_end = 0
    
    # Find all table markers (both delimiter-based and tag-based)
    table_pattern = r'--TABLE-START--(.*?)--TABLE-END--|<table[^>]*>(.*?)</table>'
    
    for match in re.finditer(table_pattern, response, re.DOTALL | re.IGNORECASE):
        # Get the table content (group 1 for delimiters, group 2 for tags)
        table_html = match.group(1) if match.group(1) is not None else match.group(2)
        table_html = table_html.strip()
        
        # Add text before this table
        text_before = response[last_end:match.start()].strip()
        if text_before:
            blocks.append(('text', text_before))
        
        # Add the table
        if table_html:
            # Wrap tag-based tables in proper format
            if not table_html.startswith('<table'):
                table_html = f"<table>{table_html}</table>"
            blocks.append(('table', table_html))
        
        last_end = match.end()
    
    # Add remaining text after last table
    text_after = response[last_end:].strip()
    if text_after:
        blocks.append(('text', text_after))
    
    # If no tables found, treat entire response as text
    if not blocks:
        blocks.append(('text', response))
    
    # Store sources with blocks for later reference if needed
    if sources and blocks:
        # Attach sources to the last block
        blocks[-1] = (blocks[-1][0], blocks[-1][1], sources) if len(blocks[-1]) == 2 else blocks[-1]
    
    return blocks



def sanitize_html_table(html: str) -> str:
    """
    Sanitize HTML table: ensure valid <table>, <tr>, <th>, <td> tags only.
    Remove dangerous attributes, scripts, and unnecessary whitespace.
    
    Args:
        html: Raw HTML table string
        
    Returns:
        Sanitized HTML table string
    """
    # Remove any script tags or dangerous content
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)  # remove event handlers
    
    # Keep only safe table-related tags
    allowed_tags = r'</?(?:table|tr|th|td|tbody|thead|tfoot|colgroup|col|caption)[\s>]'
    
    def remove_unsafe_tags(text):
        """Remove all tags except allowed table-related ones."""
        parts = []
        last_end = 0
        for match in re.finditer(r'<[^>]+>', text):
            tag = match.group(0)
            # Keep the tag if it's in the allowed list
            if re.match(allowed_tags, tag, re.IGNORECASE):
                parts.append(text[last_end:match.start()])
                parts.append(tag)
            else:
                # Skip this tag, keep content
                parts.append(text[last_end:match.start()])
            last_end = match.end()
        parts.append(text[last_end:])
        return ''.join(parts)
    
    html = remove_unsafe_tags(html)
    
    # Clean up excess whitespace within and between tags
    html = re.sub(r'>\s+<', '><', html)  # Remove whitespace between tags
    html = re.sub(r'\s+', ' ', html)     # Collapse multiple spaces
    
    return html.strip()



def parse_response_for_rendering(response: str) -> List[Tuple[str, str]]:
    """
    Parse response and return a list of blocks ready for Streamlit rendering.
    
    Process:
    1. Extract and remove source citations
    2. Identify tables (both delimited and raw HTML)
    3. Sanitize HTML tables
    4. Preserve text formatting
    
    Each block is: ('text', markdown_content) or ('table', sanitized_html)
    
    Args:
        response: Full RAG response from the model
        
    Returns:
        List of (block_type, content) tuples
    """
    if not response or not response.strip():
        return [('text', 'No response available.')]
    
    blocks = extract_response_blocks(response)
    
    parsed = []
    for block in blocks:
        block_type = block[0]
        content = block[1]
        
        if block_type == 'table':
            # Sanitize the HTML table
            safe_html = sanitize_html_table(content)
            if safe_html:
                parsed.append(('table', safe_html))
        else:
            # Clean up text: remove extra whitespace, preserve structure
            text = content.strip()
            # Replace multiple newlines with single newline for cleaner rendering
            text = re.sub(r'\n\s*\n', '\n\n', text)
            if text:
                parsed.append(('text', text))
    
    # If we ended up with empty blocks, return a default message
    if not parsed:
        parsed.append(('text', 'Could not parse response content.'))
    
    return parsed

