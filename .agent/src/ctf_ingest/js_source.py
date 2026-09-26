"""Isolated JS-capable fetcher for explicitly-provided URLs (discovery/fetch-only).

This module is separate from the static ingestion sources and does not change any existing
behavior. It renders a small, EXPLICIT list of URLs with a headless browser (Playwright
Chromium) to obtain content that the static text fetcher cannot see, records full provenance,
saves the rendered HTML/text as source artifacts, and detects (but never follows) links.

Guarantees:
- Fetches ONLY the URLs passed in. No crawling, no link following.
- Fails closed: if no JS renderer is available or a page cannot be rendered, it records an
  error result with no content and never falls back to inventing content.
- Never fabricates challenge names, descriptions, techniques, flags, or reasoning stages — it
  only stores what the browser actually rendered.
- Source content (rendered HTML/text) is kept distinct from any extracted knowledge; this
  module performs NO extraction into KnowledgeRecords.

Playwright is imported lazily so importing this module never affects environments (or the
static pipeline) that do not use it.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence
from urllib.parse import urlsplit


@dataclass(frozen=True)
class DiscoveredLink:
    href: str
    text: str
    classification: str  # internal_book | internal_other | external | anchor
    in_content: bool

    def to_dict(self) -> Dict[str, object]:
        return {
            "href": self.href,
            "text": self.text,
            "classification": self.classification,
            "in_content": self.in_content,
        }


@dataclass
class JsFetchResult:
    url: str
    ok: bool
    error: str = ""
    final_url: str = ""
    http_status: Optional[int] = None
    retrieved_at: str = ""
    content_sha256: str = ""
    rendered_html_bytes: int = 0
    rendered_text_len: int = 0
    renderer: str = ""
    renderer_version: str = ""
    browser_version: str = ""
    html_artifact: str = ""
    text_artifact: str = ""
    discovered_links: List[DiscoveredLink] = field(default_factory=list)
    writeup_link_candidates: int = 0

    def to_dict(self) -> Dict[str, object]:
        return {
            "url": self.url,
            "ok": self.ok,
            "error": self.error,
            "final_url": self.final_url,
            "http_status": self.http_status,
            "retrieved_at": self.retrieved_at,
            "content_sha256": self.content_sha256,
            "rendered_html_bytes": self.rendered_html_bytes,
            "rendered_text_len": self.rendered_text_len,
            "renderer": self.renderer,
            "renderer_version": self.renderer_version,
            "browser_version": self.browser_version,
            "html_artifact": self.html_artifact,
            "text_artifact": self.text_artifact,
            "writeup_link_candidates": self.writeup_link_candidates,
            "discovered_links": [link.to_dict() for link in self.discovered_links],
        }


def classify_link(href: str, page_url: str, *, in_content: bool = False) -> DiscoveredLink:
    """Classify a discovered anchor. Pure function (no I/O), for testability.

    - anchor:         same page, only a fragment (#...)
    - internal_book:  same host, path under /ctf-writeups/
    - internal_other: same host, other path
    - external:       different host
    """
    text = ""
    raw = href or ""
    if raw.startswith("#") or (raw.split("#", 1)[0] == page_url.split("#", 1)[0] and "#" in raw):
        return DiscoveredLink(href=raw, text=text, classification="anchor", in_content=in_content)
    page_host = urlsplit(page_url).netloc
    parts = urlsplit(raw)
    if not parts.netloc or parts.netloc == page_host:
        if parts.path.startswith("/ctf-writeups/"):
            cls = "internal_book"
        else:
            cls = "internal_other"
    else:
        cls = "external"
    return DiscoveredLink(href=raw, text=text, classification=cls, in_content=in_content)


def _is_writeup_candidate(link: DiscoveredLink, page_url: str) -> bool:
    """A same-book content link that points to an individual writeup page.

    Excludes: the page itself, and any ``index.html`` hub/landing page (event/nav indexes are
    not individual writeups). This is a generic structural rule, not a hardcoded allow-list.
    """
    if link.classification != "internal_book" or not link.in_content:
        return False
    normalized = link.href.split("#", 1)[0].rstrip("/")
    if normalized == page_url.split("#", 1)[0].rstrip("/"):
        return False
    path = urlsplit(normalized).path
    if not path.endswith(".html"):
        return False
    return path.rsplit("/", 1)[-1] != "index.html"


class RendererUnavailable(RuntimeError):
    """Raised when no JS renderer can be started (fail-closed)."""


def render_urls(
    urls: Sequence[str],
    out_dir: Path,
    *,
    timeout_ms: int = 45000,
    wait_until: str = "networkidle",
) -> List[JsFetchResult]:
    """Render ONLY the given URLs with Playwright Chromium and save source artifacts.

    Fails closed: if Playwright/the browser cannot start, raises ``RendererUnavailable``. A
    per-URL render error is recorded as ``ok=False`` with no content (never invented).
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        import playwright
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # noqa: BLE001 - fail closed
        raise RendererUnavailable(f"Playwright not importable: {exc}") from exc

    playwright_version = getattr(playwright, "__version__", "")
    if not playwright_version:
        try:
            from importlib.metadata import version as _pkg_version

            playwright_version = _pkg_version("playwright")
        except Exception:  # noqa: BLE001
            playwright_version = "unknown"
    results: List[JsFetchResult] = []

    try:
        pw = sync_playwright().start()
    except Exception as exc:  # noqa: BLE001 - fail closed
        raise RendererUnavailable(f"Playwright could not start: {exc}") from exc

    try:
        try:
            browser = pw.chromium.launch(headless=True)
        except Exception as exc:  # noqa: BLE001 - fail closed
            raise RendererUnavailable(f"Chromium could not launch: {exc}") from exc
        browser_version = browser.version
        for url in urls:
            results.append(
                _render_one(
                    browser,
                    url,
                    out_dir,
                    timeout_ms=timeout_ms,
                    wait_until=wait_until,
                    playwright_version=playwright_version,
                    browser_version=browser_version,
                )
            )
        browser.close()
    finally:
        pw.stop()
    return results


def _render_one(
    browser,
    url: str,
    out_dir: Path,
    *,
    timeout_ms: int,
    wait_until: str,
    playwright_version: str,
    browser_version: str,
) -> JsFetchResult:
    retrieved_at = datetime.now(timezone.utc).isoformat()
    page = browser.new_page()
    try:
        response = page.goto(url, wait_until=wait_until, timeout=timeout_ms)
        status = response.status if response is not None else None
        final_url = page.url
        html = page.content()
        try:
            text = page.inner_text("body")
        except Exception:  # noqa: BLE001
            text = ""
        links = _extract_links(page, final_url)
        slug = _slug(url)
        html_path = out_dir / f"{slug}.rendered.html"
        text_path = out_dir / f"{slug}.rendered.txt"
        html_path.write_text(html, encoding="utf-8")
        text_path.write_text(text, encoding="utf-8")
        candidates = sum(1 for link in links if _is_writeup_candidate(link, final_url))
        return JsFetchResult(
            url=url,
            ok=True,
            final_url=final_url,
            http_status=status,
            retrieved_at=retrieved_at,
            content_sha256=hashlib.sha256(html.encode("utf-8")).hexdigest(),
            rendered_html_bytes=len(html.encode("utf-8")),
            rendered_text_len=len(text),
            renderer="playwright-chromium",
            renderer_version=playwright_version,
            browser_version=browser_version,
            html_artifact=str(html_path),
            text_artifact=str(text_path),
            discovered_links=links,
            writeup_link_candidates=candidates,
        )
    except Exception as exc:  # noqa: BLE001 - fail closed for this URL
        return JsFetchResult(
            url=url,
            ok=False,
            error=f"{type(exc).__name__}: {exc}",
            retrieved_at=retrieved_at,
            renderer="playwright-chromium",
            renderer_version=playwright_version,
            browser_version=browser_version,
        )
    finally:
        page.close()


def _extract_links(page, final_url: str) -> List[DiscoveredLink]:
    # Anchors within the main content area (Zensical/Material uses .md-content), and all anchors.
    content_hrefs = set()
    try:
        content = page.eval_on_selector_all(
            ".md-content a[href], article a[href], main a[href]",
            "els => els.map(e => [e.href, (e.textContent||'').trim()])",
        )
    except Exception:  # noqa: BLE001
        content = []
    for href, _text in content:
        content_hrefs.add(href)
    try:
        allpairs = page.eval_on_selector_all(
            "a[href]", "els => els.map(e => [e.href, (e.textContent||'').trim()])"
        )
    except Exception:  # noqa: BLE001
        allpairs = []
    links: List[DiscoveredLink] = []
    seen = set()
    for href, text in allpairs:
        if href in seen:
            continue
        seen.add(href)
        link = classify_link(href, final_url, in_content=href in content_hrefs)
        links.append(DiscoveredLink(href=link.href, text=text, classification=link.classification, in_content=link.in_content))
    return links


def _slug(url: str) -> str:
    path = urlsplit(url).path.strip("/")
    return path.replace("/", "_").replace(".html", "") or "index"
