"""
gui_voter.py
Giao diện (TKinter) cho Cử tri (Voter).
Đọc cấu hình bầu cử từ Authority và hiển thị lựa chọn.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, OptionMenu
from pathlib import Path
import sys, os, io, json

# Thêm thư mục GỐC (parent) vào path để import src, config
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
    # ... (Giữ nguyên hàm này)
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
        self.root.geometry("600x450")
        
        # Biến lưu trữ config
        self.election_config = {}
        self.selected_position = tk.StringVar(root)
        self.selected_choice = tk.StringVar(root)

        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ---- Khung nhập liệu ----
        self.form_frame = tk.LabelFrame(main_frame, text="Tạo phiếu bầu", padx=10, pady=10)
        self.form_frame.pack(fill=tk.X, pady=5)

        tk.Label(self.form_frame, text="Cuộc bầu cử:").grid(row=0, column=0, sticky='e', pady=5)
        self.election_id_label = tk.Label(self.form_frame, text="...", font=('Arial', 10, 'bold'))
        self.election_id_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        tk.Label(self.form_frame, text="Mã cử tri (Ballot ID):").grid(row=1, column=0, sticky='e', pady=5)
        self.ballot_id_entry = tk.Entry(self.form_frame, width=50)
        self.ballot_id_entry.insert(0, "voter-001")
        self.ballot_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        tk.Label(self.form_frame, text="Chọn Vị trí (Position):").grid(row=2, column=0, sticky='e', pady=5)
        self.position_menu = OptionMenu(self.form_frame, self.selected_position, "...")
        self.position_menu.config(width=45)
        self.position_menu.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        tk.Label(self.form_frame, text="Chọn Ứng viên (Choice):").grid(row=3, column=0, sticky='e', pady=5)
        self.choice_menu = OptionMenu(self.form_frame, self.selected_choice, "...")
        self.choice_menu.config(width=45)
        self.choice_menu.grid(row=3, column=1, padx=5, pady=5, sticky='w')


        # ---- Nút bấm ----
        self.create_button = tk.Button(main_frame, text="Tạo Phiếu Bầu (Ký và Mã hóa)", 
                                       command=self.run_create_vote, bg="#4CAF50", fg="white",
                                       font=('Arial', 10, 'bold'))
        self.create_button.pack(fill=tk.X, pady=10, ipady=5)

        # ---- Khung log output ----
        log_frame = tk.LabelFrame(main_frame, text="Log Output", padx=5, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10, bg="#f0f0f0")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Chuyển hướng stdout
        sys.stdout = StdoutRedirector(self.log_text)
        
        # Tải cấu hình khi khởi động
        self.load_election_config()

    def load_election_config(self):
        """Tải file config bầu cử do Authority tạo."""
        print("[INFO] Đang tải cấu hình bầu cử...")
        try:
            config_path = config.get_election_config_path()
            if not config_path.exists():
                raise FileNotFoundError("Chưa tìm thấy file election_config.json.")
            
            auth_pub_path = config.get_authority_pub_path()
            if not auth_pub_path.exists():
                raise FileNotFoundError("Chưa tìm thấy file auth_pub.json.")

            with open(config_path, 'r', encoding='utf-8') as f:
                self.election_config = json.load(f)
            
            # Lấy danh sách
            positions = self.election_config.get("positions", [])
            choices = self.election_config.get("choices", [])
            
            if not positions or not choices:
                 raise ValueError("File cấu hình không hợp lệ (thiếu positions/choices).")

            # Cập nhật UI
            self.election_id_label.config(text=self.election_config.get("election_id", "Lỗi"))
            
            # Cập nhật menu Vị trí
            self.selected_position.set(positions[0]) # Chọn mặc định
            self.position_menu['menu'].delete(0, 'end')
            for p in positions:
                self.position_menu['menu'].add_command(label=p, command=tk._setit(self.selected_position, p))
            
            # Cập nhật menu Ứng viên
            self.selected_choice.set(choices[0]) # Chọn mặc định
            self.choice_menu['menu'].delete(0, 'end')
            for c in choices:
                self.choice_menu['menu'].add_command(label=c, command=tk._setit(self.selected_choice, c))

            print("[OK] Tải cấu hình thành công.")
            self.create_button.config(state='normal') # Bật nút

        except Exception as e:
            print(f"[ERROR] Không thể tải cấu hình: {e}")
            print("[ERROR] Vui lòng chạy Authority GUI, sinh khóa (A) và lưu cấu hình (B) trước.")
            self.election_id_label.config(text="CHƯA CÓ CẤU HÌNH")
            self.create_button.config(state='disabled') # Tắt nút
            messagebox.showerror("Lỗi Cấu hình", 
                                 f"Không thể tải cấu hình bầu cử:\n{e}\n"
                                 "Vui lòng yêu cầu Authority 'Sinh khóa' và 'Lưu Cấu hình' trước.")

    def run_create_vote(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        print("--- [VOTER] Bắt đầu tạo phiếu... ---\n")
        
        auth_pub_path = config.get_authority_pub_path()
        ballot_id = self.ballot_id_entry.get()
        if not ballot_id.strip():
            messagebox.showerror("Lỗi", "Mã cử tri (Ballot ID) không được để trống.")
            print("[ERROR] Mã cử tri không được để trống.")
            return

        try:
            voter.voter_create(
                auth_pub_file=str(auth_pub_path),
                election_id=self.election_config.get("election_id"),
                ballot_id=ballot_id,
                # Lấy giá trị từ menu dropdown
                positions=self.selected_position.get(), 
                choices=self.selected_choice.get(),
            )
            print("\n--- [VOTER] Hoàn thành! ---")
            messagebox.showinfo("Thành công", f"Đã tạo phiếu bầu cho '{ballot_id}' thành công!")

        except Exception as e:
            print(f"\n[ERROR] Lỗi khi tạo phiếu: {e}")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")


if __name__ == "__main__":
    # Đảm bảo các thư mục cần thiết tồn tại
    config.ensure_structure()
    
    root = tk.Tk()
    app = VoterApp(root)
    # Khôi phục stdout khi đóng app
    def on_closing():
        sys.stdout = sys.__stdout__
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()