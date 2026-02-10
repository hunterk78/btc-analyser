import customtkinter as ctk
import requests
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class BitcoinMasterDash(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Bitcoin Transaction Analyser")
        self.geometry("1100x850")
        self.configure(fg_color="#0b0e14")

        self.header_frame = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=0)
        self.header_frame.pack(fill="x", side="top")

        self.title_lbl = ctk.CTkLabel(self.header_frame, text="BTC ADDRESS", font=("Orbitron", 24, "bold"), text_color="#00f2ff")
        self.title_lbl.pack(side="left", padx=30, pady=20)

        self.address_entry = ctk.CTkEntry(self.header_frame, placeholder_text="Enter Wallet Address...", 
                                          width=500, height=40, fg_color="#0d1117", border_color="#30363d")
        self.address_entry.pack(side="left", padx=20)

        self.search_btn = ctk.CTkButton(self.header_frame, text="ANALYZE", width=120, height=40, 
                                        fg_color="#00f2ff", text_color="#000", font=("Arial", 14, "bold"),
                                        command=self.start_analysis)
        self.search_btn.pack(side="left", padx=10)

        self.middle_container = ctk.CTkFrame(self, fg_color="transparent")
        self.middle_container.pack(fill="x", padx=30, pady=20)

        self.info_card = ctk.CTkFrame(self.middle_container, fg_color="#161b22", corner_radius=15)
        self.info_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.labels = {}
        self.setup_info_ui()

        self.chart_card = ctk.CTkFrame(self.middle_container, fg_color="#161b22", corner_radius=15, width=400)
        self.chart_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.canvas = None

        self.table_frame = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=15)
        self.table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        ctk.CTkLabel(self.table_frame, text="RECENT TRANSACTIONS", font=("Arial", 16, "bold"), text_color="#8b949e").pack(pady=10)
        
        self.tx_list = ctk.CTkTextbox(self.table_frame, fg_color="#0d1117", font=("Consolas", 13), text_color="#d1d5da")
        self.tx_list.pack(fill="both", expand=True, padx=20, pady=10)

    def setup_info_ui(self):
        fields = [
            ("Type", "type", "#58a6ff"),
            ("Balance BTC", "bal", "#3fb950"),
            ("Value USD", "usd", "#d29922"),
            ("Total TXs", "total", "#ffffff")
        ]
        for text, key, color in fields:
            f = ctk.CTkFrame(self.info_card, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=10)
            ctk.CTkLabel(f, text=text, font=("Arial", 14), text_color="#8b949e").pack(side="left")
            val = ctk.CTkLabel(f, text="---", font=("Consolas", 16, "bold"), text_color=color)
            val.pack(side="right")
            self.labels[key] = val

    def update_chart(self, in_val, out_val):
        if self.canvas: self.canvas.get_tk_widget().destroy()
        fig, ax = plt.subplots(figsize=(3, 3), facecolor='#161b22')
        ax.pie([max(in_val, 1), max(out_val, 1)], labels=['IN', 'OUT'], colors=['#3fb950', '#f85149'],
               autopct='%1.1f%%', startangle=90, textprops={'color': "w", 'size': 8},
               wedgeprops={'width': 0.4, 'edgecolor': '#161b22'})
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_card)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=5)

    def start_analysis(self):
        addr = self.address_entry.get().strip()
        if not addr: return
        
        self.search_btn.configure(text="...", state="disabled")
        try:
            data = requests.get(f"https://blockchain.info/rawaddr/{addr}").json()
            price = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()['bitcoin']['usd']
            
            bal = data['final_balance'] / 1e8
            self.labels['bal'].configure(text=f"{bal:.8f}")
            self.labels['usd'].configure(text=f"${bal*price:,.2f}")
            self.labels['total'].configure(text=str(data['n_tx']))
            self.labels['type'].configure(text="Native SegWit" if addr.startswith("bc1") else "Legacy/SegWit")

            self.tx_list.delete("0.0", "end")
            self.tx_list.insert("end", f"{'TIME':<20} | {'AMOUNT (BTC)':<15} | {'TX HASH'}\n")
            self.tx_list.insert("end", "-"*80 + "\n")
            
            in_count = 0
            for tx in data.get('txs', [])[:10]: 
                time_str = datetime.fromtimestamp(tx['time']).strftime('%Y-%m-%d %H:%M')
                val = sum(o['value'] for o in tx['out'] if o.get('addr') == addr) / 1e8
                if val > 0: in_count += 1
                self.tx_list.insert("end", f"{time_str:<20} | {val:>14.8f} | {tx['hash'][:20]}...\n")

            self.update_chart(in_count, data['n_tx'] - in_count)
            
        except:
            self.tx_list.insert("0.0", "Error: Data fetch failed.")
        
        self.search_btn.configure(text="ANALYZE", state="normal")

if __name__ == "__main__":
    app = BitcoinMasterDash()
    app.mainloop()