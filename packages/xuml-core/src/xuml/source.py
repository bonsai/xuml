"""Source adapters. Remote input is restricted to GitHub blob URLs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

MAX_SOURCE_BYTES = 1_000_000
FETCH_TIMEOUT_SECONDS = 10


class SourceError(ValueError):
    """Raised when source input cannot be safely resolved."""


@dataclass(frozen=True)
class Source:
    text: str
    name: str
    origin: str


def _github_blob_to_raw(url: str) -> tuple[str, str, str]:
    try:
        parsed = urlparse(url)
    except ValueError as exc:
        raise SourceError(f"Invalid source URL: {exc}") from exc

    if parsed.scheme != "https" or parsed.hostname != "github.com":
        raise SourceError("Remote sources must use an https://github.com/... URL.")
    if parsed.username or parsed.password or parsed.port:
        raise SourceError("Credentials and custom ports are not allowed in source URLs.")
    if parsed.query or parsed.fragment:
        raise SourceError("Source URLs must not include a query string or fragment.")

    parts = parsed.path.strip("/").split("/")
    if len(parts) < 5 or parts[2] != "blob":
        raise SourceError("Expected a GitHub file URL in the form /owner/repo/blob/ref/path.")

    owner, repo, _, ref = parts[:4]
    path = "/".join(parts[4:])
    if not owner or not repo or not ref or not path:
        raise SourceError("GitHub source URL must include owner, repository, ref, and file path.")
    decoded_path = unquote(path)
    if any(segment in {"", ".", ".."} for segment in decoded_path.split("/")):
        raise SourceError("Source URL contains an invalid path segment.")
    if not decoded_path.endswith(".py"):
        raise SourceError("Only Python (.py) source files are supported in this release.")

    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
    return raw_url, Path(decoded_path).name, url


def _read_limited(response) -> bytes:
    declared = response.headers.get("Content-Length")
    if declared:
        try:
            declared_size = int(declared)
        except ValueError:
            declared_size = None
        if declared_size is not None and declared_size > MAX_SOURCE_BYTES:
            raise SourceError(f"Source exceeds the {MAX_SOURCE_BYTES}-byte limit.")
    payload = response.read(MAX_SOURCE_BYTES + 1)
    if len(payload) > MAX_SOURCE_BYTES:
        raise SourceError(f"Source exceeds the {MAX_SOURCE_BYTES}-byte limit.")
    return payload


def load_source(value: str) -> Source:
    """Load a local Python file or a supported GitHub blob URL without executing it."""
    if value.startswith(("https://", "http://")):
        raw_url, name, origin = _github_blob_to_raw(value)
        request = Request(raw_url, headers={"User-Agent": "xuml/0.1", "Accept": "text/plain"})
        try:
            with urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response:
                payload = _read_limited(response)
        except SourceError:
            raise
        except HTTPError as exc:
            raise SourceError(f"GitHub source fetch failed (HTTP {exc.code}): {origin}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise SourceError(f"Could not fetch GitHub source: {exc}") from exc
        try:
            text = payload.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise SourceError("Source is not valid UTF-8 text.") from exc
        return Source(text=text, name=name, origin=origin)

    if "://" in value:
        raise SourceError("Unsupported source scheme; use a local path or an https://github.com/... URL.")

    path = Path(value).expanduser()
    try:
        if not path.is_file():
            raise SourceError(f"Source file does not exist or is not a file: {path}")
        if path.suffix.lower() != ".py":
            raise SourceError("Only Python (.py) source files are supported in this release.")
        if path.stat().st_size > MAX_SOURCE_BYTES:
            raise SourceError(f"Source exceeds the {MAX_SOURCE_BYTES}-byte limit: {path}")
        payload = path.read_bytes()
    except SourceError:
        raise
    except OSError as exc:
        raise SourceError(f"Could not read source file {path}: {exc}") from exc

    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise SourceError(f"Source is not valid UTF-8 text: {path}") from exc
    return Source(text=text, name=path.name, origin=str(path.resolve()))
