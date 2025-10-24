# Demo bỏ phiếu điện tử với thuật toán Rabin

## Cấu trúc thư mục
rabin_voting/
├── src/
│ ├── utils_rabin.py # Thư viện Rabin (số học, ký, verify, mã hóa/giải mã)
│ ├── voter.py # Mô phỏng cử tri
│ ├── authority.py # Mô phỏng kiểm phiếu
│ └── config.py # Cấu hình thư mục (keys, votes, ...)
├── keys/
│ ├── authority/ # Chứa khóa Authority (auth_priv.json, auth_pub.json)
│ └── voters/ # Chứa khóa voter (riêng từng voter)
├── votes/ # Chứa các file phiếu bầu (vote_xxx.json)
├── package_plain/ # (tùy chọn) chứa package gốc chưa mã hóa


## Hướng dẫn chạy thử

⚠️ Lưu ý: mọi lệnh đều chạy từ thư mục gốc `rabin_voting/`.

### Bước A — Sinh khóa cho Authority

python -c "import src.authority as authority; authority.authority_keygen(bits=2048)"



### Bước B — Voter: tạo phiếu,ký,mã hóa
python -c "import src.voter as voter; voter.voter_create('keys/authority/auth_pub.json', election_id='e-1', ballot_id='v1')"


### Bước C — Authority kiểm phiếu
Kiểm từng phiếu:

python -c "import src.authority as authority; authority.authority_decrypt_and_verify('keys/authority/auth_priv.json','votes/vote_v1.json')"
python -c "import src.authority as authority; authority.authority_decrypt_and_verify('keys/authority/auth_priv.json','votes/vote_v2.json')"

Kiểm tất cả phiếu trong folder:

python -c "import src.authority as authority; authority.authority_verify_all_in_folder('keys/authority/auth_priv.json','votes')"

Ghi chú
Tất cả cấu hình thư mục đều có thể chỉnh trong src/config.py.

Private key của Authority (auth_priv.json) và các voter private key trong keys/voters/ phải được giữ bí mật.