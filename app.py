import os
import json
import threading
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox
import time
import sxcu
import pyperclip
from functools import partial
import requests
from typing import Union


def update_config(data):
    try:
        with open("SXCUUploader\\config.json", "w") as f:
            json.dump(data, f)
        return True
    except:
        return False


def get_data() -> Union[dict, bool]:
    try:
        with open("SXCUUploader/config.json", "r") as f:
            data = json.load(f)

        return data
    except Exception:
        return False


def get_sxcu_config(path) -> Union[dict, bool]:
    try:
        with open(path, "r") as f:
            sxcu_config = json.load(f)

        return sxcu_config
    except:
        return False


def check_config():
    if os.path.isdir("SXCUUploader"):
        if os.path.isfile("SXCUUploader\\config.json"):
            pass
        else:
            try:
                with open("SXCUUploader\\config.json", "w") as f:
                    data = {"sxcu": "/", "image": "/", "cp": None}
                    json.dump(data, f)
            except:
                pass
    else:
        try:
            os.mkdir("SXCUUploader")

            with open("SXCUUploader\\config.json", "w") as f:
                data = {"sxcu": "/", "image": "/", "cp": None}
                json.dump(data, f)
        except:
            print("Failed to create dir")


def get_config():
    try:
        with open("SXCUUploader\\config.json", "r") as f:
            data = json.load(f)
            return data
    except:
        return False


class App:
    def __init__(self, master):
        check_config()
        self.config = get_config() or {"sxcu": "/", "image": "/", "cp": None}
        self.master = master
        self.title_text = StringVar()
        self.noembed = IntVar()
        self.unlistedcoll = IntVar()
        self.privatecoll = IntVar()
        self.description_text = StringVar()
        self.color_text = StringVar()
        self.actual_image = None
        self.sxcu = None
        self.domain = None
        self.uploading = False
        self.delete_url = None

        tab_control = Notebook(master)
        # creating tabs
        main_tab = Frame(tab_control)
        config_tab = Frame(tab_control)
        collection_tab = Frame(tab_control)
        # self.about_tab = Frame(self.tab_control)

        # adding to the tab control
        tab_control.add(main_tab, text="Upload Image")
        tab_control.add(collection_tab, text="Create Collection")
        tab_control.add(config_tab, text="Config")
        # self.tab_control.add(self.about_tab, text="About")

        # packing tab
        tab_control.pack(expand=True, fill=BOTH)

        # Adding windows and pannels
        upload_window = PanedWindow(main_tab, orient="horizontal")
        upload_panel = LabelFrame(upload_window)

        config_window = PanedWindow(config_tab, orient="horizontal")
        config_panel = LabelFrame(config_window)

        coll_window = PanedWindow(collection_tab, orient="horizontal")
        coll_panel = LabelFrame(coll_window)

        # ================= Upload Tab =========================== #
        # title
        title_label = Label(upload_panel, text="Title : ")
        title_label.grid(column=0, row=0, sticky="e")

        title_entry = Entry(upload_panel, textvariable=self.title_text, width=32)
        title_entry.grid(column=1, row=0, pady=5, padx=(10, 0), columnspan=2)

        # description
        description_label = Label(upload_panel, text="Description : ")
        description_label.grid(column=0, row=1, sticky="e")

        description_entry = Text(upload_panel, height=4, width=24)
        description_entry.grid(
            column=1, row=1, pady=5, padx=(10, 0), sticky="nw", columnspan=2
        )

        # color
        color_label = Label(upload_panel, text="Color : ")
        color_label.grid(column=0, row=2, sticky="E")

        self.color_entry = Entry(upload_panel, textvariable=self.color_text, width=32)
        self.color_entry.grid(column=1, row=2, padx=(10, 0), pady=5, columnspan=2)

        # image
        image_label = Label(upload_panel, text="Image File : ")
        image_label.grid(column=0, row=4, sticky="E")

        self.image_button = Button(
            upload_panel, text="Select File", command=self.sel_image_file, width=32
        )
        self.image_button.grid(
            column=1, row=4, pady=5, padx=(10, 0), sticky="w", columnspan=2
        )

        # Noembed
        noembed_button = Checkbutton(
            upload_panel, text="No embed", variable=self.noembed
        )
        noembed_button.grid(
            column=1, row=5, sticky="w", padx=(10, 0), pady=5, columnspan=2
        )

        # Link
        link_text = Entry(upload_panel, text="", width=30)
        link_text.grid(row=7, columnspan=2, pady=5, padx=(10, 0), sticky="w")

        # Upload button
        self.upload_button = Button(
            upload_panel,
            text="Upload",
            command=partial(
                self.upload_thread,
                title_entry,
                description_entry,
                link_text,
                self.image_button,
            ),
            width=44,
        )
        self.upload_button.grid(columnspan=3, row=6, sticky="w", pady=5, padx=(10, 0))

        self.copy_button = Button(
            upload_panel, text="Copy", command=partial(self.copy, link_text)
        )
        self.copy_button.grid(column=2, row=7, sticky="w", pady=5, padx=(10, 0))

        self.delete_button = Button(
            upload_panel, text="Delete", command=self.delete, width=44, state='disabled'
        )
        self.delete_button.grid(column=0, columnspan=3, row=8, sticky="w", pady=5, padx=(10, 0))

        # ================= Config Tab =========================== #
        # sxcu
        sxcu_label = Label(config_panel, text="SXCU File : ")
        sxcu_label.grid(column=0, row=0, sticky="e")

        self.sxcu_button = Button(
            config_panel, text="Select File ", command=self.sel_sxcu_files, width=30
        )
        self.sxcu_button.grid(
            column=1, row=0, pady=(0, 5), padx=(10, 0), sticky="w", columnspan=2
        )

        self.collection_label = Label(config_panel, text="Collection ID : ")
        self.collection_label.grid(column=0, row=1, sticky="e")

        self.collection_entry = Entry(config_panel, text="", width=30)
        self.collection_entry.grid(column=1, row=1, padx=(10, 0), pady=5, sticky="e")

        self.collection_token_label = Label(config_panel, text="Coll. Token : ")
        self.collection_token_label.grid(column=0, row=2, sticky="e")

        self.collection_token_entry = Entry(config_panel, text="", width=30)
        self.collection_token_entry.grid(
            column=1, row=2, padx=(10, 0), pady=5, sticky="e"
        )

        sxcu_label = Label(config_panel, text="-> Configuration ")
        sxcu_label.grid(column=0, row=3, padx=(10, 0), pady=(30, 10), sticky="e")
        self.domain_label = Label(config_panel, text=f"Select a file to see config")
        self.domain_label.grid(column=0, columnspan=2, row=4, sticky="w")

        # ====================== Create collection =============#
        # title
        collname_label = Label(coll_panel, text="Name : ")
        collname_label.grid(column=0, row=0, sticky="e")

        collname_entry = Entry(coll_panel, width=32)
        collname_entry.grid(column=1, row=0, pady=5, padx=(10, 0), columnspan=2)

        # description
        cdescription_label = Label(coll_panel, text="Description : ")
        cdescription_label.grid(column=0, row=1, sticky="e")

        cdescription_entry = Text(coll_panel, height=4, width=24)
        cdescription_entry.grid(column=1, row=1, pady=5, padx=(10, 0), sticky="w")

        # Private
        private_button = Checkbutton(
            coll_panel, text="Private", variable=self.privatecoll
        )
        private_button.grid(
            column=1, row=2, sticky="w", padx=(10, 0), pady=5, columnspan=2
        )

        # Unlisted
        unlisted_button = Checkbutton(
            coll_panel, text="Unlisted", variable=self.unlistedcoll
        )
        unlisted_button.grid(
            column=1, row=3, sticky="w", padx=(10, 0), pady=5, columnspan=2
        )

        self.cc_button = Button(
            coll_panel,
            text="Create Collection",
            command=partial(
                self.create_collection_thread, collname_entry, cdescription_entry
            ),
            width=44,
        )
        self.cc_button.grid(columnspan=2, row=4, sticky="w", pady=5, padx=(10, 0))

        self.result_entry = Text(coll_panel, height=4, width=34)
        self.result_entry.grid(
            column=0, row=5, pady=5, padx=(10, 0), sticky="w", columnspan=2
        )

        # ====================== End Tabs ======================#

        footer_text = Label(tab_control, text="Developed by - Shahriyar#9770")
        footer_text.place(relx=0.5, rely=0.96, anchor="center")

        upload_window.add(upload_panel)
        upload_window.pack(fill="both", expand=True)

        config_window.add(config_panel)
        config_window.pack(fill="both", expand=True)

        coll_window.add(coll_panel)
        coll_window.pack(fill="both", expand=True)

    def copy_thread(self, link_text):
        data = link_text.get()
        if data:
            pyperclip.copy(data)
            self.copy_button.config(text="Copied")
            time.sleep(3)
            self.copy_button.config(text="Copy")
        else:
            pass

    def copy(self, link_text):
        my_thread = threading.Thread(target=self.copy_thread, args=(link_text,))
        # self.lock = threading.Lock()
        my_thread.daemon = True
        my_thread.start()

    def delete(self):
        my_thread = threading.Thread(target=self.delete_thread)
        # self.lock = threading.Lock()
        my_thread.daemon = True
        my_thread.start()


    def delete_thread(self):
        self.delete_button.config(text='Deleting...')
        try:
            res = requests.get(self.delete_url)
            if res.status_code == 200:
                messagebox.showinfo("Info", "Image deleted.")
            else:
                messagebox.showwarning("Warning", "Something went wrong.")
            self.delete_button.config(text='Delete')
            self.delete_button.config(state='disabled')
        except:
            self.delete_button.config(text='Delete')
            messagebox.showwarning("Error", "Something went wrong.")

    def create_collection_thread(self, collname_entry, cdescription_entry):
        my_thread = threading.Thread(
            target=self.create_collection, args=(collname_entry, cdescription_entry)
        )
        # self.lock = threading.Lock()
        my_thread.daemon = True
        my_thread.start()

    def create_collection(self, collname_entry, cdescription_entry):
        title = collname_entry.get().strip()
        description = cdescription_entry.get("1.0", END)
        private = True if self.privatecoll.get() == 1 else False
        unlisted = True if self.unlistedcoll.get() == 1 else False

        if not title:
            messagebox.showwarning("Error", "Title is requiered.")
        else:
            res = sxcu.SXCU().create_collection(
                title=title, desc=description, private=private, unlisted=unlisted
            )
            if res.status_code == 200:
                data = res.json()

                if private:
                    self.result_entry.delete("1.0", END)
                    self.result_entry.insert(
                        "1.0",
                        f"ID : {data['collection_id']} \nToken : {data['collection_token']}",
                    )
                else:
                    self.result_entry.delete("1.0", END)
                    self.result_entry.insert("1.0", f"ID : {data['collection_id']}")
            else:
                if res.status_code == 401:
                    messagebox.showwarning(
                        "Error",
                        "Collection is private but no collection token provided",
                    )

                if res.status_code == 403:
                    messagebox.showwarning("Error", "Invalid token in config file.")

                if res.status_code == 404:
                    messagebox.showwarning("Error", "Collection not found.")

                if res.status_code == 405:
                    messagebox.showwarning("Error", "Invalid request.")

                if res.status_code == 406:
                    messagebox.showwarning("Error", "Upload error.")

                if res.status_code == 409:
                    messagebox.showwarning("Error", "No file sent.")

                if res.status_code == 413:
                    messagebox.showwarning(
                        "Error", "Uploaded file is lasrger than 95 MB."
                    )

                if res.status_code == 415:
                    messagebox.showwarning("Error", "Uploaded file is not an image.")

                if res.status_code == 422:
                    messagebox.showwarning(
                        "Error",
                        "The OpenGraph properties JSON array could not be properly parsed, and is most likely malformed..",
                    )

                if res.status_code == 429:
                    messagebox.showwarning("Error", "You are being rate limited.")

                if res.status_code == 500:
                    messagebox.showwarning("Error", "Unknown error.")

    def upload_thread(self, title_entry, description_entry, link_text, image_button):
        my_thread = threading.Thread(
            target=self.upload,
            args=(title_entry, description_entry, link_text, image_button),
        )
        my_thread.daemon = True
        my_thread.start()

    def upload(self, title_entry, description_entry, link_text, image_button):
        self.uploading = True
        no_embed = False
        if self.noembed.get() == 1:
            no_embed = True

        if self.actual_image and self.sxcu:
            og = sxcu.og_properties(
                color=self.color_entry.get(),
                title=title_entry.get(),
                description=description_entry.get("1.0", END),
            )
            uploader = sxcu.SXCU(file_sxcu=self.sxcu)
            try:
                self.upload_button.config(text="Uploading...")
                self.upload_button.config(state="disabled")
                self.delete_button.config(state='disabled')
                res = uploader.upload_image(
                    file=self.actual_image,
                    og_properties=og,
                    noembed=no_embed,
                    collection=self.collection_entry.get(),
                    collection_token=self.collection_token_entry.get(),
                )

                if res.status_code == 200:
                    data = res.json()
                    print(data)
                    link_text.delete(0, END)
                    link_text.insert(0, data["url"])
                    self.delete_url = data['del_url']
                    self.delete_button.config(state='enabled')

                    title_entry.delete(0, END)
                    description_entry.delete("1.0", END)
                else:
                    if res.status_code == 401:
                        messagebox.showwarning(
                            "Error",
                            "Collection is private but no collection token provided",
                        )

                    if res.status_code == 403:
                        messagebox.showwarning("Error", "Invalid token in config file.")

                    if res.status_code == 404:
                        messagebox.showwarning("Error", "Collection not found.")

                    if res.status_code == 405:
                        messagebox.showwarning("Error", "Invalid request.")

                    if res.status_code == 406:
                        messagebox.showwarning("Error", "Upload error.")

                    if res.status_code == 409:
                        messagebox.showwarning("Error", "No file sent.")

                    if res.status_code == 413:
                        messagebox.showwarning(
                            "Error", "Uploaded file is lasrger than 95 MB."
                        )

                    if res.status_code == 415:
                        messagebox.showwarning(
                            "Error", "Uploaded file is not an image."
                        )

                    if res.status_code == 422:
                        messagebox.showwarning(
                            "Error",
                            "The OpenGraph properties JSON array could not be properly parsed, and is most likely malformed..",
                        )

                    if res.status_code == 429:
                        messagebox.showwarning("Error", "You are being rate limited.")

                    if res.status_code == 500:
                        messagebox.showwarning("Error", "Unknown error.")

                image_button.config(text="Select File")
                self.actual_image = None

                self.upload_button.config(text="Upload")
                self.upload_button.config(state="enabled")
            except Exception as e:
                self.upload_button.config(text="Upload")
                self.upload_button.config(state="enabled")

                if type(e).__name__ == 'ConnectionError':
                    messagebox.showwarning("Error", "Config is invalid or no network connection.")
                else:
                    messagebox.showwarning("Error", "Upload failed.")

            self.uploading = False
        else:
            if not self.sxcu:
                messagebox.showwarning(
                    "SXCU", "Please select an .sxcu file in Config tab"
                )
            elif not self.actual_image:
                messagebox.showwarning("Image", "Please select an image")

    def sel_image_file(self):
        image_file = filedialog.askopenfilename(
            initialdir=self.config["image"],
            title="Select file",
            filetypes=(("Image Files *.png, *.jpg, *.gif, *.jpeg, *.webp, *.bmp", ["*.png", "*.jpg", "*.gif", "*.jpeg", "*.webp", "*.bmp"]), ),
        )

        if image_file:
            filename = os.path.basename(image_file)
            idir = os.path.dirname(image_file) or "/"
            self.actual_image = image_file
            self.image_button.config(text=filename)
            self.config["image"] = idir

            try:
                with open("SXCUUploader\\config.json", "r") as f:
                    data = json.load(f)

                data["image"] = idir
                with open("SXCUUploader\\config.json", "w") as f:
                    json.dump(data, f)
            except Exception as e:
                print(e)

    def sel_sxcu_files(self):
        sxcu_file = filedialog.askopenfilename(
            initialdir=self.config["sxcu"],
            title="Select file",
            filetypes=(("SXCU Files *.sxcu", "*.sxcu"),),
        )


        if sxcu_file:
            filename = os.path.basename(sxcu_file)
            xdir = os.path.dirname(sxcu_file)
            self.sxcu = sxcu_file
            self.sxcu_button.config(text=filename)

            config_data = get_data()
            sxcu_data = get_sxcu_config(sxcu_file)

            print(config_data)
            print(sxcu_data)

            if config_data:
                config_data["sxcu"] = xdir
                config_data["cp"] = sxcu_file

            if sxcu_data:
                domain = sxcu_data["RequestURL"]

                if "Arguments" in sxcu_data:
                    privacy = "Private"
                else:
                    privacy = "Public"

                self.domain_label.config(
                    text=f"Domain : {'/'.join(domain.split('/')[:-1])} \nPrivacy: {privacy}"
                )

            if config_data and sxcu_data:
                update_config(config_data)
            else:
                if not sxcu_data:
                    messagebox.showerror(
                        "SXCU", "Not a valid config file. Try again"
                    )
                    self.sxcu = None
                    self.sxcu_button.config(text="Select File")
                else:
                    pass


def wanna():
    if messagebox.askyesno("Exit", "Sure to exit?"):
        root.destroy()


root = Tk()
try:
    root.iconbitmap("icon.ico")
except:
    pass

root.title("SXCU Uploader")
root.minsize(width=300, height=380)
root.resizable(height=False, width=False)
app = App(root)
root.protocol("WM_DELETE_WINDOW", wanna)
root.mainloop()
