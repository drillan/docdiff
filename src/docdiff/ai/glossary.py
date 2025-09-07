"""Glossary management for terminology consistency in translations."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class GlossaryTerm:
    """A single glossary term."""

    term: str
    definition: str
    translation: Optional[str] = None
    maintain_original: bool = False
    aliases: List[str] = field(default_factory=list)
    context: Optional[str] = None
    category: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "term": self.term,
            "definition": self.definition,
            "translation": self.translation,
            "maintain_original": self.maintain_original,
            "aliases": self.aliases,
            "context": self.context,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "GlossaryTerm":
        """Create from dictionary."""
        return cls(
            term=data["term"],
            definition=data["definition"],
            translation=data.get("translation"),
            maintain_original=data.get("maintain_original", False),
            aliases=data.get("aliases", []),
            context=data.get("context"),
            category=data.get("category"),
        )


@dataclass
class TranslationRules:
    """Rules for translation behavior."""

    preserve_code_terms: bool = True
    translate_ui_elements: bool = True
    keep_product_names: bool = True
    maintain_formatting: bool = True
    preserve_references: bool = True

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "preserve_code_terms": self.preserve_code_terms,
            "translate_ui_elements": self.translate_ui_elements,
            "keep_product_names": self.keep_product_names,
            "maintain_formatting": self.maintain_formatting,
            "preserve_references": self.preserve_references,
        }


class Glossary:
    """Manage glossary for consistent translations."""

    def __init__(self):
        """Initialize glossary."""
        self.terms: Dict[str, GlossaryTerm] = {}
        self.rules = TranslationRules()
        self._term_index: Dict[str, str] = {}  # Lowercase to actual term mapping
        self._alias_index: Dict[str, str] = {}  # Alias to term mapping

    def add_term(self, term: GlossaryTerm) -> None:
        """Add a term to the glossary.

        Args:
            term: Glossary term to add
        """
        self.terms[term.term] = term

        # Update indices
        self._term_index[term.term.lower()] = term.term

        # Add aliases to index
        for alias in term.aliases:
            self._alias_index[alias.lower()] = term.term

    def get_term(self, text: str) -> Optional[GlossaryTerm]:
        """Get a term from the glossary.

        Args:
            text: Text to look up (case-insensitive)

        Returns:
            GlossaryTerm if found, None otherwise
        """
        # Try direct lookup
        term_key = self._term_index.get(text.lower())
        if term_key:
            return self.terms.get(term_key)

        # Try alias lookup
        alias_key = self._alias_index.get(text.lower())
        if alias_key:
            return self.terms.get(alias_key)

        return None

    def find_terms_in_text(self, text: str) -> List[GlossaryTerm]:
        """Find all glossary terms in text.

        Args:
            text: Text to search

        Returns:
            List of found glossary terms
        """
        found_terms: List[GlossaryTerm] = []
        seen: Set[str] = set()

        # Check each term
        for term_key in self.terms:
            term = self.terms[term_key]

            # Skip if already found
            if term.term in seen:
                continue

            # Check if term appears in text (case-insensitive)
            if term.term.lower() in text.lower():
                found_terms.append(term)
                seen.add(term.term)

            # Check aliases
            for alias in term.aliases:
                if alias.lower() in text.lower():
                    if term.term not in seen:
                        found_terms.append(term)
                        seen.add(term.term)
                    break

        return found_terms

    def load_from_file(self, file_path: Path) -> None:
        """Load glossary from JSON file.

        Args:
            file_path: Path to glossary JSON file
        """
        if not file_path.exists():
            return

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Load terms
        if "terms" in data:
            for term_data in data["terms"]:
                term = GlossaryTerm.from_dict(term_data)
                self.add_term(term)

        # Load rules
        if "rules" in data:
            rules_data = data["rules"]
            self.rules.preserve_code_terms = rules_data.get("preserve_code_terms", True)
            self.rules.translate_ui_elements = rules_data.get(
                "translate_ui_elements", True
            )
            self.rules.keep_product_names = rules_data.get("keep_product_names", True)
            self.rules.maintain_formatting = rules_data.get("maintain_formatting", True)
            self.rules.preserve_references = rules_data.get("preserve_references", True)

    def save_to_file(self, file_path: Path) -> None:
        """Save glossary to JSON file.

        Args:
            file_path: Path to save glossary
        """
        data = {
            "terms": [term.to_dict() for term in self.terms.values()],
            "rules": self.rules.to_dict(),
        }

        # Create parent directory if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_prompt_context(self) -> str:
        """Create glossary context for translation prompt.

        Returns:
            Formatted glossary context string
        """
        if not self.terms:
            return "No glossary terms defined."

        lines = ["GLOSSARY TERMS:"]

        # Group by category if available
        categorized: Dict[str, List[GlossaryTerm]] = {}
        uncategorized: List[GlossaryTerm] = []

        for term in self.terms.values():
            if term.category:
                if term.category not in categorized:
                    categorized[term.category] = []
                categorized[term.category].append(term)
            else:
                uncategorized.append(term)

        # Add categorized terms
        for category, terms in sorted(categorized.items()):
            lines.append(f"\n{category}:")
            for term in sorted(terms, key=lambda t: t.term):
                lines.append(self._format_term(term))

        # Add uncategorized terms
        if uncategorized:
            lines.append("\nGeneral Terms:")
            for term in sorted(uncategorized, key=lambda t: t.term):
                lines.append(self._format_term(term))

        # Add rules
        lines.append("\nTRANSLATION RULES:")
        if self.rules.preserve_code_terms:
            lines.append("- Preserve all code terms exactly as written")
        if self.rules.translate_ui_elements:
            lines.append("- Translate UI elements and labels")
        if self.rules.keep_product_names:
            lines.append("- Keep product names unchanged")
        if self.rules.maintain_formatting:
            lines.append("- Maintain all markdown formatting")
        if self.rules.preserve_references:
            lines.append("- Preserve all {ref} and {term} references exactly")

        return "\n".join(lines)

    def _format_term(self, term: GlossaryTerm) -> str:
        """Format a single term for prompt.

        Args:
            term: Glossary term to format

        Returns:
            Formatted term string
        """
        parts = [f"- {term.term}"]

        if term.translation:
            if term.maintain_original:
                parts.append(f"→ {term.translation} (keep original)")
            else:
                parts.append(f"→ {term.translation}")
        elif term.maintain_original:
            parts.append("(do not translate)")

        if term.definition:
            parts.append(f"// {term.definition}")

        return " ".join(parts)

    def validate_translation(
        self,
        source: str,
        translation: str,
    ) -> Dict[str, List[str]]:
        """Validate translation against glossary.

        Args:
            source: Source text
            translation: Translated text

        Returns:
            Dictionary of validation issues
        """
        issues: Dict[str, List[str]] = {
            "missing_terms": [],
            "incorrect_terms": [],
            "warnings": [],
        }

        # Find terms in source
        source_terms = self.find_terms_in_text(source)

        for term in source_terms:
            # Check if term should be maintained
            if term.maintain_original:
                if term.term not in translation:
                    issues["missing_terms"].append(
                        f"Term '{term.term}' should be preserved"
                    )

            # Check if term has specific translation
            elif term.translation:
                if term.translation not in translation:
                    issues["incorrect_terms"].append(
                        f"Term '{term.term}' should be translated as '{term.translation}'"
                    )

        return issues

    def get_statistics(self) -> Dict:
        """Get glossary statistics.

        Returns:
            Dictionary of statistics
        """
        categories = set()
        maintain_original_count = 0
        has_translation_count = 0

        for term in self.terms.values():
            if term.category:
                categories.add(term.category)
            if term.maintain_original:
                maintain_original_count += 1
            if term.translation:
                has_translation_count += 1

        return {
            "total_terms": len(self.terms),
            "categories": len(categories),
            "maintain_original": maintain_original_count,
            "has_translation": has_translation_count,
            "total_aliases": sum(len(t.aliases) for t in self.terms.values()),
        }


class GlossaryBuilder:
    """Build glossary from existing translations."""

    def __init__(self):
        """Initialize glossary builder."""
        self.term_candidates: Dict[str, int] = {}  # Term frequency counter

    def extract_from_translations(
        self,
        source_texts: List[str],
        translations: List[str],
    ) -> List[GlossaryTerm]:
        """Extract potential glossary terms from translations.

        Args:
            source_texts: List of source texts
            translations: List of corresponding translations

        Returns:
            List of potential glossary terms
        """
        # This is a simplified implementation
        # A real implementation would use NLP techniques

        terms: List[GlossaryTerm] = []

        # Extract capitalized words (potential product names)
        for source in source_texts:
            words = source.split()
            for word in words:
                if word and word[0].isupper() and len(word) > 2:
                    self.term_candidates[word] = self.term_candidates.get(word, 0) + 1

        # Create terms for frequent candidates
        for term, frequency in self.term_candidates.items():
            if frequency >= 3:  # Appears at least 3 times
                glossary_term = GlossaryTerm(
                    term=term,
                    definition=f"Frequently used term (appears {frequency} times)",
                    maintain_original=True,  # Conservative default
                )
                terms.append(glossary_term)

        return terms
