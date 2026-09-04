from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from config import CORPUS_ROOT


TOKEN_RE = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]", re.IGNORECASE)
HEADING_RE = re.compile(r"(?m)^#{2,3}\s+")


class CorpusPolicyError(RuntimeError):
    pass


@dataclass(frozen=True)
class Passage:
    case_id: str
    title: str
    relative_path: str
    section: str
    text: str


def _tokens(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text)]


def _split_sections(text: str, max_chars: int = 3600) -> list[tuple[str, str]]:
    starts = [match.start() for match in HEADING_RE.finditer(text)]
    if not starts:
        starts = [0]
    sections: list[tuple[str, str]] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(text)
        block = text[start:end].strip()
        if not block:
            continue
        first_line = block.splitlines()[0].lstrip("# ").strip() or "正文"
        for offset in range(0, len(block), max_chars):
            chunk = block[offset : offset + max_chars].strip()
            if chunk:
                sections.append((first_line, chunk))
    return sections


class KnowledgeCorpus:
    """Read-only retriever governed exclusively by corpus.json retrieval_files."""

    def __init__(self, root: Path = CORPUS_ROOT) -> None:
        self.root = root.resolve()
        manifest_path = self.root / "manifests" / "corpus.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        configured = manifest.get("retrieval_files", [])
        if not configured:
            raise CorpusPolicyError("知识库清单为空。")

        self.allowed_paths: tuple[Path, ...] = tuple(
            self._validate_retrieval_path(relative_path) for relative_path in configured
        )
        self.passages = self._build_passages()
        self._document_frequency = self._build_document_frequency()

    def _validate_retrieval_path(self, relative_path: str) -> Path:
        normalized = Path(relative_path)
        if normalized.is_absolute() or normalized.parts[:2] != ("cases", "knowledge"):
            raise CorpusPolicyError(f"非法检索路径：{relative_path}")
        resolved = (self.root / normalized).resolve()
        if self.root not in resolved.parents or not resolved.is_file():
            raise CorpusPolicyError(f"知识案例不存在或越界：{relative_path}")
        return resolved

    def _build_passages(self) -> tuple[Passage, ...]:
        passages: list[Passage] = []
        for path in self.allowed_paths:
            text = path.read_text(encoding="utf-8")
            case_id = re.search(r"(?m)^case_id:\s*(.+)$", text)
            title = re.search(r"(?m)^title:\s*(.+)$", text)
            relative = str(path.relative_to(self.root))
            for section, chunk in _split_sections(text):
                passages.append(
                    Passage(
                        case_id=case_id.group(1).strip() if case_id else path.stem,
                        title=title.group(1).strip() if title else path.stem,
                        relative_path=relative,
                        section=section,
                        text=chunk,
                    )
                )
        return tuple(passages)

    def _build_document_frequency(self) -> Counter[str]:
        frequency: Counter[str] = Counter()
        for passage in self.passages:
            frequency.update(set(_tokens(passage.text)))
        return frequency

    def search(self, query: str, max_results: int = 3) -> list[dict[str, str | float]]:
        query_tokens = Counter(_tokens(query))
        if not query_tokens:
            return []
        total = max(len(self.passages), 1)
        scored: list[tuple[float, Passage]] = []
        for passage in self.passages:
            passage_tokens = Counter(_tokens(passage.text))
            length_norm = 1.0 + math.log(1.0 + sum(passage_tokens.values()))
            score = 0.0
            for token, query_count in query_tokens.items():
                term_count = passage_tokens.get(token, 0)
                if not term_count:
                    continue
                inverse_frequency = math.log((total + 1) / (self._document_frequency[token] + 1)) + 1
                score += query_count * (1 + math.log(term_count)) * inverse_frequency / length_norm
            if score > 0:
                scored.append((score, passage))
        scored.sort(key=lambda item: (-item[0], item[1].case_id, item[1].section))

        results: list[dict[str, str | float]] = []
        seen_cases: set[str] = set()
        for score, passage in scored:
            if passage.case_id in seen_cases:
                continue
            seen_cases.add(passage.case_id)
            results.append(
                {
                    "case_id": passage.case_id,
                    "title": passage.title,
                    "section": passage.section,
                    "source": passage.relative_path,
                    "score": round(score, 4),
                    "excerpt": passage.text[:2400],
                }
            )
            if len(results) >= max(1, min(max_results, 5)):
                break
        return results

    def policy_summary(self) -> dict[str, object]:
        return {
            "retrieval_case_count": len(self.allowed_paths),
            "passage_count": len(self.passages),
            "allowed_prefix": "cases/knowledge/",
            "development_access": False,
            "blind_test_access": False,
        }


_CORPUS: KnowledgeCorpus | None = None


def get_corpus() -> KnowledgeCorpus:
    global _CORPUS
    if _CORPUS is None:
        _CORPUS = KnowledgeCorpus()
    return _CORPUS
