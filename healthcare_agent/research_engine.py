import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any

class ResearchRAGEngine:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.documents = []
        self.metadatas = []
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.tfidf_matrix = None
        self._load_and_index()

    def _load_and_index(self):
        chunks_path = os.path.join(self.data_dir, "knowledge", "medical_research_chunks.csv")
        research_path = os.path.join(self.data_dir, "knowledge", "medical_research.csv")
        disease_path = os.path.join(self.data_dir, "knowledge", "disease_knowledge.csv")

        # 1. Load Research Papers metadata
        research_map = {}
        if os.path.exists(research_path):
            rdf = pd.read_csv(research_path)
            for _, r in rdf.iterrows():
                research_map[r["research_id"]] = dict(r)

        # 2. Index Chunks
        if os.path.exists(chunks_path):
            cdf = pd.read_csv(chunks_path)
            for _, row in cdf.iterrows():
                r_meta = research_map.get(row.get("research_id"), {})
                self.documents.append(str(row["chunk_text"]))
                self.metadatas.append({
                    "type": "RESEARCH_CHUNK",
                    "chunk_id": row["chunk_id"],
                    "title": row.get("source_title", r_meta.get("title", "Clinical Study")),
                    "category": row.get("category", "General Medicine"),
                    "doi": r_meta.get("doi", "N/A"),
                    "journal": r_meta.get("journal", "Peer-Reviewed Medical Literature"),
                    "pub_year": r_meta.get("publication_year", 2024)
                })

        # 3. Index Disease Knowledge
        if os.path.exists(disease_path):
            ddf = pd.read_csv(disease_path)
            for _, row in ddf.iterrows():
                text = f"Condition: {row['disease_name']} (ICD-10: {row['icd10']}). Standard of Care: {row['standard_of_care']}. Hallmark Symptoms: {row['hallmark_symptoms']}. Red Flags: {row['red_flags']}. Lifestyle: {row['lifestyle_precautions']}."
                self.documents.append(text)
                self.metadatas.append({
                    "type": "DISEASE_GUIDELINE",
                    "chunk_id": row["disease_id"],
                    "title": f"Clinical Guidelines: {row['disease_name']}",
                    "category": "Disease Management",
                    "doi": f"ICD-10:{row['icd10']}",
                    "journal": "National Standard of Care Guidelines",
                    "pub_year": 2025
                })

        if self.documents:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
            print(f"RAG Engine indexed {len(self.documents)} medical knowledge sources.")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves top-k evidence documents with similarity scores and formal citations.
        """
        if not self.documents or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        
        # Get top indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            meta = self.metadatas[idx]
            results.append({
                "document_text": self.documents[idx],
                "title": meta["title"],
                "category": meta["category"],
                "journal": meta["journal"],
                "doi": meta["doi"],
                "publication_year": meta["pub_year"],
                "relevance_score": round(score, 3),
                "citation": f"{meta['title']} ({meta['journal']}, {meta['pub_year']}). DOI: {meta['doi']}"
            })
        return results

# Singleton instance
rag_engine = ResearchRAGEngine()
