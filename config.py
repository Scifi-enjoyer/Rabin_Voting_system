"""
config.py
File cấu hình cho project Rabin Voting (Python).
"""

import os
from pathlib import Path
import stat

# --------------------
# Các giá trị mặc định
# --------------------
PROJECT_ROOT = Path(__file__).resolve().parent

DEFAULT_DIRS = {
    "keys_dir": PROJECT_ROOT / "keys",
    "keys_authority": PROJECT_ROOT / "keys" / "authority",
    # --- THƯ MỤC MỚI ĐỂ CHỨA CÁC FILE CONFIG BẦU CỬ ---
    "elections_dir": PROJECT_ROOT / "elections",
    "keys_voters": PROJECT_ROOT / "keys" / "voters",
    "votes_dir": PROJECT_ROOT / "votes",
    "votes_approved": PROJECT_ROOT / "votes_approved",
    "votes_not_approved": PROJECT_ROOT / "votes_not_approved",
    "src_dir": PROJECT_ROOT / "src",
    "package_plain": PROJECT_ROOT / "package_plain",
    "logs_dir": PROJECT_ROOT / "logs",
}

# --------------------
# Hỗ trợ override bằng biến môi trường
# --------------------
def _env_path(varname, default_path):
    v = os.environ.get(varname)
    if v:
        return Path(v).expanduser().resolve()
    return Path(default_path).expanduser().resolve()

# Public config values (initial load)
KEYS_DIR = _env_path("RABIN_KEYS_DIR", DEFAULT_DIRS["keys_dir"])
KEYS_AUTHORITY_DIR = _env_path("RABIN_KEYS_AUTHORITY_DIR", DEFAULT_DIRS["keys_authority"])
# --- BIẾN MỚI ---
ELECTIONS_DIR = _env_path("RABIN_ELECTIONS_DIR", DEFAULT_DIRS["elections_dir"])
KEYS_VOTERS_DIR = _env_path("RABIN_KEYS_VOTERS_DIR", DEFAULT_DIRS["keys_voters"])
VOTES_DIR = _env_path("RABIN_VOTES_DIR", DEFAULT_DIRS["votes_dir"])
APPROVED_DIR = _env_path("RABIN_APPROVED_DIR", DEFAULT_DIRS["votes_approved"])
NOT_APPROVED_DIR = _env_path("RABIN_NOT_APPROVED_DIR", DEFAULT_DIRS["votes_not_approved"])
SRC_DIR = _env_path("RABIN_SRC_DIR", DEFAULT_DIRS["src_dir"])
PACKAGE_PLAIN_DIR = _env_path("RABIN_PACKAGE_PLAIN_DIR", DEFAULT_DIRS["package_plain"])
LOGS_DIR = _env_path("RABIN_LOGS_DIR", DEFAULT_DIRS["logs_dir"])

# File name patterns
AUTH_PRIV_FILENAME = "auth_priv.json"
AUTH_PUB_FILENAME = "auth_pub.json"
# --- BỎ ELECTION_CONFIG_FILENAME VÌ GIỜ DÙNG THƯ MỤC ---
VOTER_PRIV_TEMPLATE = "{ballot_id}_voter_priv.json"
VOTE_FILE_TEMPLATE = "vote_{ballot_id}.json"
PACKAGE_PLAIN_TEMPLATE = "package_plain_{ballot_id}.json"

# --------------------
# Helper functions
# --------------------

def ensure_structure(create_mode_dirs=0o750):
    """Tạo các thư mục cài đặt nếu chưa tồn tại."""
    dirs = {
        "PROJECT_ROOT": Path(PROJECT_ROOT),
        "KEYS_DIR": Path(KEYS_DIR),
        "KEYS_AUTHORITY_DIR": Path(KEYS_AUTHORITY_DIR),
        # --- THÊM THƯ MỤC MỚI ---
        "ELECTIONS_DIR": Path(ELECTIONS_DIR),
        "KEYS_VOTERS_DIR": Path(KEYS_VOTERS_DIR),
        "VOTES_DIR": Path(VOTES_DIR),
        "APPROVED_DIR": Path(APPROVED_DIR),
        "NOT_APPROVED_DIR": Path(NOT_APPROVED_DIR),
        "SRC_DIR": Path(SRC_DIR),
        "PACKAGE_PLAIN_DIR": Path(PACKAGE_PLAIN_DIR),
        "LOGS_DIR": Path(LOGS_DIR),
    }

    for name, p in dirs.items():
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
        try:
            p.chmod(create_mode_dirs)
        except Exception:
            pass
    return dirs

def reload_from_env():
    """Reload các biến cấu hình từ environment."""
    global KEYS_DIR, KEYS_AUTHORITY_DIR, ELECTIONS_DIR, KEYS_VOTERS_DIR, VOTES_DIR, APPROVED_DIR, NOT_APPROVED_DIR, SRC_DIR, PACKAGE_PLAIN_DIR, LOGS_DIR
    KEYS_DIR = _env_path("RABIN_KEYS_DIR", DEFAULT_DIRS["keys_dir"])
    KEYS_AUTHORITY_DIR = _env_path("RABIN_KEYS_AUTHORITY_DIR", DEFAULT_DIRS["keys_authority"])
    ELECTIONS_DIR = _env_path("RABIN_ELECTIONS_DIR", DEFAULT_DIRS["elections_dir"])
    KEYS_VOTERS_DIR = _env_path("RABIN_KEYS_VOTERS_DIR", DEFAULT_DIRS["keys_voters"])
    VOTES_DIR = _env_path("RABIN_VOTES_DIR", DEFAULT_DIRS["votes_dir"])
    APPROVED_DIR = _env_path("RABIN_APPROVED_DIR", DEFAULT_DIRS["votes_approved"])
    NOT_APPROVED_DIR = _env_path("RABIN_NOT_APPROVED_DIR", DEFAULT_DIRS["votes_not_approved"])
    SRC_DIR = _env_path("RABIN_SRC_DIR", DEFAULT_DIRS["src_dir"])
    PACKAGE_PLAIN_DIR = _env_path("RABIN_PACKAGE_PLAIN_DIR", DEFAULT_DIRS["package_plain"])
    LOGS_DIR = _env_path("RABIN_LOGS_DIR", DEFAULT_DIRS["logs_dir"])

def get_authority_priv_path():
    """Trả về Path tới file private authority."""
    return Path(KEYS_AUTHORITY_DIR) / AUTH_PRIV_FILENAME

def get_authority_pub_path():
    """Trả về Path tới file public authority."""
    return Path(KEYS_AUTHORITY_DIR) / AUTH_PUB_FILENAME

# --- BỎ HÀM get_election_config_path() ---
# (Vì giờ chúng ta dùng thư mục config.ELECTIONS_DIR)

# ... (các hàm get_... còn lại giữ nguyên) ...
def get_voter_priv_path(ballot_id):
    """Trả về Path file private voter theo ballot_id."""
    return Path(KEYS_VOTERS_DIR) / VOTER_PRIV_TEMPLATE.format(ballot_id=ballot_id)

def get_vote_file_path(ballot_id):
    """Trả về Path file vote theo ballot_id."""
    return Path(VOTES_DIR) / VOTE_FILE_TEMPLATE.format(ballot_id=ballot_id)

def get_package_plain_path(ballot_id):
    """Trả về Path file package_plain theo ballot_id."""
    return Path(PACKAGE_PLAIN_DIR) / PACKAGE_PLAIN_TEMPLATE.format(ballot_id=ballot_id)
# ...
try:
    ensure_structure()
except Exception:
    pass