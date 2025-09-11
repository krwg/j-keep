import tkinter as tk
import customtkinter
import sqlite3
import json
from PIL import Image, ImageTk
import tkinter.messagebox as messagebox
import requests

#dev.krwg

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

CURRENT_VERSION = "1.1.0."

conn = None
cur = None
settings_window = None

current_note_id = None

font_sizes = {"Заголовок": 30, "Подзаголовок": 24, "Обычный": 18}

def db_start():
    global conn, cur
    try:
        conn = sqlite3.connect('notes.db')
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note TEXT,
                pinned INTEGER DEFAULT 0,
                formatted_text TEXT
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        customtkinter.CTkMessageBox(title="Ошибка", message="Ошибка подключения к базе данных.")

def save_note(event=None):
    global current_note_id
    if current_note_id:
        note = note_entry.get("1.0", tk.END).strip()
        if note:
            try:
                font_size = selected_font_size.get()
                formatted_data = {"text": note, "font_size": font_size}
                formatted_text = json.dumps(formatted_data)
                cur.execute("UPDATE notes SET note=?, formatted_text=? WHERE id=?", (note, formatted_text, current_note_id))
                conn.commit()
                update_notes_list()
                note_entry.delete("1.0", tk.END)
                selected_font_size.set("Обычный")
                note_entry.configure(font=("Arial", font_sizes["Обычный"]))
                current_note_id = None 
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении заметки: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Заметка пуста!")
    else:
        if event and event.state & 0x0004:
            note_entry.insert(tk.END, "\n")
        else:
            note = note_entry.get("1.0", tk.END).strip()
            if note:
                try:
                    font_size = selected_font_size.get()
                    formatted_data = {"text": note, "font_size": font_size}
                    formatted_text = json.dumps(formatted_data)
                    cur.execute("INSERT INTO notes (note, formatted_text) VALUES (?, ?)", (note, formatted_text))
                    conn.commit()
                    update_notes_list()
                    note_entry.delete("1.0", tk.END)
                    selected_font_size.set("Обычный")
                    note_entry.configure(font=("Arial", font_sizes["Обычный"]))
                except sqlite3.Error as e:
                    print(f"Ошибка сохранения заметки: {e}")
                    customtkinter.CTkMessageBox(title="Ошибка", message="Ошибка сохранения заметки.")
            else:
                customtkinter.CTkMessageBox(title="Предупреждение", message="Заметка пуста!")


def update_notes_list():
    global note_container_frame
    note_container_frame = customtkinter.CTkFrame(left_frame, fg_color="#333333")
    note_container_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
    note_container_frame.columnconfigure(0, weight=1)
    for i in range(100):
        note_container_frame.rowconfigure(i, weight=1)

    try:
        cur.execute("SELECT id, note, pinned, formatted_text FROM notes")
        notes = cur.fetchall()
        if notes:
            notes_label.configure(text="")
            instruction_label.grid_forget()
            for i, (note_id, note_text, pinned, formatted_text) in enumerate(notes):
                create_note_container(json.loads(formatted_text), i, note_id, pinned)
        else:
            notes_label.configure(text="Здесь будут ваши созданные заметки")
            instruction_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка", f"Ошибка при обновлении списка заметок: {e}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Непредвиденная ошибка: {e}")

#dev.krwg

def create_note_container(formatted_data, row_index, note_id, pinned):
    try:
        container = customtkinter.CTkFrame(note_container_frame, fg_color="transparent", corner_radius=5, border_width=2, border_color="#555555")
        container.grid(row=row_index, column=0, sticky="nsew", padx=10, pady=(5, 0))
        container.columnconfigure(0, weight=1)

        try:
            label = customtkinter.CTkLabel(container, text=formatted_data["text"], font=("Arial", font_sizes[formatted_data["font_size"]]), text_color="lightgray", anchor="w", justify="left", wraplength=300)
        except (KeyError, TypeError):
            label = customtkinter.CTkLabel(container, text=formatted_data["text"], font=("Arial", font_sizes["Обычный"]), text_color="lightgray", anchor="w", justify="left", wraplength=300)

        label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        container.rowconfigure(0, weight=1)

        menu = tk.Menu(label, tearoff=0, bg="#333333", fg="lightgray")
        menu.add_command(label="Удалить", command=lambda note_id=note_id: delete_note_by_id(note_id))
        menu.add_command(label="Изменить", command=lambda note_id=note_id: edit_note(note_id))

        if pinned:
            menu.add_command(label="Открепить", command=lambda note_id=note_id: toggle_pinned(note_id, False))
        else:
            menu.add_command(label="Закрепить", command=lambda note_id=note_id: toggle_pinned(note_id, True))

        label.bind("<Button-3>", lambda event, menu=menu: menu.post(event.x_root, event.y_root))
        label.bind("<Button-1>", lambda event, note_text=formatted_data["text"], note_id=note_id: copy_to_editor(note_text, note_id))

        if pinned:
            container.configure(fg_color="#444444")

        add_font_menu(label)
        return container
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка создания контейнера заметки: {e}")

def delete_note_by_id(note_id):
    try:
        cur.execute("DELETE FROM notes WHERE id=?", (note_id,))
        conn.commit()
        update_notes_list()
    except sqlite3.Error as e:
        print(f"Ошибка удаления заметки: {e}")
        customtkinter.CTkMessageBox(title="Ошибка", message="Ошибка удаления заметки.")

def copy_to_editor(note_text, note_id):
    global current_note_id
    note_entry.delete("1.0", tk.END)
    note_entry.insert("1.0", note_text)
    current_note_id = note_id

def toggle_fullscreen(event=None):
    root.attributes('-fullscreen', not root.attributes('-fullscreen'))

def open_settings():
    global settings_window, selected_section
    if settings_window is None or not settings_window.winfo_exists():
        settings_window = customtkinter.CTkToplevel(root)
        settings_window.title("Настройки")
        settings_window.geometry("800x600")
        settings_window.resizable(False, False)

        left_settings_column = customtkinter.CTkFrame(settings_window, fg_color="#333333")
        left_settings_column.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        right_settings_column = customtkinter.CTkFrame(settings_window, fg_color="#222222")
        right_settings_column.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        settings_sections = {
            "Главное": display_main,
            "О приложении": display_about
        }

        for i, (section_name, display_func) in enumerate(settings_sections.items()):
            button = customtkinter.CTkButton(left_settings_column, text=section_name,
                                             command=lambda func=display_func, rc=right_settings_column: select_section(func, rc),
                                             fg_color="#333333",
                                             hover_color=("gray80", "gray40"))
            button.grid(row=i, column=0, sticky="ew", pady=5)

        selected_section = display_about
        selected_section(right_settings_column)

        settings_window.columnconfigure(0, weight=1)
        settings_window.columnconfigure(1, weight=3)
        settings_window.protocol("WM_DELETE_WINDOW", close_settings)

def close_settings():
    global settings_window
    if conn:
        conn.close()
    settings_window.destroy()
    settings_window = None

def check_for_updates():
    try:
        response = requests.get("https://raw.githubusercontent.com/krwg/JustKeep/refs/heads/master/version.txt", timeout=5)
        response.raise_for_status()
        latest_version = response.text.strip()

        if latest_version > CURRENT_VERSION:
            messagebox.showinfo("Обновления", f"Доступно обновление до новой версии JKeep {latest_version}!
Вы можете обновиться, скачав новую версию https://github.com/krwg/JKeep_Desktop!")
        else:
            messagebox.showinfo("Обновления", "У вас последняя версия.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Ошибка", f"Ошибка проверки обновлений: {e}. Проверьте интернет соединение.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

def select_section(func, right_column):
    global selected_section
    selected_section = func
    clear_right_column(right_column)
    selected_section(right_column)

def clear_right_column(right_column):
    for widget in right_column.winfo_children():
        widget.grid_remove()
        widget.destroy()

def display_about(right_column):
    app_name_label = customtkinter.CTkLabel(right_column, text="JustKeep", font=("Arial", 20), text_color="lightgray")
    app_name_label.pack(pady=5)

    app_desc_label = customtkinter.CTkLabel(right_column, text="Быстрые заметки, без лишних сложностей.", font=("Arial", 14), text_color="lightgray")
    app_desc_label.pack(pady=2)

    author_label = customtkinter.CTkLabel(right_column, text="krwg. 2024", font=("Arial", 10), text_color="lightgray")
    author_label.pack(pady=5)

    version_label = customtkinter.CTkLabel(right_column, text=f"Версия: 1.1 Moonstone", font=("Arial", 12))
    version_label.pack(pady=5)

    check_updates_button = customtkinter.CTkButton(right_column, text="Проверить обновления", command=check_for_updates, fg_color=("gray70", "gray30"), hover_color=("gray80", "gray40"))
    check_updates_button.pack(pady=5)

def display_main(right_column):
    main_label = customtkinter.CTkLabel(right_column, text="В разработке, ожидайте в новой версии", font=("Arial", 12))
    main_label.pack(pady=10)

def add_font_menu(widget):
    font_sizes = {"Заголовок": 30, "Подзаголовок": 24, "Обычный": 18}
    selected_font_size = tk.StringVar(widget.master, "Обычный")

    def change_font_size(size):
        try:
            widget.configure(font=("Arial", font_sizes[size]))
        except KeyError:
            customtkinter.CTkMessageBox(title="Ошибка", message="Неверный размер шрифта.")
        except Exception as e:
            customtkinter.CTkMessageBox(title="Ошибка", message=f"Ошибка изменения шрифта: {e}")

    font_menu = tk.Menu(widget, tearoff=0, bg="#333333", fg="lightgray")
    for size_name in font_sizes:
        font_menu.add_command(label=size_name, command=lambda s=size_name: change_font_size(s))

    widget.bind("<Button-3>", lambda event, menu=font_menu: menu.post(event.x_root, event.y_root))

def change_theme(is_dark):
    if is_dark:
        customtkinter.set_appearance_mode("dark")
    else:
        customtkinter.set_appearance_mode("light")

def toggle_pinned(note_id, pinned):
    try:
        cur.execute("UPDATE notes SET pinned=? WHERE id=?", (pinned, note_id))
        conn.commit()
        update_notes_list()
    except sqlite3.Error as e:
        print(f"Ошибка изменения статуса закрепления: {e}")
        customtkinter.CTkMessageBox(title="Ошибка", message="Ошибка изменения статуса закрепления.")

root = customtkinter.CTk()
root.title("Just Keep")
root.geometry("800x600")
root.resizable(True, True)
try:
    root.iconbitmap("icon.ico")
except tk.TclError:
    print("Иконка не найдена или некорректный формат.")

header = customtkinter.CTkFrame(root, fg_color="transparent")
header.grid(row=0, column=0, columnspan=2, sticky="ew")

header_label = customtkinter.CTkLabel(header, text="JustKeep", font=("Arial", 24))
header_label.pack(pady=10, side=tk.LEFT, expand=True, fill="x")

#dev.krwg

try:
    image = Image.open("settings_icon.png")
    photo = ImageTk.PhotoImage(image)
    settings_button = customtkinter.CTkButton(header, text="Настройки", image=photo, compound=tk.RIGHT, fg_color=("gray70", "gray30"), hover_color=("gray80", "gray40"), border_width=0, command=open_settings)
    settings_button.image = photo
    settings_button.pack(side=tk.RIGHT, padx=10, pady=10)
except FileNotFoundError:
    print("Файл с иконкой не найден!")
    settings_button = customtkinter.CTkButton(header, text="Настройки", command=open_settings, fg_color=("gray70", "gray30"), hover_color=("gray80", "gray40"), border_width=0)
    settings_button.pack(side=tk.RIGHT, padx=10, pady=10)


left_frame = customtkinter.CTkFrame(root, fg_color="#333333")
left_frame.grid(row=1, column=0, sticky="nsew")

notes_label = customtkinter.CTkLabel(left_frame, text="Здесь будут ваши заметки", font=("Arial", 14), text_color="lightgray")
notes_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

instruction_label = customtkinter.CTkLabel(left_frame, text="Для создания введите текст и Enter", font=("Arial", 10), text_color="#888888")
instruction_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

note_container_frame = customtkinter.CTkFrame(left_frame, fg_color="#333333")
note_container_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
note_container_frame.columnconfigure(0, weight=1)

for i in range(100):
    note_container_frame.rowconfigure(i, weight=1)


right_frame = customtkinter.CTkFrame(root, fg_color="#222222")
right_frame.grid(row=1, column=1, sticky="nsew")

note_label = customtkinter.CTkLabel(right_frame, text="Заметка:", font=("Arial", 12), text_color="lightgray")
note_entry = customtkinter.CTkTextbox(right_frame, font=("Arial", 12), fg_color="#444444", text_color="lightgray")
note_entry.bind("<Return>", save_note)
note_entry.bind("<Control-Return>", lambda event: note_entry.insert(tk.END, "\n"))

note_label.pack(pady=10, padx=10)
note_entry.pack(pady=10, padx=10, fill="both", expand=True)

selected_font_size = tk.StringVar(right_frame, "Обычный")

def change_note_font_size(size):
    try:
        note_entry.configure(font=("Arial", font_sizes[size]))
        selected_font_size.set(size)
    except KeyError:
        customtkinter.CTkMessageBox(title="Ошибка", message="Неверный размер шрифта.")
    except Exception as e:
        customtkinter.CTkMessageBox(title="Ошибка", message=f"Ошибка изменения шрифта: {e}")

font_menu_main = tk.Menu(note_entry, tearoff=0, bg="#333333", fg="lightgray")
for size_name in font_sizes:
    font_menu_main.add_command(label=size_name, command=lambda s=size_name: change_note_font_size(s))

note_entry.bind("<Button-3>", lambda event, menu=font_menu_main: menu.post(event.x_root, event.y_root))

#dev.krwg

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=3)
root.rowconfigure(1, weight=1)


root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", toggle_fullscreen)

db_start()
update_notes_list()

root.protocol("WM_DELETE_WINDOW", lambda: [conn.close(), root.destroy()])

root.mainloop()
