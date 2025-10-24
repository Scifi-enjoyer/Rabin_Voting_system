"""
voter.py
Phía cử tri:
- Sinh khóa voter
- Tạo ballot (JSON canonical)
- Ký ballot bằng khóa voter (Rabin)
- Mã hóa ballot bằng public key của Authority
- Tạo 1 file vote_<ballot_id>.json gồm:
    { "cipher_ballot": {...}, "voter_pub": {...}, "voter_sig": {...}, "meta": {...} }
"""

import time, json
from pathlib import Path
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config
import src.utils_rabin as rabin


def voter_create(auth_pub_file, election_id=None, ballot_id=None, positions=None, choices=None,
                voter_bits=2048, out_dir=".", filename=None):
    """
    Tạo phiếu và lưu 1 file duy nhất.
    - auth_pub_file: đường dẫn tới file JSON chứa {'n': ...}
    - out_dir: thư mục lưu file vote
    - filename: tên file đầu ra (nếu None -> vote_<ballot_id>.json)
    """
    auth_pub = rabin.load_json(auth_pub_file)
    # Sinh khóa voter
    voter_key = rabin.rabin_keygen(bits=voter_bits)
    voter_pub = {'n': voter_key['n']}

    # Tạo ballot
    ballot = {
        "election_id": election_id,
        "ballot_id": ballot_id or f"ballot-{int(time.time())}",
        "issue_time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "positions": positions or "N/A",
        "choices": choices or "N/A",
    }

    # Ký ballot (voter)
    voter_sig = rabin.rabin_sign_ballot(ballot, voter_key)

    # Mã hóa ballot bằng public key Authority
    ballot_bytes = rabin.canonical_json(ballot)
    cipher_ballot = rabin.rabin_encrypt_bytes(ballot_bytes, auth_pub)  # có thể raise nếu quá lớn

    # Tạo package đơn-file
    package = {
        "cipher_ballot": cipher_ballot,
        "voter_pub": voter_pub,
        "voter_sig": voter_sig,
        "meta": {
            "created_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime()),
        }
    }

    vote_path = config.get_vote_file_path(ballot['ballot_id'])
    voter_priv_path = config.get_voter_priv_path(ballot['ballot_id'])
    package_plain_path = config.get_package_plain_path(ballot['ballot_id'])

    # Lưu các file:
    rabin.save_json(package, vote_path)
    rabin.save_json(voter_key, voter_priv_path)
    rabin.save_json({'ballot': ballot, 'voter_pub': voter_pub, 'voter_sig': voter_sig}, package_plain_path)

    print(f"[OK] Phiếu đã tạo và lưu: {vote_path}")
    print(f"[Info] Khoá bí mật voter (giữ kín) -> {voter_priv_path}")
    return str(vote_path)
