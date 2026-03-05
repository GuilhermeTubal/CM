#!uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
# "flet[all]>=0.80.5",
# ]
# ///

import flet as ft
def main(page: ft.Page):
    page.title = "Flet counter example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    txt_number = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    def minus_click(e):
        txt_number.value = str(int(txt_number.value) - 1)
    def plus_click(e):
        txt_number.value = str(int(txt_number.value) + 1)

    page.add(
        ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.REMOVE, on_click=minus_click),
                txt_number,
                ft.IconButton(icon=ft.Icons.ADD, on_click=plus_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )
ft.run(main) # Janela nativa