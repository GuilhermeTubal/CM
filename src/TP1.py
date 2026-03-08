from dataclasses import field
from typing import Callable

import flet as ft

@ft.control
class Task(ft.Column):
    task_name: str = ""
    on_status_change: Callable[[], None] = field(default=lambda: None)
    on_delete: Callable[["Task"], None] = field(default=lambda task: None)

    def init(self):
        self.completed = False
        self.display_task = ft.Checkbox(value = False, label = self.task_name, on_change = self.status_changed)
        self.edit_name = ft.TextField(expand = 1)
        self.display_view = ft.Row(
             alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
             vertical_alignment = ft.CrossAxisAlignment.CENTER,
             controls = [
                 self.display_task,
                 ft.Row(
                     spacing = 0,
                     controls = [
                        ft.IconButton(icon = ft.Icons.CREATE_OUTLINED, tooltip = "Editar", on_click = self.edit_clicked),
                        ft.IconButton(icon = ft.Icons.DELETE_OUTLINE, tooltip = "Deletar", on_click = self.delete_clicked),
                     ],
                 ),
                ],
        )


        self.edit_view = ft.Row(
            visible = False,
            alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment = ft.CrossAxisAlignment.CENTER,
            controls = [
                 self.edit_name,
                 ft.IconButton(icon = ft.Icons.DONE_OUTLINE_OUTLINED, icon_color = ft.Colors.GREEN, tooltip = "Atualizar", on_click = self.save_clicked),
            ],

        )

        self.controls = [self.display_view, self.edit_view]

    def status_changed(self, e):
        self.completed = self.display_task.value
        self.on_status_change()

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False  
        self.update()
    
    def delete_clicked(self, e):
        self.on_delete(self)
    


@ft.control
class TodoApp(ft.Column):
    def init(self):
        self.new_task = ft.TextField(hint_text = "O que precisa fazer?", expand = True)
        self.tasks = ft.Column()
        self.tasks_left = ft.Text("0 tarefas restantes")

        self.filter = ft.TabBar(
            scrollable=False,
            tabs=[
                ft.Tab(label="Todas"),
                ft.Tab(label="Ativas"),
                ft.Tab(label="Completas"),
            ],
        )

        self.filter_tabs = ft.Tabs(
            length=3,
            selected_index=0,
            on_change=lambda e: self.update(),
            content=self.filter,
        )

        self.width = 600
        self.controls = [
                ft.Row(
                    controls = [self.new_task, ft.FloatingActionButton(icon = ft.Icons.ADD, on_click=self.add_clicked)],
                ),
            ft.Column(
                spacing = 25,
                controls = [self.filter_tabs, self.tasks, ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                    vertical_alignment=ft.CrossAxisAlignment.CENTER, 
                    controls=[
                        self.tasks_left,
                        ft.OutlinedButton(
                            content = ft.Text("Limpar completas"), 
                            on_click=self.clear_tasks
                            ),
                         ],
                    ),
                 ],
             ),
         ]
    

    def clear_tasks(self, e):
        for tasks in self.tasks.controls[:]:
            if tasks.completed:
                self.tasks.controls.remove(tasks)
            self.update()

    def tabs_changed(self, e):
        self.update()

    def task_status_change(self):
        self.update()


    def add_clicked(self, e):
        task = Task(
            task_name=self.new_task.value,
            on_status_change=self.task_status_change,
            on_delete=self.task_delete,
        )
        self.tasks.controls.append(task)
        self.new_task.value = ""
        self.update()

    def task_delete(self, task):
            self.tasks.controls.remove(task)
            self.update()

    def before_update(self):
        status = self.filter.tabs[self.filter_tabs.selected_index].label
        count = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "Todas"
                or (status == "Ativas" and task.completed == False)
                or (status == "Completas" and task.completed)
            )
            if not task.completed:
                count += 1
        self.tasks_left.value = f"{count} tarefa(s) restante(s)"
        
def main(page: ft.Page):
    page.title = "Gestor de Tarefas"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()
    
    todo = TodoApp()

    page.add(todo)

ft.run(main)