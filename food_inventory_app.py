from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from tkinter import ttk
except ImportError:  # pragma: no cover - fallback for minimal Tk installs
    tk = None

try:
    import tkinter as tk
    import tkinter.messagebox as messagebox
except ModuleNotFoundError:  # pragma: no cover - GUI runtime is optional for backend tests
    tk = None
    messagebox = None

UNIDADES = [
    "gramas",
    "kilogramas",
    "mililitros",
    "litros",
]

CATEGORIAS = [
    "frutas",
    "vegetais",
    "legumes",
    "grãos",
    "carne",
    "peixe",
    "pão",
    "cereais",
    "laticínios",
    "sobremesas e doces",
    "alimentos preparados",
    "especiarias e temperos",
    "bebidas",
]

LOCATIONS = [
    "desconhecido",
    "geladeira",
    "freezer",
    "armário ",
]

FIELDNAMES = [
    "marca",
    "tipo_produto",
    "quantidade",
    "unidade",
    "categoria",
    "localizacao",
    "data_validade",
    "comentarios",
    "data_de_registro",
]

class InventoryManager:
    def __init__(self, storage_path: str = "alimentos.csv") -> None:
        if Path(storage_path).is_absolute():
            self.storage_path = Path(storage_path)
        else:
            base_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
            self.storage_path = (base_dir / storage_path).resolve()
        self.items: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        self._ensure_storage_file()
        self.load()

    def _ensure_storage_file(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if self.storage_path.exists():
            if self.storage_path.stat().st_size == 0:
                with self.storage_path.open("w", newline="", encoding="utf-8") as handle:
                    writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
                    writer.writeheader()
            return

        with self.storage_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
            writer.writeheader()

    def _normalize_key(self, marca: str, tipo_produto: str, data_validade: Optional[str] = None) -> Tuple[str, str, str]:
        return (marca.strip(), tipo_produto.strip(), (data_validade or "").strip())

    def _today_iso(self) -> str:
        return date.today().isoformat()

    def _days_until_expiration(self, data_validade: Optional[str]) -> Optional[int]:
        if not data_validade:
            return None
        try:
            return (date.fromisoformat(data_validade) - date.today()).days
        except ValueError:
            return None

    def _is_near_expiration(self, data_validade: Optional[str]) -> bool:
        days = self._days_until_expiration(data_validade)
        if days is None:
            return False
        return days <= 30

    def _load_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {
            "marca": str(item.get("marca", "")).strip(),
            "tipo_produto": str(item.get("tipo_produto", "")).strip(),
            "quantidade": float(item.get("quantidade", 0) or 0),
            "unidade": str(item.get("unidade", "")).strip(),
            "categoria": str(item.get("categoria", "")).strip(),
            "localizacao": str(item.get("localizacao", "not stored")).strip(),
            "comentarios": str(item.get("comentarios", "")).strip(),
            "data_de_registro": str(item.get("data_de_registro") or self._today_iso()),
            "data_validade": str(item.get("data_validade") or "").strip(),
        }
        return normalized

    def load(self) -> None:
        self._ensure_storage_file()
        self.items = {}

        try:
            with self.storage_path.open("r", newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames is None:
                    return
                for row in reader:
                    if not row or all((value is None or str(value).strip() == "") for value in row.values()):
                        continue
                    payload = {
                        "marca": row.get("marca", ""),
                        "tipo_produto": row.get("tipo_produto", ""),
                        "quantidade": row.get("quantidade", ""),
                        "unidade": row.get("unidade", ""),
                        "categoria": row.get("categoria", ""),
                        "localizacao": row.get("localizacao", "not stored"),
                        "comentarios": row.get("comentarios", ""),
                        "data_de_registro": row.get("data_de_registro") or self._today_iso(),
                        "data_validade": row.get("data_validade"),
                    }
                    normalized = self._load_item(payload)
                    key = self._normalize_key(normalized["marca"], normalized["tipo_produto"], normalized["data_validade"])
                    self.items[key] = normalized
        except (OSError, ValueError, TypeError):
            self.items = {}

    def save(self) -> None:
        self._ensure_storage_file()
        fieldnames = FIELDNAMES

        with self.storage_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for item in self.items.values():
                writer.writerow({
                    "marca": item.get("marca", ""),
                    "tipo_produto": item.get("tipo_produto", ""),
                    "quantidade": item.get("quantidade", 0),
                    "unidade": item.get("unidade", "pack"),
                    "categoria": item.get("categoria", ""),
                    "localizacao": item.get("localizacao", "not stored"),
                    "data_validade": item.get("data_validade", ""),
                    "comentarios": item.get("comentarios", ""),
                    "data_de_registro": item.get("data_de_registro") or self._today_iso(),
                })

    def get_item(self, marca: str, tipo_produto: str, data_validade: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if data_validade is not None:
            return self.items.get(self._normalize_key(marca, tipo_produto, data_validade))
        matches = self.search_items(marca, tipo_produto)
        return matches[0] if matches else None

    def search_items(self, marca: str, tipo_produto: str) -> List[Dict[str, Any]]:
        matches = [
            item for key, item in self.items.items()
            if key[0].strip().lower() == marca.strip().lower() and key[1].strip().lower() == tipo_produto.strip().lower()
        ]
        matches.sort(key=lambda item: item.get("data_validade") or "9999-12-31")
        return matches

    def register_item(
        self,
        marca: str,
        tipo_produto: str,
        quantidade: float,
        unidade: str,
        categoria: str,
        localização: str,
        comentários: str,
        data_validade: str,
    ) -> Dict[str, Any]:
        key = self._normalize_key(marca, tipo_produto, data_validade)
        existing = self.items.get(key)
        if existing:
            existing["marca"] = marca.strip()
            existing["tipo_produto"] = tipo_produto.strip()
            existing["quantidade"] += float(quantidade or 0)
            existing["unidade"] = unidade.strip()
            existing["categoria"] = categoria.strip()
            existing["localizacao"] = localização.strip()
            existing["comentarios"] = comentários.strip()
            existing["data_de_registro"] = existing.get("data_de_registro", self._today_iso())
            existing["data_validade"] = data_validade
            self.save()
            return existing

        item = {
            "marca": marca.strip(),
            "tipo_produto": tipo_produto.strip(),
            "quantidade": float(quantidade or 0),
            "unidade": unidade.strip(),
            "categoria": categoria.strip(),
            "localizacao": localização.strip(),
            "comentarios": comentários.strip(),
            "data_de_registro": self._today_iso(),
            "data_validade": data_validade,
        }
        self.items[key] = item
        self.save()
        return item
    
    def update_item(
        self,
        key: Tuple[str, str, str],
        quantidade: float,
    ) -> Dict[str, Any]:
        existing = self.items.get(key)
        if not existing:
            raise ValueError(f"Item with key {key} not found.")

        existing["quantidade"] += float(quantidade or 0)
        self.save()
        return existing

    def add_unidades(self, marca: str, tipo_produto: str, quantidade: int, data_validade: str) -> Dict[str, Any]:
        if quantidade <= 0:
            raise ValueError("quantidade must be greater than zero.")

        key = self._normalize_key(marca, tipo_produto, data_validade)
        item = self.update_item(
            key=key,
            quantidade=quantidade,
        )
        self.save()
        return item
    
    def remove_unidades(self, marca: str, tipo_produto: str, quantidade: int, data_validade: str) -> Dict[str, Any]:
        if quantidade <= 0:
            raise ValueError("quantidade must be greater than zero.")

        key = self._normalize_key(marca, tipo_produto, data_validade)

        item = self.items.get(key)
        if quantidade > item.get("quantidade", 0):
            raise ValueError(f"Cannot remove {quantidade} unidades; only {item.get('quantidade', 0)} available.")

        item = self.update_item(
            key=key,
            quantidade=-1*quantidade,
        )
        self.save()
        return item

    def _report_items(self, predicate) -> List[Dict[str, Any]]:
        rows = []
        for item in self.items.values():
            if item.get("quantidade", 0) <= 0:
                continue
            if predicate(item):
                row = dict(item)
                row["days_until_expiration"] = self._days_until_expiration(item.get("data_validade"))
                rows.append(row)
        rows.sort(key=lambda item: item.get("data_validade") or "9999-12-31")
        return rows

    def report_items_in_stock(self) -> List[Dict[str, Any]]:
        return self._report_items(lambda item: item.get("quantidade", 0) > 0)

    def report_data_validade(self) -> List[Dict[str, Any]]:
        return self.report_items_in_stock()

    def report_nearing_expiration(self, days: int = 30) -> List[Dict[str, Any]]:
        def predicate(item: Dict[str, Any]) -> bool:
            exp = self._days_until_expiration(item.get("data_validade"))
            return exp is not None and exp <= days

        return self._report_items(predicate)

    def report_expired_items(self) -> List[Dict[str, Any]]:
        def predicate(item: Dict[str, Any]) -> bool:
            exp = self._days_until_expiration(item.get("data_validade"))
            return exp is not None and exp < 0

        return self._report_items(predicate)


if tk is not None:
    class InventoryApp(tk.Tk):
        def __init__(self) -> None:
            super().__init__()
            self.title("Food Inventory Management")
            self.geometry("980x700")
            self.manager = InventoryManager(storage_path="alimentos.csv")
            self.current_item = None

            self.search_marca_var = tk.StringVar()
            self.search_type_var = tk.StringVar()

            self.main_frame = tk.Frame(self, padx=16, pady=16)
            self.main_frame.pack(fill="both", expand=True)

            self._build_search_panel()
            self._build_reports_panel()
            self._build_inventory_panel()

        def _build_reports_panel(self) -> None:
            report_button = tk.Button(self.main_frame, text="Relatórios", command=self.show_reports)
            report_button.pack(pady=(12, 0))
            tk.Button(report_button, text="Relatórios", command=self.show_reports).grid(row=0, column=6, padx=10, pady=4)

        def _build_search_panel(self) -> None:
            panel = tk.LabelFrame(self.main_frame, text="Buscar ou registrar produto", padx=12, pady=12)
            panel.pack(fill="x", pady=(0, 12))

            tk.Label(panel, text="Marca").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
            tk.Entry(panel, textvariable=self.search_marca_var, width=25).grid(row=0, column=1, padx=8, pady=4)

            tk.Label(panel, text="Tipo de produto").grid(row=0, column=2, sticky="w", padx=(20, 8), pady=4)
            tk.Entry(panel, textvariable=self.search_type_var, width=25).grid(row=0, column=3, padx=8, pady=4)

            tk.Button(panel, text="Buscar produto", command=self.search_item).grid(row=0, column=4, padx=10, pady=4)
            tk.Button(panel, text="Registrar novo produto", command=self.open_registration_form).grid(row=1, column=4, padx=12, pady=4)

        def _build_inventory_panel(self) -> None:
            self.info_frame = tk.LabelFrame(self.main_frame, text="Status do estoque", padx=12, pady=12)
            self.info_frame.pack(fill="both", expand=True)

            self.table_frame = tk.Frame(self.info_frame)
            self.table_frame.pack(fill="both", expand=True)

            self.table_actions_frame = tk.Frame(self.info_frame)
            self.table_actions_frame.pack(fill="x", pady=(8, 0))

            self.details_text = tk.Text(self.info_frame, height=18, width=110, wrap="word")
            self.details_text.pack(fill="both", expand=True)

            self.actions_frame = tk.Frame(self.info_frame)
            self.actions_frame.pack(fill="x", pady=(8, 0))

        def _set_detail_text(self, text: str) -> None:
            self.details_text.delete("1.0", tk.END)
            self.details_text.insert("1.0", text)

        def _show_table(self, rows: List[Dict[str, Any]]) -> None:
            for widget in self.table_frame.winfo_children():
                widget.destroy()
            if not rows:
                self.current_item = None
                self._set_detail_text("")
                self._update_actions()
                tk.Label(self.table_frame, text="Nenhum item encontrado.").pack(anchor="w")
                return

            columns = sorted(list(rows[0].keys()), key=lambda x: FIELDNAMES.index(x) if x in FIELDNAMES else len(FIELDNAMES))
            tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
            for column in columns:
                tree.heading(column, text=column)
                tree.column(column, width=120, anchor="w")
            for row in rows:
                tree.insert("", "end", values=[row.get(column, "") for column in columns])
            tree.pack(fill="both", expand=True)

            def on_select(_event) -> None:
                selected = tree.selection()
                if not selected:
                    self.current_item = None
                    self._set_detail_text("")
                    self._update_actions()
                    return

                index = tree.index(selected[0])
                self.current_item = rows[index]
                self._set_detail_text(self._format_item_details(self.current_item))
                self._update_actions()

            tree.bind("<<TreeviewSelect>>", on_select)
            self.current_item = None
            self._set_detail_text("")
            self._update_actions()

        def _update_actions(self) -> None:
            for child in self.table_actions_frame.winfo_children():
                child.destroy()
            for child in self.actions_frame.winfo_children():
                child.destroy()

            if self.current_item is None:
                return

            item_label = (
                f"Item selecionado: {self.current_item.get('marca', '')} - "
                f"{self.current_item.get('tipo_produto', '')} "
                f"(exp {self.current_item.get('data_validade', '')})"
            )
            tk.Label(self.table_actions_frame, text=item_label, anchor="w").pack(side="left", padx=(0, 10))
            tk.Button(self.table_actions_frame, text="Adicionar", command=self.add_unidades_for_current_item).pack(side="left", padx=(0, 10))
            tk.Button(self.table_actions_frame, text="Remover", command=self.remove_unidades_for_current_item).pack(side="left")

        def _build_change_quantidade_dialog(self, action: str) -> None:
            if self.current_item is None:
                return

            dialog = tk.Toplevel(self)
            dialog.title(f"{action.title()} unidades")
            dialog.geometry("320x220")

            tk.Label(dialog, text="quantidade").grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))
            quantidade_var = tk.StringVar(value="1")
            tk.Entry(dialog, textvariable=quantidade_var, width=20).grid(row=0, column=1, padx=12, pady=(12, 4))

            def submit() -> None:
                try:
                    qty = int(quantidade_var.get())
                    if action == "add":
                        self.manager.add_unidades(self.current_item["marca"], self.current_item["tipo_produto"], qty, self.current_item["data_validade"])
                    else:
                        self.manager.remove_unidades(self.current_item["marca"], self.current_item["tipo_produto"], qty, self.current_item["data_validade"])
                    self.search_item()
                    dialog.destroy()
                except Exception as exc:
                    if messagebox is not None:
                        messagebox.showerror("Erro ao atualizar estoque", str(exc))

            tk.Button(dialog, text="Confirm", command=submit).grid(row=2, column=0, columnspan=2, pady=18)

        def add_unidades_for_current_item(self) -> None:
            self._build_change_quantidade_dialog("add")

        def remove_unidades_for_current_item(self) -> None:
            self._build_change_quantidade_dialog("remove")

        def search_item(self) -> None:
            marca = self.search_marca_var.get().strip()
            tipo_produto = self.search_type_var.get().strip()

            if not marca or not tipo_produto:
                self.current_item = None
                self._update_actions()
                self._set_detail_text("Por favor, forneça tanto a marca quanto o tipo de produto para pesquisar.")
                return

            items = self.manager.search_items(marca, tipo_produto)
            if not items:
                self.current_item = None
                self._update_actions()
                self._set_detail_text(
                    f"Nenhum produto encontrado para {marca} - {tipo_produto}.\n"
                    "Use o formulário de registro para criá-lo."
                )
                return

            self.current_item = None
            self._show_table(items)
            self._set_detail_text("")
            self._update_actions()

        def _format_item_details(self, item: Dict[str, Any]) -> str:
            details = [
                f"Marca: {item.get('marca', '')}",
                f"Tipo de produto: {item.get('tipo_produto', '')}",
                f"Quantidade no estoque: {item.get('quantidade', 0)}",
                f"Categoria: {item.get('categoria', '') or 'Não definida'}",
                f"Localização: {item.get('localização', '') or 'Não definida'}",
                f"Data de validade: {item.get('data_validade', '') or 'Não definida'}",
                f"Comentários: {item.get('comentários', '') or ''}",
                f"Data de registro: {item.get('data_de_registro', 'Não disponível')}",
            ]
            return "\n".join(details)

        def open_registration_form(self) -> None:
            if tk is None:
                raise RuntimeError("Tkinter is not available in this environment.")
            marca = self.search_marca_var.get().strip() or ""
            tipo_produto = self.search_type_var.get().strip() or ""

            form = tk.Toplevel(self)
            form.title("Registrar novo item")
            form.geometry("520x520")

            current = {
                "marca": tk.StringVar(value=marca),
                "tipo_produto": tk.StringVar(value=tipo_produto),
                "quantidade": tk.StringVar(value="1"),
                "unidade": tk.StringVar(value="kilograms"),
                "categoria": tk.StringVar(value=""),
                "localizacao": tk.StringVar(value=""),
                "comentarios": tk.StringVar(value=""),
                "data_validade": tk.StringVar(value=date.today().isoformat()),
            }

            def choose_option(variable: tk.StringVar, options: List[str], title: str) -> None:
                popup = tk.Toplevel(form)
                popup.title(title)
                popup.geometry("260x260")
                listbox = tk.Listbox(popup)
                for option in options:
                    listbox.insert(tk.END, option)
                listbox.pack(fill="both", expand=True, padx=10, pady=10)

                def set_value() -> None:
                    selection = listbox.curselection()
                    if selection:
                        variable.set(listbox.get(selection[0]))
                    popup.destroy()

                tk.Button(popup, text="Select", command=set_value).pack(pady=(0, 10))

            labels = [
                ("Marca", "marca"),
                ("Tipo de produto", "tipo_produto"),
                ("Quantidade", "quantidade"),
                ("Unidade", "unidade"),
                ("Categoria", "categoria"),
                ("Localização", "localizacao"),
                ("Data de validade", "data_validade"),
                ("Comentários", "comentarios"),
            ]

            row = 0
            for label_text, key in labels:
                tk.Label(form, text=label_text).grid(row=row, column=0, sticky="w", padx=12, pady=6)
                if key in {"unidade", "categoria"}:
                    entry = tk.Entry(form, textvariable=current[key], width=28)
                    entry.grid(row=row, column=1, sticky="ew", padx=12, pady=6)
                    choices = UNIDADES if key == "unidade" else CATEGORIAS
                    tk.Button(form, text="Select", command=lambda v=current[key], opts=choices, title=label_text: choose_option(v, opts, title)).grid(row=row, column=2, padx=8)
                else:
                    entry = tk.Entry(form, textvariable=current[key], width=28)
                    entry.grid(row=row, column=1, columnspan=2, sticky="ew", padx=12, pady=6)
                row += 1

            def save_item() -> None:
                try:
                    marca = current["marca"].get().strip()
                    tipo_produto = current["tipo_produto"].get().strip()
                    if not marca or not tipo_produto:
                        raise ValueError("Marca e tipo de produto são obrigatórios.")

                    item = self.manager.register_item(
                        marca=marca,
                        tipo_produto=tipo_produto,
                        quantidade=float(current["quantidade"].get()),
                        unidade=current["unidade"].get().strip() or "",
                        categoria=current["categoria"].get().strip() or "",
                        localização=current["localizacao"].get().strip() or "",
                        comentários=current["comentarios"].get().strip(),
                        data_validade=current["data_validade"].get().strip() or date.today().isoformat(),
                    )
                    self.current_item = item
                    self.search_marca_var.set(marca)
                    self.search_type_var.set(tipo_produto)
                    self.search_item()
                    form.destroy()
                except Exception as exc:
                    if messagebox is not None:
                        messagebox.showerror("Erro ao tentar registrar item", str(exc))
                    else:
                        raise

            tk.Button(form, text="Finalizar e salvar", command=save_item).grid(row=row, column=0, columnspan=3, pady=18)

        def _sorted_items_by_product(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            return sorted(
                rows,
                key=lambda item: (
                    str(item.get("tipo_produto", "")).lower(),
                    str(item.get("marca", "")).lower(),
                    str(item.get("data_validade") or "").lower(),
                ),
            )

        def _export_summary_rows_to_csv(self, rows: List[Dict[str, Any]], filename: str) -> None:
            base_dir = Path(self.manager.storage_path).resolve().parent
            foldername = "relatorios"
            filename = f"{filename}_{date.today().isoformat()}.csv"
            export_path = (base_dir / foldername / filename).resolve()
            export_path.parent.mkdir(parents=True, exist_ok=True)

            with export_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=rows[0].keys() if rows else [])
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)

            if messagebox is not None:
                messagebox.showinfo("CSV exportado", f"Arquivo salvo em:\n{export_path}")

        def _render_summary_table(self, parent: tk.Misc, title: str, rows: List[Dict[str, Any]], columns: List[str], export: bool = False) -> None:
            frame = tk.LabelFrame(parent, text=title, padx=8, pady=8)
            frame.pack(fill="both", expand=True, pady=(0, 8))
            if not rows:
                tk.Label(frame, text="Nenhum item.").pack(anchor="w")
                return

            if export:
                tk.Button(
                    frame,
                    text="Salvar CSV",
                    command=lambda: self._export_summary_rows_to_csv(rows, f"{title.replace(' ', '_').lower()}"),
                ).pack(side="right")

            tree = ttk.Treeview(frame, columns=columns, show="headings", height=6)
            for column in columns:
                tree.heading(column, text=column)
                tree.column(column, width=180, anchor="w")
            for row in rows:
                tree.insert("", "end", values=[row.get(column, "") for column in columns])
            tree.pack(fill="both", expand=True)

        def _refresh_database_summary(self, parent: tk.Misc) -> None:
            for child in parent.winfo_children():
                child.destroy()

            stock_rows = [
                {"marca": item.get("marca", ""), "tipo_produto": item.get("tipo_produto", "")}
                for item in self.manager.items.values()
                if item.get("quantidade", 0) > 0
            ]
            near_rows = []
            expired_rows = []
            for item in self.manager.items.values():
                if item.get("quantidade", 0) <= 0:
                    continue
                days = self.manager._days_until_expiration(item.get("data_validade"))
                if days is None:
                    continue
                row = {
                    "marca": item.get("marca", ""),
                    "tipo_produto": item.get("tipo_produto", ""),
                    "data_validade": item.get("data_validade", ""),
                }
                if days < 0:
                    expired_rows.append(row)
                elif days <= 30:
                    near_rows.append(row)

            self._render_summary_table(
                parent,
                "Produtos em estoque",
                self._sorted_items_by_product(stock_rows),
                ["marca", "tipo_produto"],
            )
            self._render_summary_table(
                parent,
                "Produtos próximos ao vencimento",
                self._sorted_items_by_product(near_rows),
                ["marca", "tipo_produto", "data_validade"],
                export=True,
            )
            self._render_summary_table(
                parent,
                "Produtos vencidos",
                self._sorted_items_by_product(expired_rows),
                ["marca", "tipo_produto", "data_validade"],
                export=True,
            )

        def show_reports(self) -> None:
            report_window = tk.Toplevel(self)
            report_window.title("Relatórios")
            report_window.geometry("700x520")

            self._refresh_database_summary(report_window)

else:
    class InventoryApp:
        def __init__(self) -> None:
            raise RuntimeError("Tkinter is not available in this environment; the GUI app cannot be launched here.")


def run_application() -> None:
    if tk is None:
        raise RuntimeError("Tkinter is not available in this environment; the GUI app cannot be launched here.")
    app = InventoryApp()
    app.mainloop()


if __name__ == "__main__":
    run_application()
