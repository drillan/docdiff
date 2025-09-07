"""Sphinx project detection and configuration management."""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SphinxConfig:
    """Sphinx configuration extracted from conf.py."""

    project: str = ""
    author: str = ""
    copyright: str = ""
    version: str = ""
    release: str = ""

    # Source configuration
    source_suffix: List[str] = field(default_factory=lambda: [".rst"])
    master_doc: str = "index"
    exclude_patterns: List[str] = field(default_factory=list)

    # Language and i18n
    language: str = "en"
    locale_dirs: List[str] = field(default_factory=lambda: ["locale/"])
    gettext_compact: bool = False
    gettext_uuid: bool = False

    # Extensions
    extensions: List[str] = field(default_factory=list)

    # MyST configuration
    myst_enable_extensions: List[str] = field(default_factory=list)
    myst_heading_anchors: Optional[int] = None

    # Other settings
    html_theme: str = "alabaster"
    html_static_path: List[str] = field(default_factory=lambda: ["_static"])
    templates_path: List[str] = field(default_factory=lambda: ["_templates"])


@dataclass
class SphinxProject:
    """Represents a detected Sphinx documentation project."""

    root: Path
    config: SphinxConfig
    source_dir: Path
    build_dir: Path
    locale_dirs: List[Path] = field(default_factory=list)

    # Detected files
    conf_file: Optional[Path] = None
    makefile: Optional[Path] = None
    requirements_file: Optional[Path] = None

    # Content analysis
    doc_files: List[Path] = field(default_factory=list)
    has_myst: bool = False
    has_i18n: bool = False
    has_glossary: bool = False

    def get_source_files(self, suffix: Optional[str] = None) -> List[Path]:
        """Get all source documentation files.

        Args:
            suffix: Optional file suffix filter (e.g., '.rst', '.md')

        Returns:
            List of source file paths
        """
        if suffix:
            return [f for f in self.doc_files if f.suffix == suffix]
        return self.doc_files

    def get_build_path(self, builder: str = "html") -> Path:
        """Get the build output path for a specific builder.

        Args:
            builder: Sphinx builder name (html, gettext, etc.)

        Returns:
            Path to builder output directory
        """
        return self.build_dir / builder

    def get_locale_path(self, language: str) -> Optional[Path]:
        """Get the locale path for a specific language.

        Args:
            language: Language code (e.g., 'ja', 'fr')

        Returns:
            Path to language locale directory if it exists
        """
        for locale_dir in self.locale_dirs:
            lang_path = locale_dir / language / "LC_MESSAGES"
            if lang_path.exists():
                return lang_path
        return None


def parse_conf_py(conf_path: Path) -> SphinxConfig:
    """Parse Sphinx conf.py file to extract configuration.

    Args:
        conf_path: Path to conf.py file

    Returns:
        Extracted Sphinx configuration
    """
    config = SphinxConfig()

    if not conf_path.exists():
        return config

    try:
        content = conf_path.read_text(encoding="utf-8")

        # Parse as AST for safer extraction
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        value: Any = None

                        # Extract value based on type
                        if isinstance(node.value, ast.Constant):
                            value = node.value.value
                        elif isinstance(node.value, ast.List):
                            list_value: List[Any] = []
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant):
                                    list_value.append(elt.value)
                                elif isinstance(elt, ast.Str):  # Python < 3.8
                                    list_value.append(elt.s)
                            value = list_value
                        elif isinstance(node.value, ast.Dict):
                            dict_value: Dict[Any, Any] = {}
                            for k, v in zip(node.value.keys, node.value.values):
                                if isinstance(k, ast.Constant) and isinstance(
                                    v, ast.Constant
                                ):
                                    dict_value[k.value] = v.value
                            value = dict_value

                        # Map to config attributes
                        if value is not None:
                            if name == "project" and isinstance(value, str):
                                config.project = value
                            elif name == "author" and isinstance(value, str):
                                config.author = value
                            elif name == "copyright" and isinstance(value, str):
                                config.copyright = value
                            elif name == "version" and isinstance(value, str):
                                config.version = value
                            elif name == "release" and isinstance(value, str):
                                config.release = value
                            elif name == "source_suffix" and isinstance(
                                value, (str, list)
                            ):
                                config.source_suffix = (
                                    [value] if isinstance(value, str) else value
                                )
                            elif name == "master_doc" and isinstance(value, str):
                                config.master_doc = value
                            elif name == "language" and isinstance(value, str):
                                config.language = value
                            elif name == "locale_dirs" and isinstance(value, list):
                                config.locale_dirs = value
                            elif name == "extensions" and isinstance(value, list):
                                config.extensions = value
                            elif name == "html_theme" and isinstance(value, str):
                                config.html_theme = value
                            elif name == "exclude_patterns" and isinstance(value, list):
                                config.exclude_patterns = value
                            elif name == "myst_enable_extensions" and isinstance(
                                value, list
                            ):
                                config.myst_enable_extensions = value
                            elif name == "myst_heading_anchors" and isinstance(
                                value, int
                            ):
                                config.myst_heading_anchors = value

    except (SyntaxError, UnicodeDecodeError):
        # If we can't parse as Python, try regex fallback for basic values
        try:
            content = conf_path.read_text(encoding="utf-8")

            # Extract basic string values with regex
            patterns = {
                "project": r"project\s*=\s*['\"]([^'\"]+)['\"]",
                "author": r"author\s*=\s*['\"]([^'\"]+)['\"]",
                "language": r"language\s*=\s*['\"]([^'\"]+)['\"]",
                "master_doc": r"master_doc\s*=\s*['\"]([^'\"]+)['\"]",
                "html_theme": r"html_theme\s*=\s*['\"]([^'\"]+)['\"]",
            }

            for attr, pattern in patterns.items():
                match = re.search(pattern, content)
                if match:
                    setattr(config, attr, match.group(1))

            # Extract list values
            extensions_match = re.search(
                r"extensions\s*=\s*\[(.*?)\]", content, re.DOTALL
            )
            if extensions_match:
                ext_str = extensions_match.group(1)
                config.extensions = [
                    e.strip().strip("'\"")
                    for e in re.findall(r"['\"]([^'\"]+)['\"]", ext_str)
                ]

            source_suffix_match = re.search(
                r"source_suffix\s*=\s*(\[.*?\]|['\"].*?['\"])", content
            )
            if source_suffix_match:
                suffix_str = source_suffix_match.group(1)
                if suffix_str.startswith("["):
                    config.source_suffix = [
                        s.strip().strip("'\"")
                        for s in re.findall(r"['\"]([^'\"]+)['\"]", suffix_str)
                    ]
                else:
                    config.source_suffix = [suffix_str.strip("'\"")]

        except Exception:
            pass  # Return config with defaults

    return config


def detect_source_dir(project_path: Path) -> Path:
    """Detect the source directory for Sphinx documentation.

    Args:
        project_path: Root path of the project

    Returns:
        Path to source directory
    """
    # Common source directory patterns
    candidates = [
        project_path / "source",
        project_path / "docs",
        project_path / "doc",
        project_path,  # Root itself might be source
    ]

    for candidate in candidates:
        if candidate.exists():
            # Check for index file
            if (candidate / "index.rst").exists() or (candidate / "index.md").exists():
                return candidate
            # Check for conf.py in candidate
            if (candidate / "conf.py").exists():
                return candidate

    # Default to project root
    return project_path


def detect_locale_dirs(project_path: Path) -> List[Path]:
    """Detect locale directories in a Sphinx project.

    Args:
        project_path: Root path of the project

    Returns:
        List of locale directory paths
    """
    locale_dirs = []

    # Common locale directory locations
    candidates = [
        project_path / "locale",
        project_path / "_locale",
        project_path / "locales",
        project_path / "source" / "locale",
        project_path / "docs" / "locale",
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            # Check if it has language subdirectories
            for item in candidate.iterdir():
                if item.is_dir() and (item / "LC_MESSAGES").exists():
                    locale_dirs.append(candidate)
                    break

    return locale_dirs


def detect_sphinx_project(path: Path) -> Optional[SphinxProject]:
    """Detect and analyze Sphinx project structure.

    Args:
        path: Path to analyze for Sphinx project

    Returns:
        SphinxProject if detected, None otherwise
    """
    # Indicators of a Sphinx project with weights
    indicators: Dict[str, int] = {}

    # Check for conf.py (strongest indicator)
    conf_locations = [
        path / "conf.py",
        path / "source" / "conf.py",
        path / "docs" / "conf.py",
        path / "doc" / "conf.py",
    ]

    conf_file = None
    for conf_path in conf_locations:
        if conf_path.exists():
            conf_file = conf_path
            indicators["conf.py"] = 10
            break

    # If no conf.py, it's likely not a Sphinx project
    if not conf_file:
        return None

    # Parse configuration
    config = parse_conf_py(conf_file)

    # Determine source directory
    source_dir = conf_file.parent if conf_file else detect_source_dir(path)

    # Check for Makefile
    makefile = None
    if (path / "Makefile").exists():
        makefile = path / "Makefile"
        # Verify it's a Sphinx Makefile
        try:
            content = makefile.read_text()
            if "sphinx-build" in content or "SPHINXBUILD" in content:
                indicators["Makefile"] = 5
        except Exception:
            pass

    # Check for make.bat (Windows)
    if (path / "make.bat").exists():
        indicators["make.bat"] = 5

    # Check for build directory
    build_dir = path / "_build"
    if not build_dir.exists():
        build_dir = path / "build"
    if build_dir.exists():
        indicators["_build"] = 3

    # Check for index files
    if (source_dir / "index.rst").exists():
        indicators["index.rst"] = 8
    if (source_dir / "index.md").exists():
        indicators["index.md"] = 6

    # Check for requirements file
    requirements_file = None
    for req_name in [
        "requirements.txt",
        "doc-requirements.txt",
        "docs-requirements.txt",
    ]:
        req_path = path / req_name
        if req_path.exists():
            try:
                content = req_path.read_text()
                if "sphinx" in content.lower():
                    requirements_file = req_path
                    indicators["requirements"] = 3
                    break
            except Exception:
                pass

    # Calculate confidence score
    confidence = sum(indicators.values())

    # Require minimum confidence
    if confidence < 10:
        return None

    # Detect locale directories
    locale_dirs = detect_locale_dirs(path)
    if not locale_dirs and config.locale_dirs:
        # Try configured locale dirs
        for locale_dir in config.locale_dirs:
            locale_path = source_dir / locale_dir
            if locale_path.exists():
                locale_dirs.append(locale_path)

    # Collect documentation files
    doc_files: List[Path] = []
    for suffix in config.source_suffix:
        doc_files.extend(source_dir.rglob(f"*{suffix}"))

    # Detect MyST support
    has_myst = "myst_parser" in config.extensions or ".md" in config.source_suffix

    # Detect i18n setup
    has_i18n = bool(locale_dirs) or bool(config.locale_dirs)

    # Create project object
    project = SphinxProject(
        root=path,
        config=config,
        source_dir=source_dir,
        build_dir=build_dir,
        locale_dirs=locale_dirs,
        conf_file=conf_file,
        makefile=makefile,
        requirements_file=requirements_file,
        doc_files=doc_files,
        has_myst=has_myst,
        has_i18n=has_i18n,
    )

    # Quick scan for glossary
    for doc_file in doc_files[:10]:  # Sample first 10 files
        try:
            content = doc_file.read_text(encoding="utf-8")
            if ".. glossary::" in content or "```{glossary}" in content:
                project.has_glossary = True
                break
        except Exception:
            continue

    return project


def export_sphinx_config(project: SphinxProject) -> Dict[str, Any]:
    """Export Sphinx project configuration for JSON output.

    Args:
        project: SphinxProject to export

    Returns:
        Dictionary containing project configuration
    """
    return {
        "project_detected": True,
        "project_config": {
            "project_name": project.config.project,
            "author": project.config.author,
            "version": project.config.version,
            "language": project.config.language,
            "source_suffix": project.config.source_suffix,
            "master_doc": project.config.master_doc,
            "locale_dirs": project.config.locale_dirs,
            "extensions": project.config.extensions,
            "has_myst": project.has_myst,
            "has_i18n": project.has_i18n,
            "has_glossary": project.has_glossary,
        },
        "project_structure": {
            "root": str(project.root),
            "source_dir": str(project.source_dir),
            "build_dir": str(project.build_dir),
            "conf_file": str(project.conf_file) if project.conf_file else None,
            "makefile": str(project.makefile) if project.makefile else None,
            "locale_dirs": [str(d) for d in project.locale_dirs],
            "doc_file_count": len(project.doc_files),
        },
    }
