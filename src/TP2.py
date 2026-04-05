from dataclasses import dataclass, field
import uuid
import flet as ft


# ---------------------------------------------------------
#   DATA CLASS DAS MENSAGENS
# ---------------------------------------------------------
@dataclass
class Message:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_name: str = ""
    text: str = ""
    message_type: str = "chat_message"  
    room: str = "general"
    to_user: str | None = None
    target_id: str | None = None
    reaction_emoji: str | None = None


# ---------------------------------------------------------
#   COMPONENTE VISUAL DE UMA MENSAGEM
# ---------------------------------------------------------
@ft.control
class ChatMessage(ft.Column):
    def __init__(self, message: Message, current_user: str, dark_mode: bool, on_edit, on_delete, on_react):
        super().__init__()
        self.message = message
        self.current_user = current_user
        self.dark_mode = dark_mode
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_react = on_react
        self.reactions: dict[str, int] = {}

        bg = ft.Colors.BLUE_GREY_900 if dark_mode else ft.Colors.BLUE
        txt = ft.Colors.WHITE if dark_mode else ft.Colors.WHITE

        avatar = ft.CircleAvatar(
            content=ft.Text(self.message.user_name[:1].upper()) if self.message.user_name else None,
            bgcolor=bg,
            color=txt,
        )

        header = ft.Text(self.message.user_name, weight=ft.FontWeight.BOLD, color=txt) if self.message.user_name else ft.Text("")

        if self.message.message_type == "private_message":
            content = ft.Text(f"[Privado] {self.message.text}", color=ft.Colors.PINK)
        else:
            content = ft.Text(self.message.text, color=txt)

        actions = ft.Row(spacing=5)
        if self.message.user_name == self.current_user and self.message.message_type in ("chat_message", "private_message"):
            actions.controls.append(
                ft.IconButton(icon=ft.Icons.EDIT, icon_size=16, on_click=lambda _: self.on_edit(self.message))
            )
            actions.controls.append(
                ft.IconButton(icon=ft.Icons.DELETE, icon_size=16, on_click=lambda _: self.on_delete(self.message))
            )

        self.reactions_row = ft.Row(spacing=5)
        reaction_buttons = ft.Row(
            controls=[
                ft.TextButton("👍", on_click=lambda _: self.on_react(self.message, "👍")),
                ft.TextButton("❤️", on_click=lambda _: self.on_react(self.message, "❤️")),
                ft.TextButton("😂", on_click=lambda _: self.on_react(self.message, "😂")),
            ]
        )

        self.controls = [
            ft.Row(
                controls=[
                    avatar,
                    ft.Column(
                        controls=[header, content, actions, self.reactions_row, reaction_buttons],
                        spacing=3,
                    ),
                ]
            )
        ]

    def apply_reaction(self, emoji):
        self.reactions[emoji] = self.reactions.get(emoji, 0) + 1
        self.refresh_reactions()

    def refresh_reactions(self):
        self.reactions_row.controls = [
            ft.Container(
                content=ft.Text(f"{emoji} {count}"),
                bgcolor=ft.Colors.GREY_800,
                padding=5,
                border_radius=5,
            )
            for emoji, count in self.reactions.items()
        ]


# ---------------------------------------------------------
#   APLICAÇÃO PRINCIPAL
# ---------------------------------------------------------
def main(page: ft.Page):
    page.title = "Chat Avançado com Tema Escuro e Utilizadores Online"

    user_name = None
    room = "general"
    dark_mode = False

    rooms = ["general", "gaming", "programação"]

    chat = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    current_room_text = ft.Text(f"Sala atual: {room}", weight=ft.FontWeight.BOLD)

    # Lista de utilizadores online por sala
    online_users = {r: [] for r in rooms}
    users_column = ft.Column()

    def update_users_ui():
        users_column.controls = [
            ft.Text("Utilizadores online:", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE if dark_mode else ft.Colors.BLACK)
        ]
        for u in online_users[room]:
            users_column.controls.append(ft.Text(f"• {u}", color=ft.Colors.WHITE if dark_mode else ft.Colors.BLACK))
        page.update()

    # -----------------------------------------------------
    #   Funções auxiliares
    # -----------------------------------------------------
    def find_message_control(msg_id):
        for c in chat.controls:
            if isinstance(c, ChatMessage) and c.message.id == msg_id:
                return c
        return None

    def handle_edit(msg):
        field = ft.TextField(value=msg.text)

        def save(e):
            new_text = field.value.strip()
            if new_text:
                page.pubsub.send_all(
                    Message(
                        user_name=user_name,
                        text=new_text,
                        message_type="edit_message",
                        room=room,
                        target_id=msg.id,
                    )
                )
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Editar"),
            content=field,
            actions=[ft.TextButton("Guardar", on_click=save)],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def handle_delete(msg):
        page.pubsub.send_all(
            Message(
                user_name=user_name,
                message_type="delete_message",
                room=room,
                target_id=msg.id,
            )
        )

    def handle_react(msg, emoji):
        page.pubsub.send_all(
            Message(
                user_name=user_name,
                message_type="reaction",
                room=room,
                target_id=msg.id,
                reaction_emoji=emoji,
            )
        )

    # -----------------------------------------------------
    #   TROCAR DE SALA
    # -----------------------------------------------------
    def change_room(new_room: str):
        nonlocal room
        room = new_room
        current_room_text.value = f"Sala atual: {room}"
        chat.controls.clear()

        # Atualizar lista de utilizadores
        page.pubsub.send_all(
            Message(
                user_name=user_name,
                text="",
                message_type="user_status",
                room=room,
            )
        )

        # Mensagem de entrada
        page.pubsub.send_all(
            Message(
                user_name="",
                text=f"{user_name} entrou na sala {room}.",
                message_type="login_message",
                room=room,
            )
        )

        update_users_ui()
        page.update()

    botoes_salas = ft.Row(
        [
            ft.TextButton("General", on_click=lambda e: change_room("general")),
            ft.TextButton("Gaming", on_click=lambda e: change_room("gaming")),
            ft.TextButton("Programação", on_click=lambda e: change_room("programação")),
        ],
        spacing=10
    )

    # -----------------------------------------------------
    #   TEMA ESCURO
    # -----------------------------------------------------
    def toggle_theme(e):
        nonlocal dark_mode
        dark_mode = not dark_mode

        page.theme_mode = ft.ThemeMode.DARK if dark_mode else ft.ThemeMode.LIGHT

        update_users_ui()
        page.update()

    botao_tema = ft.TextButton("Alternar tema", on_click=toggle_theme)

    # -----------------------------------------------------
    #   RECEBER MENSAGENS
    # -----------------------------------------------------
    def on_message(msg: Message):
        nonlocal user_name, room

        # Atualizar utilizadores online
        if msg.message_type == "user_status":
            for r in rooms:
                if msg.user_name in online_users[r]:
                    online_users[r].remove(msg.user_name)
            online_users[msg.room].append(msg.user_name)
            update_users_ui()
            return

        if msg.room != room and msg.message_type != "login_message":
            return

        if msg.message_type == "private_message":
            if msg.to_user != user_name and msg.user_name != user_name:
                return

        if msg.message_type in ("chat_message", "private_message"):
            chat.controls.append(
                ChatMessage(msg, user_name, dark_mode, handle_edit, handle_delete, handle_react)
            )

        elif msg.message_type == "login_message":
            chat.controls.append(ft.Text(msg.text, italic=True, color=ft.Colors.WHITE if dark_mode else ft.Colors.BLACK))

        elif msg.message_type == "edit_message":
            target = find_message_control(msg.target_id)
            if target:
                target.message.text = msg.text
                target.controls[0].controls[1].controls[1] = ft.Text(msg.text)

        elif msg.message_type == "delete_message":
            target = find_message_control(msg.target_id)
            if target:
                chat.controls.remove(target)

        elif msg.message_type == "reaction":
            target = find_message_control(msg.target_id)
            if target:
                target.apply_reaction(msg.reaction_emoji)

        page.update()

    page.pubsub.subscribe(on_message)

    # -----------------------------------------------------
    #   LOGIN
    # -----------------------------------------------------
    name_field = ft.TextField(label="Nome")
    room_field = ft.Dropdown(
        label="Sala inicial",
        options=[ft.dropdown.Option(r) for r in rooms],
        value="general",
    )

    def join_chat(e):
        nonlocal user_name, room

        if not name_field.value.strip():
            name_field.error_text = "Nome obrigatório"
            name_field.update()
            return

        user_name = name_field.value
        room = room_field.value
        current_room_text.value = f"Sala atual: {room}"

        dialog.open = False

        # Atualizar utilizadores online
        page.pubsub.send_all(
            Message(
                user_name=user_name,
                text="",
                message_type="user_status",
                room=room,
            )
        )

        # Mensagem de entrada
        page.pubsub.send_all(
            Message(
                user_name="",
                text=f"{user_name} entrou na sala {room}.",
                message_type="login_message",
                room=room,
            )
        )

        update_users_ui()
        page.update()

    dialog = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Bem-vindo!"),
        content=ft.Column([name_field, room_field]),
        actions=[ft.TextButton("Entrar", on_click=join_chat)],
    )
    page.overlay.append(dialog)

    # -----------------------------------------------------
    #   ENVIAR MENSAGENS
    # -----------------------------------------------------
    private_to = ft.TextField(label="Privado para (opcional)", width=200)

    async def send_message(e):
        text = msg_field.value.strip()
        if not text:
            return

        to_user = private_to.value.strip() or None
        msg_type = "private_message" if to_user else "chat_message"

        page.pubsub.send_all(
            Message(
                user_name=user_name,
                text=text,
                message_type=msg_type,
                room=room,
                to_user=to_user,
            )
        )

        msg_field.value = ""
        await msg_field.focus()
        page.update()

    msg_field = ft.TextField(
        hint_text="Escreve a mensagem...",
        expand=True,
        shift_enter=True,
        on_submit=send_message,
    )

    # -----------------------------------------------------
    #   LAYOUT FINAL
    # -----------------------------------------------------
    page.add(
        ft.Row([current_room_text, botao_tema]),
        botoes_salas,
        ft.Row(
            [
                ft.Container(users_column, width=200, padding=10),
                ft.Container(chat, expand=True, border=ft.Border.all(1), padding=10),
            ],
            expand=True
        ),
        ft.Row([msg_field, ft.IconButton(icon=ft.Icons.SEND, on_click=send_message)]),
        private_to,
    )


ft.run(main, view=ft.AppView.WEB_BROWSER)
