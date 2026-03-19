import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class StudentRow(ttk.Frame):
    """Represents a data row with read-only cells and action buttons."""

    def __init__(self, parent, record, on_edit, on_delete, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.record_id = record["id"]
        self.on_edit = on_edit
        self.on_delete = on_delete
        self._edit_mode = False
        self.vars = {
            "name": tk.StringVar(value=record["name"]),
            "enrollment": tk.StringVar(value=record["enrollment"]),
            "course": tk.StringVar(value=record["course"]),
            "phone": tk.StringVar(value=record["phone"]),
        }

        self.cells = {}
        self.inputs = {}
        for col, text in enumerate(
            ["name", "enrollment", "course", "phone"], start=0
        ):
            lbl = ttk.Label(
                self,
                textvariable=self.vars[text],
                anchor="center",
                style="TableCell.TLabel",
                padding=(10, 6),
            )
            lbl.grid(row=0, column=col, sticky="nsew")

            entry = ttk.Entry(self, textvariable=self.vars[text], width=18)
            entry.grid(row=0, column=col, sticky="nsew", padx=2, pady=3)
            entry.grid_remove()

            self.cells[text] = lbl
            self.inputs[text] = entry

        self.action_frame = ttk.Frame(self)
        self.action_frame.grid(row=0, column=4, sticky="nsew", padx=4)

        self.edit_btn = ttk.Button(
            self.action_frame, text="Edit", command=self._enter_edit_mode, width=8
        )
        self.delete_btn = ttk.Button(
            self.action_frame,
            text="Delete",
            command=lambda: self.on_delete(self.record_id),
            width=8,
            style="Danger.TButton",
        )
        self.save_btn = ttk.Button(
            self.action_frame, text="Save", command=self._save_changes, width=8
        )
        self.cancel_btn = ttk.Button(
            self.action_frame, text="Cancel", command=self._cancel_edit, width=8
        )

        self.edit_btn.pack(side="left", padx=2)
        self.delete_btn.pack(side="left", padx=2)

        for col in range(5):
            self.columnconfigure(col, weight=1)

    def update_record(self, record):
        """Refresh displayed values from record store."""
        for key in self.vars:
            self.vars[key].set(record[key])

    def _enter_edit_mode(self):
        if self._edit_mode:
            return
        self._edit_mode = True
        for key in self.cells:
            self.cells[key].grid_remove()
            self.inputs[key].grid()
        self.edit_btn.pack_forget()
        self.delete_btn.pack_forget()
        self.save_btn.pack(side="left", padx=2)
        self.cancel_btn.pack(side="left", padx=2)
        self.on_edit(self.record_id, state="started")

    def _save_changes(self):
        data = {key: var.get().strip() for key, var in self.vars.items()}
        success = self.on_edit(self.record_id, state="saved", data=data)
        if success:
            self._exit_edit_mode()

    def _cancel_edit(self):
        self.on_edit(self.record_id, state="cancelled")
        self._exit_edit_mode()

    def _exit_edit_mode(self):
        self._edit_mode = False
        for key in self.cells:
            self.inputs[key].grid_remove()
            self.cells[key].grid()
        self.save_btn.pack_forget()
        self.cancel_btn.pack_forget()
        self.edit_btn.pack(side="left", padx=2)
        self.delete_btn.pack(side="left", padx=2)


class Dashboard(tk.Tk):
    """Main application window encapsulating CRUD logic."""

    def __init__(self):
        super().__init__()
        self.title("College Management Dashboard")
        self.geometry("1000x640")
        self.minsize(920, 600)

        self.records = []
        self.next_id = 1
        self.row_widgets = {}
        self.active_edit_id = None

        self._configure_style()
        self._build_layout()

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Card.TFrame",
            background="#ffffff",
            borderwidth=1,
            relief="ridge",
            padding=20,
        )
        style.configure(
            "Heading.TLabel", font=("Segoe UI Semibold", 18), background="#f7f9fc"
        )
        style.configure(
            "Subheading.TLabel", font=("Segoe UI", 12), background="#ffffff"
        )
        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=6,
            background="#2563eb",
            foreground="#ffffff",
        )
        style.map(
            "Accent.TButton",
            foreground=[("active", "#ffffff")],
            background=[("active", "#1d4ed8")],
        )
        style.configure(
            "Danger.TButton",
            background="#dc2626",
            foreground="#ffffff",
            font=("Segoe UI", 10),
        )
        style.map(
            "Danger.TButton",
            foreground=[("active", "#ffffff")],
            background=[("active", "#b91c1c")],
        )
        style.configure(
            "TableHeader.TLabel",
            font=("Segoe UI Semibold", 11),
            background="#e2e8f0",
            padding=(10, 6),
        )
        style.configure(
            "TableCell.TLabel",
            font=("Segoe UI", 10),
            background="#ffffff",
        )

    def _build_layout(self):
        root_container = ttk.Frame(self, padding=20)
        root_container.pack(fill="both", expand=True)
        root_container.columnconfigure(0, weight=1)
        root_container.rowconfigure(1, weight=1)

        header = ttk.Label(
            root_container,
            text="College Management Dashboard",
            style="Heading.TLabel",
            padding=(10, 20),
        )
        header.grid(row=0, column=0, sticky="w")

        content = ttk.Frame(root_container)
        content.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        content.columnconfigure(1, weight=1)

        self._build_form(content)
        self._build_table(content)

    def _build_form(self, parent):
        form_card = ttk.Frame(parent, style="Card.TFrame")
        form_card.grid(row=0, column=0, sticky="ns", padx=(0, 20))

        ttk.Label(
            form_card, text="Add Student Record", style="Subheading.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        self.form_vars = {
            "name": tk.StringVar(),
            "enrollment": tk.StringVar(),
            "course": tk.StringVar(),
            "phone": tk.StringVar(),
        }

        fields = [
            ("Student Name", "name"),
            ("Enrollment Number", "enrollment"),
            ("Course Name", "course"),
            ("Phone Number", "phone"),
        ]

        for idx, (label, key) in enumerate(fields, start=1):
            ttk.Label(form_card, text=label).grid(
                row=idx, column=0, sticky="w", pady=6
            )
            entry = ttk.Entry(form_card, textvariable=self.form_vars[key], width=28)
            entry.grid(row=idx, column=1, pady=6)

        add_btn = ttk.Button(
            form_card,
            text="Add Record",
            style="Accent.TButton",
            command=self._handle_add_record,
        )
        add_btn.grid(row=len(fields) + 1, column=0, columnspan=2, pady=(16, 0))

    def _build_table(self, parent):
        table_container = ttk.Frame(parent)
        table_container.grid(row=0, column=1, sticky="nsew")
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(1, weight=1)

        ttk.Label(
            table_container,
            text="Student Records",
            style="Subheading.TLabel",
            padding=(0, 0, 0, 10),
        ).grid(row=0, column=0, sticky="w")

        header_frame = ttk.Frame(table_container)
        header_frame.grid(row=1, column=0, sticky="ew")
        header_frame.columnconfigure(tuple(range(5)), weight=1)

        headers = [
            "Student Name",
            "Enrollment No.",
            "Course",
            "Phone",
            "Actions",
        ]
        for idx, text in enumerate(headers):
            ttk.Label(
                header_frame,
                text=text,
                style="TableHeader.TLabel",
                anchor="center",
            ).grid(row=0, column=idx, sticky="ew")

        self.table_frame = ttk.Frame(table_container)
        self.table_frame.grid(row=2, column=0, sticky="nsew")
        self.table_frame.columnconfigure(0, weight=1)

    def _validate_inputs(self, data):
        if not all(data.values()):
            messagebox.showwarning("Validation", "All fields are required.")
            return False

        if not data["phone"].isdigit() or len(data["phone"]) < 7:
            messagebox.showwarning(
                "Validation", "Phone number must be numeric and at least 7 digits."
            )
            return False

        return True

    def _handle_add_record(self):
        data = {key: var.get().strip() for key, var in self.form_vars.items()}
        if not self._validate_inputs(data):
            return

        record = {**data, "id": self.next_id}
        self.next_id += 1
        self.records.append(record)
        self._render_row(record)

        for var in self.form_vars.values():
            var.set("")

    def _render_row(self, record):
        row = StudentRow(
            self.table_frame,
            record,
            on_edit=self._handle_row_edit,
            on_delete=self._handle_row_delete,
        )
        index = len(self.row_widgets)
        row.grid(row=index, column=0, sticky="ew", pady=4)
        row.columnconfigure(tuple(range(5)), weight=1)
        self.row_widgets[record["id"]] = row
        self._refresh_row_styles()

    def _refresh_row_styles(self):
        for pos, row in enumerate(self.row_widgets.values()):
            bg = "#f8fafc" if pos % 2 == 0 else "#ffffff"
            for label in row.cells.values():
                label.configure(background=bg)

    def _handle_row_edit(self, record_id, state, data=None):
        if state == "started":
            if self.active_edit_id and self.active_edit_id != record_id:
                messagebox.showinfo(
                    "Edit in progress",
                    "Finish the current edit before modifying another record.",
                )
                return False
            self.active_edit_id = record_id
            return True

        if state == "cancelled":
            record = self._get_record(record_id)
            if record:
                self.row_widgets[record_id].update_record(record)
            self.active_edit_id = None
            return True

        if state == "saved" and data:
            if not self._validate_inputs(data):
                return False
            record = self._get_record(record_id)
            if record:
                record.update(data)
                self.row_widgets[record_id].update_record(record)
            self.active_edit_id = None
            return True

        return False

    def _handle_row_delete(self, record_id):
        if messagebox.askyesno(
            "Delete Record", "Are you sure you want to delete this record?"
        ):
            record = self._get_record(record_id)
            if record:
                self.records.remove(record)
                widget = self.row_widgets.pop(record_id, None)
                if widget:
                    widget.destroy()
                self._reflow_rows()
                self.active_edit_id = None

    def _get_record(self, record_id):
        for record in self.records:
            if record["id"] == record_id:
                return record
        return None

    def _reflow_rows(self):
        for index, row in enumerate(self.row_widgets.values()):
            row.grid_configure(row=index)
        self._refresh_row_styles()


def main():
    app = Dashboard()
    app.mainloop()


if __name__ == "__main__":
    main()

