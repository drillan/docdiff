"""Token estimation for different content types and languages."""

from typing import Dict, Optional


class TokenEstimator:
    """Accurate token estimation for different content types.

    Provides language and content-aware token counting for optimal batching.
    """

    # Token multipliers by language (characters per token)
    LANGUAGE_MULTIPLIERS: Dict[str, float] = {
        "en": 0.25,  # ~4 chars per token
        "ja": 0.5,  # ~2 chars per token (Japanese)
        "zh": 0.5,  # ~2 chars per token (Chinese)
        "ko": 0.5,  # ~2 chars per token (Korean)
        "es": 0.23,  # Spanish
        "fr": 0.23,  # French
        "de": 0.22,  # German (compound words)
        "ru": 0.3,  # Cyrillic
        "ar": 0.35,  # Arabic
        "code": 0.3,  # Programming code
    }

    # Content type adjustments
    CONTENT_ADJUSTMENTS: Dict[str, float] = {
        "text": 1.0,  # Base multiplier
        "code": 1.2,  # Code needs more tokens
        "equation": 1.5,  # LaTeX/Math notation is complex
        "table": 1.3,  # Tables have structure
        "list": 1.1,  # Lists have bullets/numbers
        "metadata": 0.8,  # Metadata is simpler
    }

    def __init__(self, safety_margin: float = 0.1):
        """Initialize token estimator.

        Args:
            safety_margin: Safety margin to add (0.1 = 10% extra)
        """
        self.safety_margin = safety_margin

    def estimate(
        self,
        text: str,
        content_type: str = "text",
        language: str = "en",
    ) -> int:
        """Estimate token count for given text.

        Args:
            text: Text to estimate tokens for
            content_type: Type of content (text, code, equation, etc.)
            language: Language code (en, ja, zh, etc.)

        Returns:
            Estimated token count
        """
        if not text:
            return 0

        # Get base multiplier for language
        lang_multiplier = self.LANGUAGE_MULTIPLIERS.get(
            language, self.LANGUAGE_MULTIPLIERS["en"]
        )

        # Calculate base estimate
        base_estimate = len(text) * lang_multiplier

        # Apply content type adjustment
        content_adjustment = self.CONTENT_ADJUSTMENTS.get(
            content_type, self.CONTENT_ADJUSTMENTS["text"]
        )
        adjusted_estimate = base_estimate * content_adjustment

        # Apply safety margin
        final_estimate = adjusted_estimate * (1 + self.safety_margin)

        return int(final_estimate)

    def estimate_batch(
        self,
        texts: list[str],
        content_types: Optional[list[str]] = None,
        language: str = "en",
    ) -> int:
        """Estimate total tokens for a batch of texts.

        Args:
            texts: List of texts to estimate
            content_types: Optional list of content types (parallel to texts)
            language: Language code for all texts

        Returns:
            Total estimated token count
        """
        if not texts:
            return 0

        # If no content types provided, use "text" for all
        if content_types is None:
            content_types = ["text"] * len(texts)

        # Sum up estimates for all texts
        total = 0
        for text, content_type in zip(texts, content_types):
            total += self.estimate(text, content_type, language)

        return total

    def estimate_json_overhead(self, num_nodes: int) -> int:
        """Estimate JSON structure overhead tokens.

        Args:
            num_nodes: Number of nodes in the structure

        Returns:
            Estimated overhead tokens
        """
        # Approximate JSON structure overhead
        # Each node has: id, type, status, source, target, metadata
        # Plus brackets, quotes, commas, etc.
        overhead_per_node = 50  # Conservative estimate
        return num_nodes * overhead_per_node

    def fits_in_limit(
        self,
        text: str,
        limit: int,
        content_type: str = "text",
        language: str = "en",
    ) -> bool:
        """Check if text fits within token limit.

        Args:
            text: Text to check
            limit: Token limit
            content_type: Type of content
            language: Language code

        Returns:
            True if text fits within limit
        """
        estimated_tokens = self.estimate(text, content_type, language)
        return estimated_tokens <= limit

    def calculate_chunks_needed(
        self,
        text: str,
        max_tokens: int,
        content_type: str = "text",
        language: str = "en",
    ) -> int:
        """Calculate how many chunks are needed for text.

        Args:
            text: Text to chunk
            max_tokens: Maximum tokens per chunk
            content_type: Type of content
            language: Language code

        Returns:
            Number of chunks needed
        """
        total_tokens = self.estimate(text, content_type, language)
        chunks = (total_tokens + max_tokens - 1) // max_tokens  # Ceiling division
        return max(1, chunks)

    def get_optimal_batch_size(
        self,
        texts: list[str],
        max_tokens: int,
        content_types: Optional[list[str]] = None,
        language: str = "en",
    ) -> int:
        """Get optimal batch size to stay under token limit.

        Args:
            texts: List of texts to batch
            max_tokens: Maximum tokens per batch
            content_types: Optional list of content types
            language: Language code

        Returns:
            Optimal number of texts to include in batch
        """
        if not texts:
            return 0

        if content_types is None:
            content_types = ["text"] * len(texts)

        # Find how many texts fit in the limit
        current_tokens = 0
        batch_size = 0

        for i, (text, content_type) in enumerate(zip(texts, content_types)):
            text_tokens = self.estimate(text, content_type, language)

            # Check if adding this text would exceed limit
            if current_tokens + text_tokens > max_tokens:
                break

            current_tokens += text_tokens
            batch_size = i + 1

        return max(1, batch_size)  # At least include one text
