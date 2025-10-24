"""
config.py
File cấu hình cho project Rabin Voting (Python).
- Định nghĩa các đường dẫn thư mục mặc định (keys, votes, src, package_plain)
- Hỗ trợ override bằng biến môi trường (ví dụ: RABIN_KEYS_DIR)
- Hàm ensure_structure() để tạo các thư mục cần thiết (và đặt quyền cơ bản)
- Hàm reload_from_env() để load lại config nếu cần (sau khi thay env)
"""

import os
from pathlib import Path
import stat

# --------------------
# Các giá trị mặc định (có thể chỉnh tay ở đây)
# --------------------
# Root của project (mặc định là thư mục chứa file config.py)
PROJECT_ROOT = Path(__file__).resolve().parent

# Thư mục con mặc định (relative to PROJECT_ROOT)
DEFAULT_DIRS = {
    "keys_dir": PROJECT_ROOT / "keys",
    "keys_authority": PROJECT_ROOT / "keys" / "authority",
    "keys_voters": PROJECT_ROOT / "keys" / "voters",
    "votes_dir": PROJECT_ROOT / "votes",
    "src_dir": PROJECT_ROOT / "src",
    "package_plain": PROJECT_ROOT / "package_plain",
    "approved_dir": PROJECT_ROOT / "votes_approved",
    "not_approved_dir": PROJECT_ROOT / "votes_not_approved",
}

# --------------------
# Hỗ trợ override bằng biến môi trường
# Ví dụ: export RABIN_KEYS_DIR=/some/secure/path
# --------------------
def _env_path(varname, default_path):
    v = os.environ.get(varname)
    if v:
        return Path(v).expanduser().resolve()
    return Path(default_path).expanduser().resolve()

# Public config values (initial load)
KEYS_DIR = _env_path("RABIN_KEYS_DIR", DEFAULT_DIRS["keys_dir"])
KEYS_AUTHORITY_DIR = _env_path("RABIN_KEYS_AUTHORITY_DIR", DEFAULT_DIRS["keys_authority"])
KEYS_VOTERS_DIR = _env_path("RABIN_KEYS_VOTERS_DIR", DEFAULT_DIRS["keys_voters"])
VOTES_DIR = _env_path("RABIN_VOTES_DIR", DEFAULT_DIRS["votes_dir"])
SRC_DIR = _env_path("RABIN_SRC_DIR", DEFAULT_DIRS["src_dir"])
PACKAGE_PLAIN_DIR = _env_path("RABIN_PACKAGE_PLAIN_DIR", DEFAULT_DIRS["package_plain"])
APPROVED_DIR = _env_path("RABIN_APPROVED_DIR", DEFAULT_DIRS["approved_dir"])
NOT_APPROVED_DIR = _env_path("RABIN_NOT_APPROVED_DIR", DEFAULT_DIRS["not_approved_dir"])

# File name patterns / templates
AUTH_PRIV_FILENAME = "auth_priv.json"
AUTH_PUB_FILENAME = "auth_pub.json"
ELECTION_CONFIG_FILENAME = "election_config.json"
VOTER_PRIV_TEMPLATE = "{ballot_id}_voter_priv.json"
VOTE_FILE_TEMPLATE = "vote_{ballot_id}.json"
PACKAGE_PLAIN_TEMPLATE = "package_plain_{ballot_id}.json"

# --------------------
# Helper functions
# --------------------

def ensure_structure(create_mode_dirs=0o750):
    """
    Tạo các thư mục cài đặt nếu chưa tồn tại.
    - create_mode_dirs (int): permission mode cho thư mục (octal), mặc định 0o750.
    Trả về dict chứa các Path cho tiện dụng.
    """
    dirs = {
        "PROJECT_ROOT": Path(PROJECT_ROOT),
        "KEYS_DIR": Path(KEYS_DIR),
        "KEYS_AUTHORITY_DIR": Path(KEYS_AUTHORITY_DIR),
        "KEYS_VOTERS_DIR": Path(KEYS_VOTERS_DIR),
        "VOTES_DIR": Path(VOTES_DIR),
        "SRC_DIR": Path(SRC_DIR),
        "PACKAGE_PLAIN_DIR": Path(PACKAGE_PLAIN_DIR),
        "APPROVED_DIR": Path(APPROVED_DIR),
        "NOT_APPROVED_DIR": Path(NOT_APPROVED_DIR),
    }

    for name, p in dirs.items():
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
        try:
            # set permission (posix only; on Windows this will be mostly no-op)
            p.chmod(create_mode_dirs)
        except Exception:
            # nếu không set được (ví dụ trên Windows) thì bỏ qua không crash
            pass
    return dirs

def reload_from_env():
    """Reload các biến cấu hình từ environment (gọi khi muốn thay đổi dynamic)."""
    global KEYS_DIR, KEYS_AUTHORITY_DIR, KEYS_VOTERS_DIR, VOTES_DIR, SRC_DIR, PACKAGE_PLAIN_DIR, APPROVED_DIR, NOT_APPROVED_DIR
    KEYS_DIR = _env_path("RABIN_KEYS_DIR", DEFAULT_DIRS["keys_dir"])
    KEYS_AUTHORITY_DIR = _env_path("RABIN_KEYS_AUTHORITY_DIR", DEFAULT_DIRS["keys_authority"])
    KEYS_VOTERS_DIR = _env_path("RABIN_KEYS_VOTERS_DIR", DEFAULT_DIRS["keys_voters"])
    VOTES_DIR = _env_path("RABIN_VOTES_DIR", DEFAULT_DIRS["votes_dir"])
    SRC_DIR = _env_path("RABIN_SRC_DIR", DEFAULT_DIRS["src_dir"])
    PACKAGE_PLAIN_DIR = _env_path("RABIN_PACKAGE_PLAIN_DIR", DEFAULT_DIRS["package_plain"])
    APPROVED_DIR = _env_path("RABIN_APPROVED_DIR", DEFAULT_DIRS["approved_dir"])
    NOT_APPROVED_DIR = _env_path("RABIN_NOT_APPROVED_DIR", DEFAULT_DIRS["not_approved_dir"])

def get_authority_priv_path():
    """Trả về Path tới file private authority (nên dùng để đọc/ghi)."""
    return Path(KEYS_AUTHORITY_DIR) / AUTH_PRIV_FILENAME

def get_authority_pub_path():
    """Trả về Path tới file public authority."""
    return Path(KEYS_AUTHORITY_DIR) / AUTH_PUB_FILENAME

def get_election_config_path():
    """Trả về Path tới file config bầu cử (do authority tạo)."""
    # Lưu chung thư mục với khóa public của authority
    return Path(KEYS_AUTHORITY_DIR) / ELECTION_CONFIG_FILENAME

def get_voter_priv_path(ballot_id):
    """Trả về Path file private voter theo ballot_id."""
    return Path(KEYS_VOTERS_DIR) / VOTER_PRIV_TEMPLATE.format(ballot_id=ballot_id)

def get_vote_file_path(ballot_id):
    """Trả về Path file vote theo ballot_id."""
    return Path(VOTES_DIR) / VOTE_FILE_TEMPLATE.format(ballot_id=ballot_id)

def get_package_plain_path(ballot_id):
    """Trả về Path file package_plain theo ballot_id."""
    return Path(PACKAGE_PLAIN_DIR) / PACKAGE_PLAIN_TEMPLATE.format(ballot_id=ballot_id)

# --------------------
# .gitignore helper
# --------------------
def create_gitignore():
    """
    Tạo file .gitignore trong PROJECT_ROOT với các dòng khuyến nghị.
    Nếu .gitignore đã tồn tại, sẽ thêm những dòng không tồn tại.
    """
    gitignore_path = PROJECT_ROOT / ".gitignore"
    lines = [
        "# Keys and sensitive data",
        "keys/",
        "package_plain/",
        "",
    ]
    if gitignore_path.exists():
        existing = gitignore_path.read_text(encoding='utf-8').splitlines()
    else:
        existing = []
    to_add = [ln for ln in lines if ln not in existing]
    if to_add:
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write("\n".join(to_add) + "\n")
    return gitignore_path

# --------------------
# Auto-run: khi import config, đảm bảo folder tồn (nhẹ nhàng)
# Bạn có thể comment dòng này nếu không muốn auto tạo lúc import.
# --------------------
try:
    ensure_structure()
except Exception:
    # không gây crash khi import
    pass
