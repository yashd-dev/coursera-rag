import os, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("PAPERFORGE_DATA", ROOT / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.environ.get("DATABASE_URL", "")
OPENCODE_BIN = os.environ.get("OPENCODE_BIN") or shutil.which("opencode") or "opencode"
# Owner-selected NVIDIA model. No authentication/provider fallback.
MODEL = os.environ.get(
    "PAPERFORGE_MODEL", "nvidia/nvidia/nemotron-3.5-lightning-30b-a3b"
)
# Candidate-only reviewer model for the span-review structured stage. Empty (default) = the same MODEL, behaviour unchanged.
# Format provider/model, e.g. nvidia/minimaxai/minimax-m3.1-flash. REVIEW_MODEL_OPTIONS is a JSON object merged into that model's OpenCode options.
REVIEW_MODEL = os.environ.get("PAPERFORGE_REVIEW_MODEL", "")
REVIEW_MODEL_OPTIONS = os.environ.get("PAPERFORGE_REVIEW_MODEL_OPTIONS", "")
# One embedding model per deployment. Chosen by the user: Voyage AI (hosted). "local" is an explicit opt-in dev mode only.
EMBED_PROVIDER = os.environ.get("PAPERFORGE_EMBED_PROVIDER", "voyage")
if EMBED_PROVIDER == "voyage":
    EMBED_MODEL = os.environ.get("PAPERFORGE_EMBED_MODEL", "voyage-4")
    EMBED_DIM = 1024
else:
    EMBED_MODEL = os.environ.get("PAPERFORGE_EMBED_MODEL", "BAAI/bge-small-en-v1.5")
    EMBED_DIM = 384
VOYAGE_API_KEY = os.environ.get("VOYAGE_API_KEY", "")
EMBED_TOKEN_BUDGET = int(
    os.environ.get("PAPERFORGE_EMBED_TOKEN_BUDGET", "2000000")
)  # per backend process; guards the free allowance
UNSTRUCTURED_API_KEY = os.environ.get("UNSTRUCTURED_API_KEY", "")
UNSTRUCTURED_API_URL = os.environ.get(
    "UNSTRUCTURED_API_URL", "https://transform.unstructured.io/api/v2"
)
UNSTRUCTURED_MODE = os.environ.get(
    "UNSTRUCTURED_MODE", "scanned"
)  # scanned | always | off
UNSTRUCTURED_STRATEGY = os.environ.get("UNSTRUCTURED_STRATEGY", "hi_res")
UNSTRUCTURED_MAX_PAGES_PER_RUN = int(
    os.environ.get("UNSTRUCTURED_MAX_PAGES_PER_RUN", "200")
)
MAX_SOURCES = int(os.environ.get("PAPERFORGE_MAX_SOURCES", "8"))
MAX_FIX_ITERATIONS = int(os.environ.get("PAPERFORGE_MAX_FIX_ITERATIONS", "4"))
PUBLIC_URL = os.environ.get("PAPERFORGE_PUBLIC_URL", "http://127.0.0.1:8000")
CONTACT = os.environ.get(
    "PAPERFORGE_CONTACT_EMAIL", "paperforge@example.org"
)  # sent to OpenAlex/arXiv as courtesy
TEMPLATES = {
    "ieee": {
        "label": "IEEE conference",
        "dir": "ieee",
        "csl": "ieee.csl",
        "bst": "IEEEtran",
    },
    "springer": {
        "label": "Springer LNCS",
        "dir": "springer",
        "csl": "springer-lecture-notes-in-computer-science.csl",
        "bst": "splncs04",
    },
}

# Fail-closed guard for hosted (potentially billable) calls. App-side ledger only: it counts usage made by THIS app's database,
# not usage on the provider account from elsewhere, and it cannot prevent provider-side billing. Check the provider dashboards.
HOSTED_CALLS = os.environ.get("PAPERFORGE_HOSTED_CALLS", "disabled") == "enabled"
VOYAGE_TOKEN_CAP = int(
    os.environ.get("PAPERFORGE_VOYAGE_TOKEN_CAP", "100000000")
)  # app lifetime; free allowance is 200M


# Direct hosted answering API, separate from OpenCode. No default provider/model.
ANSWER_BASE_URL = os.environ.get(
    "PAPERFORGE_ANSWER_BASE_URL", "https://integrate.api.nvidia.com/v1"
)
ANSWER_MODEL = os.environ.get(
    "PAPERFORGE_ANSWER_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b"
)
ANSWER_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
ANSWER_CALLS = os.environ.get("PAPERFORGE_ANSWER_CALLS", "disabled") == "enabled"

# Dedicated namespace. Initialization is an explicit operator action, never on a read.
DB_SCHEMA = os.environ.get("PAPERFORGE_DB_SCHEMA", "paperforge")
DB_INITIALIZE = os.environ.get("PAPERFORGE_DB_INITIALIZE", "disabled") == "enabled"

OPENALEX_API_KEY = os.environ.get("OPENALEX_API_KEY", "")
OPENALEX_CALLS = os.environ.get("PAPERFORGE_OPENALEX_CALLS", "disabled") == "enabled"

UNSTRUCTURED_FREE_PAGES_VERIFIED = (
    os.environ.get("PAPERFORGE_UNSTRUCTURED_FREE_VERIFIED", "disabled") == "enabled"
)
UNSTRUCTURED_PAGE_CAP = int(os.environ.get("PAPERFORGE_UNSTRUCTURED_PAGE_CAP", "100"))

FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "")
FIRECRAWL_CALLS = os.environ.get("PAPERFORGE_FIRECRAWL_CALLS", "disabled") == "enabled"
FIRECRAWL_FREE_VERIFIED = (
    os.environ.get("PAPERFORGE_FIRECRAWL_FREE_VERIFIED", "disabled") == "enabled"
)
FIRECRAWL_CREDIT_CAP = int(os.environ.get("PAPERFORGE_FIRECRAWL_CREDIT_CAP", "20"))
