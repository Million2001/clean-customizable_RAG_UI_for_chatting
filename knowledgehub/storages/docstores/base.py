from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Union

from ...base import Document


class BaseDocumentStore(ABC):
    """A document store is in charged of storing and managing documents"""

    @abstractmethod
    def __init__(self, *args, **kwargs):
        ...

    @abstractmethod
    def add(
        self,
        docs: Union[Document, List[Document]],
        ids: Optional[Union[List[str], str]] = None,
        **kwargs,
    ):
        """Add document into document store

        Args:
            docs: Document or list of documents
            ids: List of ids of the documents. Optional, if not set will use doc.doc_id
        """
        ...

    @abstractmethod
    def get(self, ids: Union[List[str], str]) -> List[Document]:
        """Get document by id"""
        ...

    @abstractmethod
    def get_all(self) -> List[Document]:
        """Get all documents"""
        ...

    @abstractmethod
    def count(self) -> int:
        """Count number of documents"""
        ...

    @abstractmethod
    def delete(self, ids: Union[List[str], str]):
        """Delete document by id"""
        ...

    @abstractmethod
    def save(self, path: Union[str, Path]):
        """Save document to path"""
        ...

    @abstractmethod
    def load(self, path: Union[str, Path]):
        """Load document store from path"""
        ...
