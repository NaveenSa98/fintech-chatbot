"""
Helper functions for text processing and document handling.
"""

from typing import List
from langchain.schema import Document
import re


def replace_t_with_space(documents: List[Document]) -> List[Document]:
    """
    Clean document text by replacing tab characters and multiple spaces with single spaces.
    Also removes extra whitespace and normalizes text.

    Args:
        documents: List of LangChain Document objects

    Returns:
        List of cleaned Document objects
    """
    cleaned_documents = []

    for doc in documents:
        # Replace tabs with spaces
        cleaned_text = doc.page_content.replace('\t', ' ')

        # Replace multiple spaces with single space
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

        # Strip leading and trailing whitespace
        cleaned_text = cleaned_text.strip()

        # Create new document with cleaned text
        cleaned_doc = Document(
            page_content=cleaned_text,
            metadata=doc.metadata
        )

        cleaned_documents.append(cleaned_doc)

    return cleaned_documents
