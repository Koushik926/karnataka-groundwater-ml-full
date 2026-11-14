"""download_papers.py

Helper script to fetch the remaining open-access papers listed in
``papers/TO_DOWNLOAD.txt``.  Paywalled papers are skipped (they must be
downloaded through the REVA library / campus network).

Usage::

    python scripts/download_papers.py [--out ../papers]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Papers that are freely available (open access).
FREE_PAPERS = {
    "01  Hanumantha et al., 2026": "https://doi.org/10.1007/s43832-026-00341-2",
    "03  Alkon et al., 2024": "https://doi.org/10.1088/1748-9326/ad34e5",
    "05  Halder et al., 2024": "https://doi.org/10.1186/s12302-024-00981-y",
    "08  Wang et al., 2024": "https://doi.org/10.2166/hydro.2024.226",
    "16  Mohanavelu et al., 2020": "https://doi.org/10.3390/w12113209",
}

# Papers that are behind a paywall – they are skipped by this script.
PAYWALLED_PAPERS = {
    "04  Boo et al., 2024": "https://doi.org/10.1016/j.watres.2024.121249",
    "09  Shakya et al., 2022": "https://doi.org/10.1016/j.gsd.2022.100825",
    "12  Jyolsna et al., 2021": "https://doi.org/10.1080/02626667.2021.1896719",
    "13  Malakar et al., 2021": "https://doi.org/10.1021/acsestengg.0c00238",
    "14  Saha et al., 2021": "https://doi.org/10.1016/j.jclepro.2021.128073",
    "18  Yadav et al., 2020": "https://doi.org/10.1016/j.scitotenv.2019.135539",
}


def _resolve_doi(doi: str) -> str:
    """Resolve a DOI to its final URL (following redirects)."""
    try:
        resp = requests.head(doi, allow_redirects=True, timeout=30)
        if resp.status_code == 200:
            return resp.url
    except requests.RequestException as exc:
        logger.warning("Could not resolve %s: %s", doi, exc)
    return doi


def _download_pdf(url: str, out_path: Path) -> bool:
    """Download a PDF, returning ``True`` on success."""
    try:
        resp = requests.get(url, timeout=120, stream=True)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")
        if "pdf" not in content_type.lower():
            logger.warning("URL %s returned %s – skipping.", url, content_type)
            return False
        with open(out_path, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                fh.write(chunk)
        logger.info("Saved %s", out_path)
        return True
    except requests.RequestException as exc:
        logger.warning("Failed to download %s: %s", url, exc)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Download missing papers.")
    parser.add_argument("--out", type=str, default="../papers",
                        help="Directory to save PDFs into.")
    parser.add_argument("--only-free", action="store_true",
                        help="Skip paywalled papers (default behaviour).")
    args = parser.parse_args()

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    papers = dict(FREE_PAPERS)
    if not args.only_free:
        papers.update(PAYWALLED_PAPERS)

    success = 0
    for name, doi in papers.items():
        safe_name = name.replace("/", "_").replace(" ", "_")
        out_path = out_dir / f"{safe_name}.pdf"
        if out_path.exists():
            logger.info("Already present: %s", out_path.name)
            success += 1
            continue
        url = _resolve_doi(doi)
        if _download_pdf(url, out_path):
            success += 1

    logger.info("Downloaded %d/%d papers.", success, len(papers))
    return 0 if success == len(papers) else 1


if __name__ == "__main__":
    sys.exit(main())