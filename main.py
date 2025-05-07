import threading
import customtkinter as ctk
from func import access_api, make_file_list, make_dir, save_file

FONT_TYPE = "meiryo"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.fonts = (FONT_TYPE, 18)
        self.progress_data = [
            [ctk.StringVar(), ctk.IntVar(value=1), ctk.IntVar()],
            [
                ctk.StringVar(),
                ctk.IntVar(value=1),
                ctk.IntVar(),
            ],
            [ctk.StringVar(), ctk.IntVar(), ctk.IntVar()],
            "",
        ]
        self.setup_form()

    def setup_form(self):
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.geometry("800x600")
        self.title("kemono downloader")

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.input_label = ctk.CTkLabel(
            self, text="kemono downloader", font=(FONT_TYPE, 36)
        )
        self.input_label.grid(row=0, column=0, padx=20, pady=20)

        self.input_frame = InputFrame(
            master=self, header_name="URL入力", progress_data=self.progress_data
        )
        self.input_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")


# 入力エリア
class InputFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name="InputFrame", progress_data, **kwargs):
        super().__init__(*args, **kwargs)
        self.fonts = (FONT_TYPE, 18)
        self.header_name = header_name
        self.progress_data = progress_data
        self.setup_form()

    # ウィジェット設置
    def setup_form(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.input_label = ctk.CTkLabel(
            self, text=self.header_name, font=(FONT_TYPE, 14)
        )
        self.input_label.grid(row=0, column=0, padx=20, sticky="w")

        self.input_url = ctk.CTkEntry(
            master=self,
            placeholder_text="ex)https://kemono.su/***/user/***",
            width=400,
            font=self.fonts,
        )
        self.input_url.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.start_button = ctk.CTkButton(
            master=self,
            text="ダウンロード",
            command=self.button_function,
            font=self.fonts,
        )
        self.start_button.grid(row=1, column=1, padx=10, pady=(0, 10))

    def button_function(self):
        app.info_frame = InfoFrame(
            master=app,
            progress_data=self.progress_data,
        )
        app.info_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        def run_download(url):
            self.progress_data[0][0].set("データ収集しています...")

            artist_data = access_api(url)
            artist_dir, artist_name = make_dir(artist_data)
            posts_count = artist_data["props"]["count"]
            posts_data = make_file_list(url, posts_count, artist_dir)

            self.progress_data[0][0].set(artist_name)

            save_file(posts_data, artist_dir, self.progress_data)

        t_1 = threading.Thread(target=run_download, args=(self.input_url.get(),))
        t_1.start()


# 進捗エリア
class InfoFrame(ctk.CTkFrame):
    def __init__(self, *args, progress_data, **kwargs):
        super().__init__(*args, **kwargs)
        self.fonts = (FONT_TYPE, 18)
        self.progress_data = progress_data
        self.setup_form()
        t_2 = threading.Thread(target=self.form_refresh)
        t_2.start()

    # ウィジェット設置
    def setup_form(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.FONT_SIZE = 18

        self.artist_name = ctk.CTkLabel(self, font=(FONT_TYPE, self.FONT_SIZE))
        self.artist_name.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")
        self.total_count = ctk.CTkLabel(self, font=(FONT_TYPE, self.FONT_SIZE))
        self.total_count.grid(row=0, column=1, padx=20, pady=(10, 0), sticky="e")
        self.total_bar = ctk.CTkProgressBar(self, width=400, height=8)
        self.total_bar.grid(
            row=1, column=0, padx=20, pady=(0, 10), sticky="ew", columnspan=2
        )

        self.post_name = ctk.CTkLabel(self, font=(FONT_TYPE, self.FONT_SIZE))
        self.post_name.grid(row=2, column=0, padx=20, sticky="w")
        self.post_count = ctk.CTkLabel(self, font=(FONT_TYPE, self.FONT_SIZE))
        self.post_count.grid(row=2, column=1, padx=20, sticky="e")
        self.post_bar = ctk.CTkProgressBar(self, width=400, height=8)
        self.post_bar.grid(
            row=3, column=0, padx=20, pady=(0, 10), sticky="ew", columnspan=2
        )

        self.file_name = ctk.CTkLabel(self, font=(FONT_TYPE, self.FONT_SIZE))
        self.file_name.grid(row=4, column=0, padx=20, sticky="w")
        self.file_count = ctk.CTkLabel(self, font=(FONT_TYPE, self.FONT_SIZE))
        self.file_count.grid(row=4, column=1, padx=20, sticky="e")
        self.file_bar = ctk.CTkProgressBar(self, width=400, height=8)
        self.file_bar.grid(
            row=5, column=0, padx=20, pady=(0, 10), sticky="ew", columnspan=2
        )

        self.error_report = ctk.CTkLabel(self, font=(FONT_TYPE, self.FONT_SIZE))
        self.error_report.grid(row=6, column=0, padx=20, pady=20, sticky="w")

    # 進捗状況更新
    def form_refresh(self):
        self.artist_name.configure(text=self.progress_data[0][0].get())
        self.total_count.configure(
            text=f"{self.progress_data[0][2].get()}/{self.progress_data[0][1].get()}"
        )
        self.total_bar.set(
            self.progress_data[0][2].get()
            * 0.01
            * (100 / (self.progress_data[0][1].get()))
        )

        self.post_name.configure(text=self.progress_data[1][0].get())
        self.post_count.configure(
            text=f"{self.progress_data[1][2].get()}/{self.progress_data[1][1].get()}"
        )
        self.post_bar.set(
            self.progress_data[1][2].get()
            * 0.01
            * (100 / (self.progress_data[1][1].get()))
        )

        self.file_name.configure(text=self.progress_data[2][0].get())
        self.file_count.configure(
            text=f"{self.progress_data[2][2].get()/(1024 * 1024):.2f}MB/{self.progress_data[2][1].get()/(1024 * 1024):.2f}MB"
        )
        self.file_bar.set(
            self.progress_data[2][2].get()
            * 0.01
            * (100 / (self.progress_data[2][1].get() - 1))
        )

        self.error_report.configure(text=self.progress_data[3])

        self.after(100, self.form_refresh)


if __name__ == "__main__":
    app = App()
    app.mainloop()
