from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from llama_index.schema import NodeRelationship, RelatedNodeInfo
from llama_index.vector_stores.types import BasePydanticVectorStore
from llama_index.vector_stores.types import VectorStore as LIVectorStore
from llama_index.vector_stores.types import VectorStoreQuery

from kotaemon.base import DocumentWithEmbedding


class BaseVectorStore(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        ...

    @abstractmethod
    def add(
        self,
        embeddings: list[list[float]] | list[DocumentWithEmbedding],
        metadatas: Optional[list[dict]] = None,
        ids: Optional[list[str]] = None,
    ) -> list[str]:
        """Add vector embeddings to vector stores

        Args:
            embeddings: List of embeddings
            metadatas: List of metadata of the embeddings
            ids: List of ids of the embeddings
            kwargs: meant for vectorstore-specific parameters

        Returns:
            List of ids of the embeddings
        """
        ...

    @abstractmethod
    def delete(self, ids: list[str], **kwargs):
        """Delete vector embeddings from vector stores

        Args:
            ids: List of ids of the embeddings to be deleted
            kwargs: meant for vectorstore-specific parameters
        """
        ...

    @abstractmethod
    def query(
        self,
        embedding: list[float],
        top_k: int = 1,
        ids: Optional[list[str]] = None,
        **kwargs,
    ) -> tuple[list[list[float]], list[float], list[str]]:
        """Return the top k most similar vector embeddings

        Args:
            embedding: List of embeddings
            top_k: Number of most similar embeddings to return
            ids: List of ids of the embeddings to be queried

        Returns:
            the matched embeddings, the similarity scores, and the ids
        """
        ...


class LlamaIndexVectorStore(BaseVectorStore):
    _li_class: type[LIVectorStore | BasePydanticVectorStore]

    def __init__(self, *args, **kwargs):
        if self._li_class is None:
            raise AttributeError(
                "Require `_li_class` to set a VectorStore class from LlamarIndex"
            )

        self._client = self._li_class(*args, **kwargs)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            return super().__setattr__(name, value)

        return setattr(self._client, name, value)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)

    def add(
        self,
        embeddings: list[list[float]] | list[DocumentWithEmbedding],
        metadatas: Optional[list[dict]] = None,
        ids: Optional[list[str]] = None,
    ):
        if isinstance(embeddings[0], list):
            nodes: list[DocumentWithEmbedding] = [
                DocumentWithEmbedding(embedding=embedding) for embedding in embeddings
            ]
        else:
            nodes = embeddings  # type: ignore
        if metadatas is not None:
            for node, metadata in zip(nodes, metadatas):
                node.metadata = metadata
        if ids is not None:
            for node, id in zip(nodes, ids):
                node.id_ = id
                node.relationships = {
                    NodeRelationship.SOURCE: RelatedNodeInfo(node_id=id)
                }

        return self._client.add(nodes=nodes)

    def delete(self, ids: list[str], **kwargs):
        for id_ in ids:
            self._client.delete(ref_doc_id=id_, **kwargs)

    def query(
        self,
        embedding: list[float],
        top_k: int = 1,
        ids: Optional[list[str]] = None,
        **kwargs,
    ) -> tuple[list[list[float]], list[float], list[str]]:
        output = self._client.query(
            query=VectorStoreQuery(
                query_embedding=embedding,
                similarity_top_k=top_k,
                node_ids=ids,
                **kwargs,
            ),
        )

        embeddings = []
        if output.nodes:
            for node in output.nodes:
                embeddings.append(node.embedding)
        similarities = output.similarities if output.similarities else []
        out_ids = output.ids if output.ids else []

        return embeddings, similarities, out_ids
