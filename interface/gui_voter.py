"""
gui_voter.py
Giao diện (TKinter) cho Cử tri (Voter).
Cho phép CHỌN cuộc bầu cử trước khi vote.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, OptionMenu
from pathlib import Path
import sys, os, io, json

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

try:
    import config
    import src.voter as voter
except ImportError as e:
    messagebox.showerror("Lỗi Import", f"Không thể import module cần thiết: {e}\n"
                         "Hãy đảm bảo file này nằm ở thư mục gốc rabin_voting/.")
    sys.exit(1)


class StdoutRedirector(io.StringIO):
    # ... (Giữ nguyên) ...
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
    def flush(self):
        pass


class VoterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voter GUI (Cử tri)")
        self.root.geometry("600x550") # Tăng chiều cao
        
        # Biến lưu trữ config
        # --- SỬA LỖI .JSON ---
        # Chúng ta cần 1 dict để tra cứu: Tên Sạch -> Tên File
        self.display_name_to_filename = {} 
        # --- HẾT SỬA ---
        
        self.current_election_config = {} # Config của cuộc bầu cử đang chọn
        self.selected_election_file = tk.StringVar(root) # Biến này giờ sẽ lưu TÊN SẠCH
        self.selected_position = tk.StringVar(root)
        self.selected_choice = tk.StringVar(root)
        
        # --- KHI CHỌN ELECTION -> KÍCH HOẠT HÀM on_election_selected ---
        self.selected_election_file.trace("w", self.on_election_selected)

        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ---- KHUNG MỚI: CHỌN BẦU CỬ ----
        election_frame = tk.LabelFrame(main_frame, text="Chọn cấu hình", padx=10, pady=10)
        election_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(election_frame, text="Chọn cuộc bầu cử:").pack(side=tk.LEFT, padx=(0, 5))
        self.election_menu = OptionMenu(election_frame, self.selected_election_file, "...")
        self.election_menu.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=5)


        # ---- Khung nhập liệu (BƯỚC 2) ----
        self.form_frame = tk.LabelFrame(main_frame, text="Bỏ Phiếu", padx=10, pady=10)
        self.form_frame.pack(fill=tk.X, pady=5)
        
        self.form_frame.columnconfigure(1, weight=1) 

        tk.Label(self.form_frame, text="Người tạo phiếu:").grid(row=1, column=0, sticky='e', pady=5)
        self.ballot_id_entry = tk.Entry(self.form_frame) 
        self.ballot_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        tk.Label(self.form_frame, text="Vị trí:").grid(row=2, column=0, sticky='e', pady=5)
        self.position_menu = OptionMenu(self.form_frame, self.selected_position, "...")
        self.position_menu.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        tk.Label(self.form_frame, text="Lựa chọn:").grid(row=3, column=0, sticky='e', pady=5)
        self.choice_menu = OptionMenu(self.form_frame, self.selected_choice, "...")
        self.choice_menu.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        # ---- Nút bấm ----
        self.create_button = tk.Button(main_frame, text="Tạo Phiếu", 
                                       command=self.run_create_vote, bg="#4CAF50", fg="white",
                                       font=('Arial', 10, 'bold'))
        self.create_button.pack(fill=tk.X, pady=10, ipady=5)

        # ---- Khung log output ----
        log_frame = tk.LabelFrame(main_frame, text="Log Output", padx=5, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10, bg="#f0f0f0")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        sys.stdout = StdoutRedirector(self.log_text)
        
        # Tải cấu hình khi khởi động
        self.load_available_elections()
        # Khóa Bước 2 ban đầu
        self.set_voting_ui_state('disabled')


    def set_voting_ui_state(self, state):
        """Bật/Tắt các widget của Bước 2."""
        self.ballot_id_entry.config(state=state)
        self.position_menu.config(state=state)
        self.choice_menu.config(state=state)
        self.create_button.config(state=state)


    def load_available_elections(self):
        """Quét thư mục 'elections' và cập nhật menu (với tên sạch)."""
        print("[INFO] Đang tải danh sách các cuộc bầu cử...")
        
        # --- SỬA LỖI .JSON ---
        self.display_name_to_filename = {} # Xóa dict cũ
        # --- HẾT SỬA ---
        
        config.ELECTIONS_DIR.mkdir(exist_ok=True) # Đảm bảo thư mục tồn tại
        
        try:
            auth_pub_path = config.get_authority_pub_path()
            if not auth_pub_path.exists():
                raise FileNotFoundError("Chưa tìm thấy file auth_pub.json. Yêu cầu Authority sinh khóa.")
                
            config_files = sorted(list(config.ELECTIONS_DIR.glob("*.json")))
            
            for f_path in config_files:
                try:
                    with open(f_path, 'r', encoding='utf-8') as f:
                        cfg = json.load(f)
                        
                        # 1. Luôn tạo tên sạch (ví dụ: "lop-truong")
                        clean_name = f_path.name.rsplit('.json', 1)[0]
                        
                        # 2. Lấy "display_name" từ file, NẾU KHÔNG CÓ, 
                        #    dùng "clean_name" (tên sạch) làm dự phòng.
                        display_name = cfg.get("display_name", clean_name) 
                        
                        # --- SỬA LỖI .JSON ---
                        # Key là Tên Hiển Thị, Value là Tên File
                        self.display_name_to_filename[display_name] = f_path.name
                        # --- HẾT SỬA ---
                        
                except Exception:
                    pass # Bỏ qua file config lỗi
            
            menu = self.election_menu["menu"]
            menu.delete(0, "end")
            
            if not self.display_name_to_filename:
                menu.add_command(label="--- (Chưa có cuộc bầu cử nào) ---", state="disabled")
                self.selected_election_file.set("")
                print("[ERROR] Không tìm thấy cuộc bầu cử nào.")
                messagebox.showerror("Lỗi", "Không tìm thấy cấu hình bầu cử nào.\n"
                                     "Vui lòng yêu cầu Authority tạo và lưu cấu hình trước.")
            else:
                placeholder = "--- Chọn một cuộc bầu cử ---"
                self.selected_election_file.set(placeholder)
                menu.add_command(label=placeholder, command=tk._setit(self.selected_election_file, placeholder))
                
                # --- SỬA LỖI .JSON ---
                # Giờ đây, d_name là Tên Sạch
                for d_name in self.display_name_to_filename.keys():
                    # Hiển thị (label) = Tên Sạch
                    # Giá trị (value) = Tên Sạch
                    menu.add_command(label=d_name, command=tk._setit(self.selected_election_file, d_name))
                # --- HẾT SỬA ---
                    
                print(f"[OK] Tải thành công {len(self.display_name_to_filename)} cuộc bầu cử.")

        except Exception as e:
            print(f"[ERROR] Không thể tải danh sách bầu cử: {e}")
            self.set_voting_ui_state('disabled')
            messagebox.showerror("Lỗi Cấu hình", f"Không thể tải cấu hình bầu cử:\n{e}")

            

    def on_election_selected(self, *args):
        """Kích hoạt khi người dùng chọn 1 cuộc bầu cử từ menu."""
        # --- SỬA LỖI .JSON ---
        # 1. Biến này giờ là Tên Sạch (ví dụ: "testttt")
        display_name = self.selected_election_file.get()
        # --- HẾT SỬA ---
        
        if not display_name or display_name == "--- Chọn một cuộc bầu cử ---":
            self.set_voting_ui_state('disabled') # Khóa UI Bước 2
            self.current_election_config = {}
            return

        try:
            # --- SỬA LỖI .JSON ---
            # 2. Tra cứu Tên File thật (ví dụ: "testttt.json") từ Tên Sạch
            filename = self.display_name_to_filename[display_name]
            # --- HẾT SỬA ---
            
            print(f"[INFO] Đã chọn cuộc bầu cử (file: {filename})")
            
            config_path = config.ELECTIONS_DIR / filename
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            
            # Lưu config hiện tại
            self.current_election_config = cfg
            # Thêm election_id (tên file) vào config để dùng lúc vote
            self.current_election_config["election_id"] = filename.rsplit('.json', 1)[0]
            
            positions = cfg.get("positions", [])
            choices = cfg.get("choices", [])
            
            if not positions or not choices:
                 raise ValueError("File cấu hình không hợp lệ (thiếu positions/choices).")

            # Cập nhật menu Vị trí
            self.selected_position.set(positions[0])
            self.position_menu['menu'].delete(0, 'end')
            for p in positions:
                self.position_menu['menu'].add_command(label=p, command=tk._setit(self.selected_position, p))
            
            # Cập nhật menu Ứng viên
            self.selected_choice.set(choices[0])
            self.choice_menu['menu'].delete(0, 'end')
            for c in choices:
                self.choice_menu['menu'].add_command(label=c, command=tk._setit(self.selected_choice, c))

            print("[OK] Tải chi tiết bầu cử thành công.")
            self.set_voting_ui_state('normal') # Mở khóa UI Bước 2

        except Exception as e:
            print(f"[ERROR] Không thể tải chi tiết file {filename}: {e}")
            messagebox.showerror("Lỗi Tải file", f"Không thể đọc file {filename}:\n{e}")
            self.set_voting_ui_state('disabled')


    def run_create_vote(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        print("--- [VOTER] Bắt đầu tạo phiếu... ---\n")
        
        auth_pub_path = config.get_authority_pub_path()
        ballot_id = self.ballot_id_entry.get()
        if not ballot_id.strip():
            messagebox.showerror("Lỗi", "Người tạo phiếu (Ballot ID) không được để trống.")
            print("[ERROR] Mã cử tri không được để trống.")
            return

        try:
            voter.voter_create(
                auth_pub_file=str(auth_pub_path),
                # Lấy ID từ config đã tải
                election_id=self.current_election_config.get("election_id"), 
                ballot_id=ballot_id,
                positions=self.selected_position.get(), 
                choices=self.selected_choice.get(),
            )
            print("\n--- [VOTER] Hoàn thành! ---")
            messagebox.showinfo("Thành công", f"Đã tạo phiếu bầu cho '{ballot_id}' thành công!")

        except Exception as e:
            print(f"\n[ERROR] Lỗi khi tạo phiếu: {e}")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")


if __name__ == "__main__":
    # ... (Giữ nguyên) ...
    config.ensure_structure()
    root = tk.Tk()
    app = VoterApp(root)
    def on_closing():
        sys.stdout = sys.__stdout__
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()