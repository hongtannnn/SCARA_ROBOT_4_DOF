import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
import tkinter.messagebox as messagebox
import serial
import serial.tools.list_ports

# ==========================================
# BIẾN TOÀN CỤC & HÀNG ĐỢI LỆNH
# ==========================================
arduino = None
cmd_queue = []       
is_busy = False      
serial_buffer = ""   
current_j1 = 0.0     
current_j2 = 0.0     
emergency_stop_pending = False 

# ==========================================
# BỘ TỪ ĐIỂN FONT CHỮ GỐC (VECTOR FONT)
# ==========================================
VECTOR_FONT = {
    'A': [(0,0, 0.5,1), (0.5,1, 1,0), (0.2,0.5, 0.8,0.5)],
    'B': [(0,0, 0,1), (0,1, 0.8,1), (0.8,1, 1,0.75), (1,0.75, 0.8,0.5), (0.8,0.5, 0,0.5), (0.8,0.5, 1,0.25), (1,0.25, 0.8,0), (0.8,0, 0,0)],
    'C': [(1,0.2, 0.8,0), (0.8,0, 0.2,0), (0.2,0, 0,0.2), (0,0.2, 0,0.8), (0,0.8, 0.2,1), (0.2,1, 0.8,1), (0.8,1, 1,0.8)],
    'D': [(0,0, 0,1), (0,1, 0.8,1), (0.8,1, 1,0.8), (1,0.8, 1,0.2), (1,0.2, 0.8,0), (0.8,0, 0,0)],
    'E': [(1,0, 0,0), (0,0, 0,1), (0,1, 1,1), (0,0.5, 0.8,0.5)],
    'F': [(0,0, 0,1), (0,1, 1,1), (0,0.5, 0.8,0.5)],
    'G': [(1,1, 0,1), (0,1, 0,0), (0,0, 1,0), (1,0, 1,0.5), (0.5,0.5, 1,0.5)],
    'H': [(0,0, 0,1), (1,0, 1,1), (0,0.5, 1,0.5)],
    'I': [(0.5,0, 0.5,1), (0.25,0, 0.75,0), (0.25,1, 0.75,1)],
    'J': [(0,0.5, 0.5,0), (0.5,0, 1,0), (1,0, 1,1)],
    'K': [(0,0, 0,1), (1,1, 0,0.5), (0,0.5, 1,0)],
    'L': [(0,1, 0,0), (0,0, 1,0)],
    'M': [(0,0, 0,1), (0,1, 0.5,0.5), (0.5,0.5, 1,1), (1,1, 1,0)],
    'N': [(0,0, 0,1), (0,1, 1,0), (1,0, 1,1)],
    'O': [(0,0, 0,1), (0,1, 1,1), (1,1, 1,0), (1,0, 0,0)],
    'P': [(0,0, 0,1), (0,1, 1,1), (1,1, 1,0.5), (1,0.5, 0,0.5)],
    'Q': [(0,0, 0,1), (0,1, 1,1), (1,1, 1,0), (1,0, 0,0), (0.5,0.5, 1,-0.2)],
    'R': [(0,0, 0,1), (0,1, 1,1), (1,1, 1,0.5), (1,0.5, 0,0.5), (0,0.5, 1,0)],
    'S': [(0,0, 1,0), (1,0, 1,0.5), (1,0.5, 0,0.5), (0,0.5, 0,1), (0,1, 1,1)],
    'T': [(0,1, 1,1), (0.5,1, 0.5,0)],
    'U': [(0,1, 0,0), (0,0, 1,0), (1,0, 1,1)],
    'V': [(0,1, 0.5,0), (0.5,0, 1,1)],
    'W': [(0,1, 0.25,0), (0.25,0, 0.5,0.5), (0.5,0.5, 0.75,0), (0.75,0, 1,1)],
    'X': [(0,0, 1,1), (0,1, 1,0)],
    'Y': [(0,1, 0.5,0.5), (1,1, 0.5,0.5), (0.5,0.5, 0.5,0)],
    'Z': [(0,1, 1,1), (1,1, 0,0), (0,0, 1,0)],
    '0': [(0,0, 0,1), (0,1, 1,1), (1,1, 1,0), (1,0, 0,0), (0,0, 1,1)],
    '1': [(0.2,0.8, 0.5,1), (0.5,1, 0.5,0), (0.2,0, 0.8,0)],
    '2': [(0,1, 1,1), (1,1, 1,0.5), (1,0.5, 0,0.5), (0,0.5, 0,0), (0,0, 1,0)],
    '3': [(0,1, 1,1), (1,1, 1,0), (1,0, 0,0), (0,0.5, 1,0.5)],
    '4': [(0,1, 0,0.5), (0,0.5, 1,0.5), (1,1, 1,0)],
    '5': [(1,1, 0,1), (0,1, 0,0.5), (0,0.5, 1,0.5), (1,0.5, 1,0), (1,0, 0,0)],
    '6': [(1,1, 0,1), (0,1, 0,0), (0,0, 1,0), (1,0, 1,0.5), (1,0.5, 0,0.5)],
    '7': [(0,1, 1,1), (1,1, 0.5,0)],
    '8': [(0,0, 0,1), (0,1, 1,1), (1,1, 1,0), (1,0, 0,0), (0,0.5, 1,0.5)],
    '9': [(0,0, 1,0), (1,0, 1,1), (1,1, 0,1), (0,1, 0,0.5), (0,0.5, 1,0.5)],
    '-': [(0.2,0.5, 0.8,0.5)]
}

ACCENTS = {
    'SAC': [(0.5, 1.05, 0.7, 1.25)],
    'HUYEN': [(0.5, 1.05, 0.3, 1.25)],
    'HOI': [(0.3, 1.15, 0.5, 1.3), (0.5, 1.3, 0.7, 1.15), (0.7, 1.15, 0.5, 1.05)],
    'NGA': [(0.3, 1.1, 0.5, 1.25), (0.5, 1.25, 0.7, 1.1)],
    'NANG': [(0.4, -0.2, 0.6, -0.2)],
    'MU_A': [(0.2, 1.05, 0.5, 1.25), (0.5, 1.25, 0.8, 1.05)], 
    'MU_AW': [(0.2, 1.25, 0.5, 1.05), (0.5, 1.05, 0.8, 1.25)], 
    'RAU': [(0.8, 1.0, 1.0, 1.2), (1.0, 1.2, 0.9, 1.0)], 
    'GAC_D': [(-0.1, 0.5, 0.4, 0.5)], 
}

VIETNAMESE_MAP = {
    'Á': ('A', ['SAC']), 'À': ('A', ['HUYEN']), 'Ả': ('A', ['HOI']), 'Ã': ('A', ['NGA']), 'Ạ': ('A', ['NANG']),
    'Â': ('A', ['MU_A']), 'Ấ': ('A', ['MU_A', 'SAC']), 'Ầ': ('A', ['MU_A', 'HUYEN']), 'Ẩ': ('A', ['MU_A', 'HOI']), 'Ẫ': ('A', ['MU_A', 'NGA']), 'Ậ': ('A', ['MU_A', 'NANG']),
    'Ă': ('A', ['MU_AW']), 'Ắ': ('A', ['MU_AW', 'SAC']), 'Ằ': ('A', ['MU_AW', 'HUYEN']), 'Ẳ': ('A', ['MU_AW', 'HOI']), 'Ẵ': ('A', ['MU_AW', 'NGA']), 'Ặ': ('A', ['MU_AW', 'NANG']),
    'Đ': ('D', ['GAC_D']),
    'É': ('E', ['SAC']), 'È': ('E', ['HUYEN']), 'Ẻ': ('E', ['HOI']), 'Ẽ': ('E', ['NGA']), 'Ẹ': ('E', ['NANG']),
    'Ê': ('E', ['MU_A']), 'Ế': ('E', ['MU_A', 'SAC']), 'Ề': ('E', ['MU_A', 'HUYEN']), 'Ể': ('E', ['MU_A', 'HOI']), 'Ễ': ('E', ['MU_A', 'NGA']), 'Ệ': ('E', ['MU_A', 'NANG']),
    'Í': ('I', ['SAC']), 'Ì': ('I', ['HUYEN']), 'Ỉ': ('I', ['HOI']), 'Ĩ': ('I', ['NGA']), 'Ị': ('I', ['NANG']),
    'Ó': ('O', ['SAC']), 'Ò': ('O', ['HUYEN']), 'Ỏ': ('O', ['HOI']), 'Õ': ('O', ['NGA']), 'Ọ': ('O', ['NANG']),
    'Ô': ('O', ['MU_A']), 'Ố': ('O', ['MU_A', 'SAC']), 'Ồ': ('O', ['MU_A', 'HUYEN']), 'Ổ': ('O', ['MU_A', 'HOI']), 'Ỗ': ('O', ['MU_A', 'NGA']), 'Ộ': ('O', ['MU_A', 'NANG']),
    'Ơ': ('O', ['RAU']), 'Ớ': ('O', ['RAU', 'SAC']), 'Ờ': ('O', ['RAU', 'HUYEN']), 'Ở': ('O', ['RAU', 'HOI']), 'Ỡ': ('O', ['RAU', 'NGA']), 'Ợ': ('O', ['RAU', 'NANG']),
    'Ú': ('U', ['SAC']), 'Ù': ('U', ['HUYEN']), 'Ủ': ('U', ['HOI']), 'Ũ': ('U', ['NGA']), 'Ụ': ('U', ['NANG']),
    'Ư': ('U', ['RAU']), 'Ứ': ('U', ['RAU', 'SAC']), 'Ừ': ('U', ['RAU', 'HUYEN']), 'Ử': ('U', ['RAU', 'HOI']), 'Ữ': ('U', ['RAU', 'NGA']), 'Ự': ('U', ['RAU', 'NANG']),
    'Ý': ('Y', ['SAC']), 'Ỳ': ('Y', ['HUYEN']), 'Ỷ': ('Y', ['HOI']), 'Ỹ': ('Y', ['NGA']), 'Ỵ': ('Y', ['NANG']),
}

def create_ui_v2():
    global arduino, is_busy, serial_buffer, cmd_queue, current_j1, current_j2, emergency_stop_pending
    root = tk.Tk()
    root.title("Điều Khiển Robot SCARA - Phiên bản Tiếng Việt")
    root.geometry("1250x950") 
    root.configure(bg="#F2F2F2")
    
    font_title = tkfont.Font(family="Arial", size=22, weight="bold")
    font_subtitle = tkfont.Font(family="Arial", size=15, weight="bold")
    font_status = tkfont.Font(family="Arial", size=14, weight="bold")
    font_label = tkfont.Font(family="Arial", size=11)
    font_btn = tkfont.Font(family="Arial", size=10, weight="bold")
    
    BG_COLOR = "#F2F2F2"
    BTN_COLOR = "#0C2E59"
    BTN_TEXT = "#FFFFFF"

    def log_to_monitor(msg, tag="SYS"):
        try:
            serial_text.config(state=tk.NORMAL)
            if tag == "TX": prefix = ">> GỬI: "
            elif tag == "RX": prefix = "<< NHẬN: "
            elif tag == "ERR": prefix = "!! LỖI: "
            else: prefix = "-- HỆ THỐNG: "
            serial_text.insert(tk.END, prefix + str(msg) + "\n", tag)
            serial_text.see(tk.END)
            serial_text.config(state=tk.DISABLED)
        except Exception: pass

    def send_command(cmd, force=False):
        global arduino, is_busy
        if arduino and arduino.is_open:
            try:
                if force:
                    arduino.write((cmd + "\n").encode('utf-8'))
                    is_busy = True
                    log_to_monitor(cmd, "TX")
                elif not is_busy:
                    arduino.write((cmd + "\n").encode('utf-8'))
                    is_busy = True
                    log_to_monitor(cmd, "TX")
                else:
                    cmd_queue.append(cmd)
                    lbl_queue.config(text=f"Lệnh chờ: {len(cmd_queue)}")
            except Exception as e:
                log_to_monitor(f"Lỗi viết Serial: {e}", "ERR")
        else:
            messagebox.showwarning("Chưa kết nối", "Vui lòng kết nối Arduino trước khi gửi lệnh!")

    def read_serial():
        global arduino, is_busy, serial_buffer, current_j1, current_j2, emergency_stop_pending
        if arduino and arduino.is_open:
            try:
                while arduino.in_waiting > 0:
                    serial_buffer += arduino.read(arduino.in_waiting).decode('utf-8', errors='ignore')
                
                if '\n' in serial_buffer:
                    lines = serial_buffer.split('\n')
                    serial_buffer = lines[-1] 
                    
                    for line in lines[:-1]:
                        data = line.strip()
                        
                        if "STATUS," in data:
                            status_str = data.split("STATUS,")[1]
                            parts = status_str.split(',')
                            if len(parts) == 5:
                                x, y, z, j1, j2 = parts
                                lbl_x.config(text=f"X: {float(x):.1f} mm")
                                lbl_y.config(text=f"Y: {float(y):.1f} mm")
                                lbl_z.config(text=f"Z: {float(z):.1f} mm")
                                lbl_j1.config(text=f"J1: {float(j1):.1f}°")
                                lbl_j2.config(text=f"J2: {float(j2):.1f}°")
                                current_j1 = float(j1)
                                current_j2 = float(j2)
                            
                            is_busy = False
                            
                            if emergency_stop_pending:
                                emergency_stop_pending = False
                                try:
                                    z_up = float(entry_z_up.get())
                                    send_command(f"A,{current_j1},{current_j2},{z_up}", force=True)
                                    log_to_monitor("ĐÃ TỰ ĐỘNG NHẤC BÚT AN TOÀN!", "ERR")
                                except: pass
                            elif len(cmd_queue) > 0:
                                next_cmd = cmd_queue.pop(0)
                                lbl_queue.config(text=f"Lệnh chờ: {len(cmd_queue)}")
                                send_command(next_cmd)
                                
                        elif data:
                            log_to_monitor(data, "RX")
                            if "HE THONG DA KHOI DONG" in data:
                                is_busy = False
                                cmd_queue.clear()
                                lbl_queue.config(text="Lệnh chờ: 0")
                                messagebox.showerror("Lỗi Nguồn", "Phát hiện Arduino bị khởi động lại đột ngột!")
            except Exception as e: pass
        root.after(50, read_serial)

    # --- TOP: KẾT NỐI SERIAL ---
    top_frame = tk.Frame(root, bg=BG_COLOR)
    top_frame.pack(fill=tk.X, pady=10, padx=30)
    tk.Label(top_frame, text="BẢNG ĐIỀU KHIỂN ROBOT SCARA", font=font_title, bg=BG_COLOR, fg="#222222").pack(side=tk.LEFT)
    
    connect_frame = tk.Frame(top_frame, bg=BG_COLOR)
    connect_frame.pack(side=tk.RIGHT)
    tk.Label(connect_frame, text="Cổng COM:", font=font_label, bg=BG_COLOR).pack(side=tk.LEFT)
    port_cb = ttk.Combobox(connect_frame, values=[port.device for port in serial.tools.list_ports.comports()], width=10)
    port_cb.pack(side=tk.LEFT, padx=5)
    
    def connect_serial():
        global arduino, serial_buffer
        port = port_cb.get()
        if not port: return
        try:
            arduino = serial.Serial(port, 115200, timeout=0.1)
            serial_buffer = ""
            btn_connect.config(text="ĐÃ KẾT NỐI", bg="#27ae60", state=tk.DISABLED)
            btn_disconnect.config(state=tk.NORMAL)
            log_to_monitor(f"Đã mở cổng {port} thành công", "SYS")
            root.after(2000, lambda: send_command("H", force=True)) 
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def disconnect_serial():
        global arduino, is_busy
        if arduino and arduino.is_open:
            try:
                arduino.close()
                btn_connect.config(state=tk.NORMAL, bg="#d35400", text="KẾT NỐI")
                btn_disconnect.config(state=tk.DISABLED)
                log_to_monitor("Đã ngắt kết nối cổng COM", "SYS")
                is_busy = False
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể ngắt kết nối: {e}")

    btn_connect = tk.Button(connect_frame, text="KẾT NỐI", font=font_btn, bg="#d35400", fg=BTN_TEXT, command=connect_serial)
    btn_connect.pack(side=tk.LEFT, padx=(0, 5))

    btn_disconnect = tk.Button(connect_frame, text="NGẮT KẾT NỐI", font=font_btn, bg="#7f8c8d", fg=BTN_TEXT, command=disconnect_serial, state=tk.DISABLED)
    btn_disconnect.pack(side=tk.LEFT)

    # --- CHIA BỐ CỤC CHÍNH ---
    main_body = tk.Frame(root, bg=BG_COLOR)
    main_body.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

    # --- CỘT PHẢI: BẢNG TRẠNG THÁI ROBOT (HIỂN THỊ DỌC) ---
    right_sidebar = tk.Frame(main_body, bg=BG_COLOR, width=200)
    right_sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))

    status_frame = tk.LabelFrame(right_sidebar, text=" Trạng Thái ", font=font_subtitle, bg=BG_COLOR, fg="#16a085", padx=20, pady=15)
    status_frame.pack(fill=tk.X, anchor="n")
    
    lbl_x = tk.Label(status_frame, text="X: 0.0 mm", font=font_status, bg=BG_COLOR, fg="#c0392b"); lbl_x.pack(pady=10, anchor="w")
    lbl_y = tk.Label(status_frame, text="Y: 0.0 mm", font=font_status, bg=BG_COLOR, fg="#c0392b"); lbl_y.pack(pady=10, anchor="w")
    lbl_z = tk.Label(status_frame, text="Z: 0.0 mm", font=font_status, bg=BG_COLOR, fg="#2980b9"); lbl_z.pack(pady=10, anchor="w")
    ttk.Separator(status_frame, orient='horizontal').pack(fill=tk.X, pady=10)
    lbl_j1 = tk.Label(status_frame, text="J1: 0.0°", font=font_status, bg=BG_COLOR, fg="#8e44ad"); lbl_j1.pack(pady=10, anchor="w")
    lbl_j2 = tk.Label(status_frame, text="J2: 0.0°", font=font_status, bg=BG_COLOR, fg="#8e44ad"); lbl_j2.pack(pady=10, anchor="w")
    ttk.Separator(status_frame, orient='horizontal').pack(fill=tk.X, pady=10)
    lbl_queue = tk.Label(status_frame, text="Lệnh chờ: 0", font=font_label, bg=BG_COLOR, fg="#e67e22"); lbl_queue.pack(pady=5, anchor="w")

    # --- VÙNG TRÁI: ĐIỀU KHIỂN VÀ MÀN HÌNH SERIAL ---
    left_area = tk.Frame(main_body, bg=BG_COLOR)
    left_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    controls_frame = tk.Frame(left_area, bg=BG_COLOR)
    controls_frame.pack(fill=tk.X)

    col1 = tk.Frame(controls_frame, bg=BG_COLOR); col1.pack(side=tk.LEFT, fill=tk.Y, expand=True)
    col2 = tk.Frame(controls_frame, bg=BG_COLOR); col2.pack(side=tk.LEFT, fill=tk.Y, expand=True)
    col3 = tk.Frame(controls_frame, bg=BG_COLOR); col3.pack(side=tk.LEFT, fill=tk.Y, expand=True)

    # ==========================================
    # CỘT 1 (ĐIỀU KHIỂN JOG & GÓC)
    # ==========================================
    tk.Label(col1, text="Động Học Thuận", font=font_subtitle, bg=BG_COLOR, fg="#2980b9").pack(pady=(0, 10))
    
    # Điều khiển Jog
    jog_frame = tk.LabelFrame(col1, text=" Điều khiển từng bước (JOG) ", font=font_label, bg=BG_COLOR, padx=10, pady=10)
    jog_frame.pack(fill=tk.X, pady=10)

    def create_jog_group(parent, label_text, joint_id):
        frame = tk.Frame(parent, bg=BG_COLOR); frame.pack(pady=5)
        # Tăng width lên 6 để hiển thị trọn vẹn chữ và đơn vị
        tk.Label(frame, text=label_text, font=font_label, bg=BG_COLOR, width=6, anchor="w").grid(row=0, column=0, rowspan=2)
        entry_step = tk.Entry(frame, width=5, justify="center"); entry_step.insert(0, "5.0"); entry_step.grid(row=0, column=2, sticky="w")
        
        def jog(dir):
            try: 
                step_val = float(entry_step.get()) * dir
                send_command(f"J,{joint_id},{step_val}")
            except: pass
            
        tk.Button(frame, text="- GIẢM", font=font_btn, bg=BTN_COLOR, fg=BTN_TEXT, width=6, command=lambda: jog(-1)).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(frame, text="+ TĂNG", font=font_btn, bg=BTN_COLOR, fg=BTN_TEXT, width=6, command=lambda: jog(1)).grid(row=1, column=2, padx=5, pady=5)

    # Đã thêm đơn vị cho JOG control
    create_jog_group(jog_frame, "J1 (°)", 1)
    create_jog_group(jog_frame, "J2 (°)", 2)
    create_jog_group(jog_frame, "Z (mm)", 3)  

    # Góc tuyệt đối
    angle_frame = tk.LabelFrame(col1, text=" Nhập góc trực tiếp ", font=font_label, bg=BG_COLOR, padx=10, pady=10)
    angle_frame.pack(fill=tk.X, pady=10)
    
    # Đã thêm đơn vị cho nhãn nhập góc trực tiếp
    tk.Label(angle_frame, text="J1 (°):", bg=BG_COLOR).grid(row=0, column=0); entry_a1 = tk.Entry(angle_frame, width=8); entry_a1.grid(row=0, column=1, padx=5)
    tk.Label(angle_frame, text="J2 (°):", bg=BG_COLOR).grid(row=1, column=0); entry_a2 = tk.Entry(angle_frame, width=8); entry_a2.grid(row=1, column=1, padx=5)
    tk.Label(angle_frame, text="Z (mm):", bg=BG_COLOR).grid(row=2, column=0); entry_az = tk.Entry(angle_frame, width=8); entry_az.grid(row=2, column=1, padx=5)
    
    def send_absolute_angle():
        try:
            t1 = float(entry_a1.get())
            t2 = float(entry_a2.get())
            z = float(entry_az.get())
            send_command(f"A,{t1},{t2},{z}")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập đúng định dạng số!")

    tk.Button(angle_frame, text="ĐI TỚI", font=font_btn, bg="#27ae60", fg=BTN_TEXT, command=send_absolute_angle).grid(row=3, column=0, columnspan=2, pady=10, sticky="we")

    # ==========================================
    # CỘT 2 (ĐỘNG HỌC NGƯỢC)
    # ==========================================
    tk.Label(col2, text="Động Học Ngược", font=font_subtitle, bg=BG_COLOR, fg="#8e44ad").pack(pady=(0, 20))
    ik_frame = tk.LabelFrame(col2, text=" Di chuyển Tọa Độ XY ", font=font_label, bg=BG_COLOR, padx=15, pady=15)
    ik_frame.pack(fill=tk.X, pady=10)
    tk.Label(ik_frame, text="X (mm):", font=font_label, bg=BG_COLOR).grid(row=0, column=0, pady=10)
    entry_ik_x = tk.Entry(ik_frame, font=font_label, width=8, justify="center"); entry_ik_x.grid(row=0, column=1, padx=10)
    tk.Label(ik_frame, text="Y (mm):", font=font_label, bg=BG_COLOR).grid(row=1, column=0, pady=10)
    entry_ik_y = tk.Entry(ik_frame, font=font_label, width=8, justify="center"); entry_ik_y.grid(row=1, column=1, padx=10)

    def move_to_xyz():
        try: 
            x = float(entry_ik_x.get())
            y = float(entry_ik_y.get())
            send_command(f"P,{x},{y}")
        except: pass
            
    tk.Button(ik_frame, text="TỚI TỌA ĐỘ XY", font=font_btn, bg=BTN_COLOR, fg=BTN_TEXT, height=2, command=move_to_xyz).grid(row=2, column=0, columnspan=2, pady=15, sticky="we")

    # ==========================================
    # CỘT 3 (CÔNG CỤ VẼ PLOTTER)
    # ==========================================
    tk.Label(col3, text="Công Cụ Plotter", font=font_subtitle, bg=BG_COLOR, fg="#d35400").pack(pady=(0, 20))
    draw_box = tk.LabelFrame(col3, text=" Chọn chế độ vẽ ", font=font_label, bg=BG_COLOR, padx=15, pady=15)
    draw_box.pack(fill=tk.X)

    z_frame = tk.Frame(draw_box, bg=BG_COLOR); z_frame.pack(fill=tk.X, pady=(0, 10))
    tk.Label(z_frame, text="Z Nhấc an toàn:", bg=BG_COLOR).grid(row=0, column=0)
    entry_z_up = tk.Entry(z_frame, width=5, justify="center"); entry_z_up.insert(0, "20.0"); entry_z_up.grid(row=0, column=1, padx=5)
    tk.Label(z_frame, text=" Z Hạ mặt giấy:", bg=BG_COLOR).grid(row=0, column=2)
    entry_z_down = tk.Entry(z_frame, width=5, justify="center"); entry_z_down.insert(0, "0.0"); entry_z_down.grid(row=0, column=3, padx=5)

    draw_mode = tk.IntVar(value=3) 

    line_frame = tk.Frame(draw_box, bg=BG_COLOR)
    tk.Label(line_frame, text="X1:", bg=BG_COLOR).grid(row=0, column=0); entry_x1 = tk.Entry(line_frame, width=7); entry_x1.grid(row=0, column=1)
    tk.Label(line_frame, text=" Y1:", bg=BG_COLOR).grid(row=0, column=2); entry_y1 = tk.Entry(line_frame, width=7); entry_y1.grid(row=0, column=3)
    tk.Label(line_frame, text="X2:", bg=BG_COLOR).grid(row=1, column=0); entry_x2 = tk.Entry(line_frame, width=7); entry_x2.grid(row=1, column=1)
    tk.Label(line_frame, text=" Y2:", bg=BG_COLOR).grid(row=1, column=2); entry_y2 = tk.Entry(line_frame, width=7); entry_y2.grid(row=1, column=3)

    circle_frame = tk.Frame(draw_box, bg=BG_COLOR)
    tk.Label(circle_frame, text="Tâm X:", bg=BG_COLOR).grid(row=0, column=0); entry_cx = tk.Entry(circle_frame, width=7); entry_cx.grid(row=0, column=1)
    tk.Label(circle_frame, text=" Tâm Y:", bg=BG_COLOR).grid(row=0, column=2); entry_cy = tk.Entry(circle_frame, width=7); entry_cy.grid(row=0, column=3)
    tk.Label(circle_frame, text="Bán kính:", bg=BG_COLOR).grid(row=1, column=0); entry_r = tk.Entry(circle_frame, width=7); entry_r.grid(row=1, column=1)

    text_frame = tk.Frame(draw_box, bg=BG_COLOR)
    tk.Label(text_frame, text="Chữ:", bg=BG_COLOR).grid(row=0, column=0, sticky="e")
    entry_text = tk.Entry(text_frame, width=18); entry_text.insert(0, "HỒNG TÂN"); entry_text.grid(row=0, column=1, columnspan=3, sticky="w")
    tk.Label(text_frame, text="X Bắt đầu:", bg=BG_COLOR).grid(row=1, column=0, sticky="e"); entry_tx = tk.Entry(text_frame, width=7); entry_tx.grid(row=1, column=1)
    tk.Label(text_frame, text=" Y Bắt đầu:", bg=BG_COLOR).grid(row=1, column=2, sticky="e"); entry_ty = tk.Entry(text_frame, width=7); entry_ty.grid(row=1, column=3)
    tk.Label(text_frame, text="Cao chữ:", bg=BG_COLOR).grid(row=2, column=0, sticky="e"); entry_th = tk.Entry(text_frame, width=7); entry_th.insert(0, "20"); entry_th.grid(row=2, column=1)
    tk.Label(text_frame, text=" Cách chữ:", bg=BG_COLOR).grid(row=2, column=2, sticky="e"); entry_tspace = tk.Entry(text_frame, width=7); entry_tspace.insert(0, "4"); entry_tspace.grid(row=2, column=3)

    def toggle_draw_mode():
        line_frame.pack_forget(); circle_frame.pack_forget(); text_frame.pack_forget()
        if draw_mode.get() == 1: line_frame.pack(pady=10)
        elif draw_mode.get() == 2: circle_frame.pack(pady=10)
        elif draw_mode.get() == 3: text_frame.pack(pady=10)

    tk.Radiobutton(draw_box, text="Đường thẳng (Line)", variable=draw_mode, value=1, bg=BG_COLOR, command=toggle_draw_mode).pack(anchor="w")
    tk.Radiobutton(draw_box, text="Hình tròn (Circle)", variable=draw_mode, value=2, bg=BG_COLOR, command=toggle_draw_mode).pack(anchor="w")
    tk.Radiobutton(draw_box, text="Viết chữ Tiếng Việt", variable=draw_mode, value=3, bg=BG_COLOR, command=toggle_draw_mode).pack(anchor="w")
    toggle_draw_mode()

    # Các hàm nút bấm
    def stop_drawing():
        global cmd_queue, is_busy, emergency_stop_pending, current_j1, current_j2
        cmd_queue.clear()
        lbl_queue.config(text="Lệnh chờ: 0")
        if is_busy:
            emergency_stop_pending = True
            log_to_monitor("ĐÃ XÓA HÀNG ĐỢI! Chờ vẽ xong nét hiện tại để nhấc bút...", "ERR")
        else:
            try:
                z_up = float(entry_z_up.get())
                send_command(f"A,{current_j1},{current_j2},{z_up}", force=True)
                log_to_monitor("ĐÃ DỪNG VÀ NHẤC BÚT AN TOÀN!", "ERR")
            except: pass

    def homing_and_clear():
        global cmd_queue, emergency_stop_pending
        cmd_queue.clear()
        lbl_queue.config(text="Lệnh chờ: 0")
        emergency_stop_pending = False
        log_to_monitor("Đã xóa hàng đợi. Kích hoạt lệnh VỀ GỐC!", "SYS")
        send_command("H", force=True) 

    def send_draw():
        global is_busy
        try:
            z_up = float(entry_z_up.get())
            z_down = float(entry_z_down.get())
        except ValueError: 
            messagebox.showerror("Lỗi", "Vui lòng kiểm tra Z Nhấc và Z Hạ!")
            return

        if draw_mode.get() == 1:
            try: 
                x1, y1 = float(entry_x1.get()), float(entry_y1.get())
                x2, y2 = float(entry_x2.get()), float(entry_y2.get())
                send_command(f"D,{x1:.1f},{y1:.1f},{x2:.1f},{y2:.1f},{z_up:.1f},{z_down:.1f}") 
            except: pass
            
        elif draw_mode.get() == 2:
            try: 
                cx, cy, r = float(entry_cx.get()), float(entry_cy.get()), float(entry_r.get())
                send_command(f"C,{cx:.1f},{cy:.1f},{r:.1f},{z_up:.1f},{z_down:.1f}") 
            except: pass
            
        elif draw_mode.get() == 3:
            try:
                text_val = entry_text.get().upper()
                start_x, start_y = float(entry_tx.get()), float(entry_ty.get())
                height, spacing = float(entry_th.get()), float(entry_tspace.get())
                width = height * 0.6 
                current_x_offset = 0
                
                all_lines = []
                for char in text_val:
                    if char == ' ':
                        current_x_offset += width + spacing; continue
                    
                    lines = []
                    if char in VECTOR_FONT: 
                        lines = VECTOR_FONT[char].copy()
                    elif char in VIETNAMESE_MAP:
                        base_char, accents = VIETNAMESE_MAP[char]
                        lines = VECTOR_FONT[base_char].copy()
                        for acc in accents:
                            shift_y = 0.25 if (acc in ['SAC','HUYEN','HOI','NGA'] and ('MU_A' in accents or 'MU_AW' in accents)) else 0.0
                            shift_x = 0.15 if (acc in ['SAC','HUYEN','HOI','NGA'] and 'RAU' in accents) else 0.0
                            for stroke in ACCENTS[acc]:
                                lines.append((stroke[0] + shift_x, stroke[1] + shift_y, stroke[2] + shift_x, stroke[3] + shift_y))
                    
                    for line in lines:
                        lx1 = start_x + current_x_offset + (line[0] * width)
                        ly1 = start_y + (line[1] * height)
                        lx2 = start_x + current_x_offset + (line[2] * width)
                        ly2 = start_y + (line[3] * height)
                        all_lines.append((lx1, ly1, lx2, ly2))
                    
                    current_x_offset += width + spacing

                paths = []
                current_path = []
                for line in all_lines:
                    x1, y1, x2, y2 = line
                    if not current_path:
                        current_path = [(x1, y1), (x2, y2)]
                    else:
                        last_x, last_y = current_path[-1]
                        if abs(x1 - last_x) < 0.05 and abs(y1 - last_y) < 0.05:
                            current_path.append((x2, y2))
                        else:
                            paths.append(current_path)    
                            current_path = [(x1, y1), (x2, y2)]
                if current_path: paths.append(current_path)

                for path in paths:
                    cmd_queue.append(f"Z,{z_up:.1f}")                      
                    start_point = path[0]
                    cmd_queue.append(f"P,{start_point[0]:.1f},{start_point[1]:.1f}") 
                    cmd_queue.append(f"Z,{z_down:.1f}")                    
                    for point in path[1:]:
                        cmd_queue.append(f"L,{point[0]:.1f},{point[1]:.1f}") 
                cmd_queue.append(f"Z,{z_up:.1f}") 
                
                lbl_queue.config(text=f"Lệnh chờ: {len(cmd_queue)}")
                if not is_busy and len(cmd_queue) > 0:
                    send_command(cmd_queue.pop(0))

            except Exception as e: 
                messagebox.showerror("Lỗi", "Vui lòng nhập đủ thông số Viết Chữ!")

    action_frame = tk.Frame(draw_box, bg=BG_COLOR)
    action_frame.pack(pady=15)
    
    tk.Button(action_frame, text="BẮT ĐẦU VẼ", font=font_btn, bg="#27ae60", fg=BTN_TEXT, width=15, height=2, command=send_draw).grid(row=0, column=0, padx=5, pady=5)
    tk.Button(action_frame, text="DỪNG KHẨN CẤP", font=font_btn, bg="#c0392b", fg=BTN_TEXT, width=15, height=2, command=stop_drawing).grid(row=0, column=1, padx=5, pady=5)
    tk.Button(action_frame, text="VỀ GỐC TỌA ĐỘ (HOMING)", font=font_btn, bg="#8e44ad", fg=BTN_TEXT, height=2, command=homing_and_clear).grid(row=1, column=0, columnspan=2, pady=(5,0), sticky="we")

    # ==========================================
    # CỬA SỔ SERIAL MONITOR (DƯỚI CÙNG VÙNG TRÁI)
    # ==========================================
    monitor_frame = tk.LabelFrame(left_area, text=" Màn hình Serial Monitor ", font=font_subtitle, bg=BG_COLOR, fg="#2c3e50")
    monitor_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
    
    scrollbar = tk.Scrollbar(monitor_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    serial_text = tk.Text(monitor_frame, height=25, font=tkfont.Font(family="Consolas", size=10), bg="#1e1e1e", fg="#ffffff", state=tk.DISABLED, yscrollcommand=scrollbar.set)
    serial_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
    scrollbar.config(command=serial_text.yview)
    
    serial_text.tag_config("TX", foreground="#00a8ff")
    serial_text.tag_config("RX", foreground="#4cd137") 
    serial_text.tag_config("SYS", foreground="#fbc531")
    serial_text.tag_config("ERR", foreground="#ff4757") 

    root.after(50, read_serial)
    root.mainloop()

if __name__ == "__main__":
    create_ui_v2()