"""
gui_authority.py
Giao diện (TKinter) cho Authority (Bên kiểm phiếu).
Cho phép sinh khóa, thiết lập bầu cử, kiểm phiếu và XEM KẾT QUẢ.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
from pathlib import Path
import sys, os, io, json

# Thêm thư mục GỐC (parent) vào path để import src, config
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

try:
    import config
    import src.authority as authority
    import src.utils_rabin as rabin 
except ImportError as e:
    messagebox.showerror("Lỗi Import", f"Không thể import module cần thiết: {e}\n"
                         "Hãy đảm bảo file này nằm ở thư mục gốc rabin_voting/.")
    sys.exit(1)


class StdoutRedirector(io.StringIO):
    # ... (Giữ nguyên)
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.text_widget.config(state='disabled')
    def write(self, s):
        self.text_widget.config(state='normal')
        self.text_widget.insert(tk.END, s)
        self.text_widget.see(tk.END)
        self.text_widget.config(state='disabled')
        io.StringIO.write(self, s)
    def flush(selfT):
        pass


class AuthorityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Authority GUI (Bên kiểm phiếu)")
        self.root.geometry("600x700") # Tăng chiều cao

        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ---- Khung điều khiển (Bước A) ----
        setup_frame_A = tk.Frame(main_frame)
        setup_frame_A.pack(fill=tk.X, pady=5)
        self.keygen_button = tk.Button(setup_frame_A, text="Sinh khóa Authority", 
                                       command=self.run_keygen, bg="#E65100", fg="white",
                                       font=('Arial', 10, 'bold'))
        self.keygen_button.pack(fill=tk.X, expand=True, ipady=5)


        # ---- Khung Thiết lập (Bước B) ----
        setup_frame_B = tk.LabelFrame(main_frame, text="Thiết lập Bầu cử", padx=10, pady=10)
        setup_frame_B.pack(fill=tk.X, pady=5)
        # ... (Toàn bộ nội dung của khung này giữ nguyên)
        tk.Label(setup_frame_B, text="Election ID:").grid(row=0, column=0, sticky='e', pady=2)
        self.setup_election_id = tk.Entry(setup_frame_B, width=50)
        self.setup_election_id.insert(0, "")
        self.setup_election_id.grid(row=0, column=1, padx=5, pady=2, sticky='w')
        tk.Label(setup_frame_B, text="Các Vị trí (Positions):").grid(row=1, column=0, sticky='e', pady=2)
        self.setup_positions = tk.Entry(setup_frame_B, width=50)
        self.setup_positions.insert(0, "")
        self.setup_positions.grid(row=1, column=1, padx=5, pady=2, sticky='w')
        tk.Label(setup_frame_B).grid(row=1, column=2, sticky='w', padx=5)
        tk.Label(setup_frame_B, text="Các Ứng cử viên (Choices):").grid(row=2, column=0, sticky='e', pady=2)
        self.setup_choices = tk.Entry(setup_frame_B, width=50)
        self.setup_choices.insert(0, "")
        self.setup_choices.grid(row=2, column=1, padx=5, pady=2, sticky='w')
        tk.Label(setup_frame_B).grid(row=2, column=2, sticky='w', padx=5)
        self.save_config_button = tk.Button(setup_frame_B, text="Lưu Cấu hình Bầu cử", 
                                            command=self.save_election_config, bg="#00695C", fg="white")
        self.save_config_button.grid(row=3, column=1, pady=10, padx=5, sticky='w')
        self.load_election_config() # Tải config cũ (nếu có)

        # ---- Khung Hành động (Bước C & D) ----
        action_frame = tk.LabelFrame(main_frame, text="Xử lý và Xem Kết quả", padx=10, pady=10)
        action_frame.pack(fill=tk.X, pady=5)
        
        self.verify_button = tk.Button(action_frame, text="Kiểm phiếu (Xử lý thư mục 'votes/')", 
                                       command=self.run_verify_all, bg="#1E88E5", fg="white",
                                       font=('Arial', 10, 'bold'))
        self.verify_button.pack(fill=tk.X, expand=True, ipady=5, pady=(0, 5))
        
        # --- NÚT MỚI ---
        self.results_button = tk.Button(action_frame, text="Xem Kết Quả (Tổng hợp)",
                                        command=self.run_show_results, bg="#43A047", fg="white",
                                        font=('Arial', 10, 'bold'))
        self.results_button.pack(fill=tk.X, expand=True, ipady=5)
        # --- HẾT NÚT MỚI ---

        # ---- Khung log output ----
        log_frame = tk.LabelFrame(main_frame, text="Log Output", padx=5, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15, bg="#f0f0f0")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        sys.stdout = StdoutRedirector(self.log_text)
        
        print("Chào mừng Authority.")
        print("A. Sinh khóa (nếu chưa có).")
        print("B. Lưu Cấu hình Bầu cử.")
        print("C. Kiểm phiếu (xử lý các phiếu mới).")
        print("D. Xem Kết Quả (tổng hợp).")
        print("-" * 30)

    def clear_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')

    def run_keygen(self):
        # ... (Giữ nguyên)
        self.clear_log()
        print("--- [AUTH] Bắt đầu sinh khóa (2048 bit)... ---\n")
        try:
            authority.authority_keygen(bits=2048)
            print("\n--- [AUTH] Sinh khóa thành công! ---")
            messagebox.showinfo("Thành công", "Đã sinh khóa Authority thành công!")
        except Exception as e:
            print(f"\n[ERROR] Lỗi khi sinh khóa: {e}")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    def load_election_config(self):
        # ... (Giữ nguyên)
        try:
            config_path = config.get_election_config_path()
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                self.setup_election_id.delete(0, tk.END)
                self.setup_election_id.insert(0, cfg.get("election_id", ""))
                self.setup_positions.delete(0, tk.END)
                self.setup_positions.insert(0, ",".join(cfg.get("positions", [])))
                self.setup_choices.delete(0, tk.END)
                self.setup_choices.insert(0, ",".join(cfg.get("choices", [])))
        except Exception as e:
            print(f"[WARN] Không thể tải config bầu cử đã lưu: {e}")

    def save_election_config(self):
        # ... (Giữ nguyên)
        self.clear_log()
        print("\n--- [AUTH] Bắt đầu lưu cấu hình bầu cử... ---")
        try:
            positions_list = [p.strip() for p in self.setup_positions.get().split(',') if p.strip()]
            choices_list = [c.strip() for c in self.setup_choices.get().split(',') if c.strip()]
            if not positions_list or not choices_list:
                messagebox.showerror("Lỗi", "Vị trí và Ứng cử viên không được để trống.")
                print("[ERROR] Vị trí và Ứng cử viên không được để trống.")
                return
            config_data = { "election_id": self.setup_election_id.get(), "positions": positions_list, "choices": choices_list }
            config_path = config.get_election_config_path()
            rabin.save_json(config_data, str(config_path)) 
            print(f"Đã lưu cấu hình vào: {config_path}")
            print(json.dumps(config_data, ensure_ascii=False, indent=2))
            print("--- [AUTH] Lưu cấu hình thành công! ---")
            messagebox.showinfo("Thành công", f"Đã lưu cấu hình bầu cử vào:\n{config_path}")
        except Exception as e:
            print(f"\n[ERROR] Lỗi khi lưu cấu hình: {e}")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    def run_verify_all(self):
        # ... (Giữ nguyên)
        self.clear_log()
        print("--- [AUTH] Bắt đầu kiểm tra tất cả phiếu trong thư mục 'votes/'... ---\n")
        auth_priv_path = config.get_authority_priv_path()
        votes_dir = config.VOTES_DIR
        if not auth_priv_path.exists():
            messagebox.showerror("Lỗi", f"Không tìm thấy khóa bí mật Authority:\n{auth_priv_path}\n"
                             "Vui lòng 'Sinh khóa Authority' trước.")
            print(f"[ERROR] Không tìm thấy {auth_priv_path}")
            return
        if not votes_dir.exists():
             votes_dir.mkdir(exist_ok=True) # Tạo thư mục nếu chưa có
             
        # Kiểm tra xem thư mục có file không
        vote_files = list(votes_dir.glob("vote_*.json"))
        if not vote_files:
            print(f"[INFO] Thư mục '{votes_dir}' rỗng, không có phiếu nào để kiểm tra.")
            messagebox.showinfo("Thông báo", "Thư mục 'votes/' rỗng. Chưa có phiếu bầu mới.")
            return
        try:
            # Sửa lại hàm gọi:
            print(f"[INFO] Tìm thấy {len(vote_files)} phiếu mới. Bắt đầu xử lý...")
            valid_count = 0
            total_count = len(vote_files)
            
            # Phải duyệt thủ công vì authority_verify_all_in_folder không còn phù hợp
            # (do file bị xóa trong lúc duyệt)
            for f_path in vote_files:
                if authority.authority_decrypt_and_verify(str(auth_priv_path), str(f_path)):
                    valid_count += 1
            
            print("\n--- [AUTH] Hoàn tất kiểm phiếu! ---")
            print(f"[SUMMARY] Đã xử lý: {total_count} phiếu. Hợp lệ: {valid_count}. Không hợp lệ: {total_count - valid_count}.")
            
        except Exception as e:
            print(f"\n[ERROR] Lỗi khi kiểm phiếu: {e}")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    # --- HÀM MỚI ĐỂ XEM KẾT QUẢ ---
    def run_show_results(self):
        """
        Đọc file từ thư mục 'approved' và 'not_approved' để tổng hợp kết quả.
        Không cần private key.
        """
        self.clear_log()
        print("--- [AUTH] Đang tổng hợp kết quả bầu cử... ---")
        
        approved_count = 0
        rejected_count = 0
        
        # Xử lý phiếu HỢP LỆ (APPROVED)
        print("\n=== PHIẾU HỢP LỆ ===\n")
        config.APPROVED_DIR.mkdir(exist_ok=True) # Đảm bảo thư mục tồn tại
        approved_files = sorted(list(config.APPROVED_DIR.glob("*.json")))
        approved_count = len(approved_files)
        
        if not approved_files:
            print("(Không có phiếu hợp lệ nào)")
        else:
            for f in approved_files:
                try:
                    with open(f, 'r', encoding='utf-8') as rf:
                        data = json.load(rf)
                    
                    # Trích xuất thông tin theo yêu cầu
                    ballot_id = data.get('ballot_id', f.name)
                    position = data.get('positions', 'N/A')
                    choice = data.get('choices', 'N/A')
                    
                    print(f"  [File]: {f.name}")
                    print(f"  - ID Cử tri: {ballot_id}")
                    print(f"  - Lựa chọn: [{position}] -> [{choice}]\n")
                    
                except Exception as e:
                    print(f"[ERROR] Không thể đọc file kết quả {f.name}: {e}\n")

        # Xử lý phiếu KHÔNG HỢP LỆ (NOT_APPROVED)
        print("\n=== PHIẾU BỊ TỪ CHỐI ===\n")
        config.NOT_APPROVED_DIR.mkdir(exist_ok=True) # Đảm bảo thư mục tồn tại
        rejected_files = sorted(list(config.NOT_APPROVED_DIR.glob("*.json")))
        rejected_count = len(rejected_files)

        if not rejected_files:
            print("(Không có phiếu nào bị từ chối)")
        else:
            for f in rejected_files:
                try:
                    with open(f, 'r', encoding='utf-8') as rf:
                        data = json.load(rf)
                    
                    # Trích xuất thông tin theo yêu cầu
                    reason = data.get('error', 'Lỗi không xác định')
                    details = data.get('details', '')
                    
                    # Cố gắng lấy ID từ nhiều nguồn
                    ballot_id = data.get('ballot_id') # Từ ballot đã giải mã (nếu ký sai)
                    if not ballot_id:
                        ballot_id = data.get('original_filename', f.name) # Từ file JSON lỗi
                    
                    print(f"  [File]: {f.name}")
                    print(f"  - ID Cử tri: {ballot_id}")
                    print(f"  - Lý do từ chối: {reason}")
                    if details:
                        print(f"  - Chi tiết: {details}\n")
                    else:
                        print("") # Xuống dòng
                        
                except Exception as e:
                    print(f"[ERROR] Không thể đọc file lỗi {f.name}: {e}\n")

        # In tổng kết
        print("\n" + "=" * 30)
        print("TỔNG KẾT")
        print(f"  Phiếu hợp lệ: {approved_count}")
        print(f"  Phiếu bị từ chối: {rejected_count}")
        print(f"  TỔNG SỐ PHIẾU ĐÃ XỬ LÝ: {approved_count + rejected_count}")
        print("=" * 30)


if __name__ == "__main__":
    # ... (Giữ nguyên)
    config.ensure_structure()
    root = tk.Tk()
    app = AuthorityApp(root)
    def on_closing():
        sys.stdout = sys.__stdout__
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()