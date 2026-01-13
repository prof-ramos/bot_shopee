# Manual de Uso: Evolution Client Python

Este manual documenta o uso da biblioteca Python para interação com a Evolution API.

## Instalação

```bash
pip install evolutionapi
```

## Uso Básico

### Inicializando o Cliente

```python
from evolutionapi.client import EvolutionClient

client = EvolutionClient(
    base_url='http://seu-servidor:porta',
    api_token='seu-api-token'
)
```

### Gerenciamento de Instância

#### Listar Instâncias

```python
instances = client.instances.fetch_instances()
```

#### Criar Nova Instância

```python
from evolutionapi.models.instance import InstanceConfig

# Configuração básica
config = InstanceConfig(
    instanceName="minha-instancia",
    integration="WHATSAPP-BAILEYS",
    qrcode=True
)

# Configuração completa
config = InstanceConfig(
    instanceName="minha-instancia",
    integration="WHATSAPP-BAILEYS",
    token="token_da_instancia",
    number="5511999999999",
    qrcode=True,
    rejectCall=True,
    msgCall="Mensagem de chamada rejeitada",
    groupsIgnore=True,
    alwaysOnline=True,
    readMessages=True,
    readStatus=True,
    syncFullHistory=True
)

new_instance = client.instances.create_instance(config)
```

### Configurar Webhook

```python
from evolutionapi.models.instance import WebhookConfig

config = WebhookConfig(
    url="https://seu-servidor.com/webhook",
    webhook_by_events=True,  # Corrigido para match com API v2
    webhook_base64=True,     # Corrigido para match com API v2
    headers={
        "Authorization": "Bearer seu-token"
    },
    events=[
        "MESSAGES_UPSERT",    # Nomes de eventos atualizados para UPPERCASE conforme v2
        "MESSAGES_UPDATE",
        "MESSAGES_DELETE",
        "GROUPS_UPSERT",
        "GROUP_UPDATE",
        "GROUP_PARTICIPANTS_UPDATE",
        "CONTACTS_UPSERT",
        "CONTACTS_UPDATE",
        "CONTACTS_DELETE",
        "PRESENCE_UPDATE",
        "CHATS_UPSERT",
        "CHATS_UPDATE",
        "CHATS_DELETE",
        "CALL"
    ]
)

response = client.instances.set_webhook(instance_id, config, instance_token)
```

#### Configurar Eventos (Legacy/Opcional)

```python
from evolutionapi.models.instance import EventsConfig

config = EventsConfig(
    enabled=True,
    events=[
        "MESSAGES_UPSERT",
        "MESSAGES_UPDATE",
        "MESSAGES_DELETE",
        "GROUPS_UPSERT",
        "GROUP_UPDATE",
        "GROUP_PARTICIPANTS_UPDATE",
        "CONTACTS_UPSERT",
        "CONTACTS_UPDATE",
        "CONTACTS_DELETE",
        "PRESENCE_UPDATE",
        "CHATS_UPSERT",
        "CHATS_UPDATE",
        "CHATS_DELETE",
        "CALL"
    ]
)

response = client.instances.set_events(instance_id, config, instance_token)
```

#### Configurar Integração Chatwoot

```python
from evolutionapi.models.instance import ChatwootConfig

config = ChatwootConfig(
    accountId="seu-account-id",
    token="seu-token",
    url="https://seu-chatwoot.com",
    signMsg=True,
    reopenConversation=True,
    conversationPending=False,
    importContacts=True,
    nameInbox="evolution",
    mergeBrazilContacts=True,
    importMessages=True,
    daysLimitImportMessages=3,
    organization="Evolution Bot",
    logo="https://evolution-api.com/files/evolution-api-favicon.png"
)

response = client.instances.set_chatwoot(instance_id, config, instance_token)
```

#### Deletar Instância

```python
response = client.instances.delete_instance(instance_id, instance_token)
```

#### Obter Informações da Instância

```python
response = client.instances.get_instance_info(instance_id, instance_token)
```

#### Obter QR Code da Instância

```python
response = client.instances.get_instance_qrcode(instance_id, instance_token)
```

#### Obter Status da Instância

```python
response = client.instances.get_instance_status(instance_id, instance_token)
```

#### Logout da Instância

```python
response = client.instances.logout_instance(instance_id, instance_token)
```

#### Reiniciar Instância

```python
response = client.instances.restart_instance(instance_id, instance_token)
```

### Operações da Instância

#### Conectar Instância

```python
state = client.instance_operations.connect(instance_id, instance_token)
```

#### Verificar Estado da Conexão

```python
state = client.instance_operations.get_connection_state(instance_id, instance_token)
```

#### Definir Presença

```python
from evolutionapi.models.presence import PresenceConfig, PresenceStatus

# Definir como disponível
config = PresenceConfig(
    presence=PresenceStatus.AVAILABLE
)

# Definir como indisponível
config = PresenceConfig(
    presence=PresenceStatus.UNAVAILABLE
)

response = client.instance_operations.set_presence(instance_id, config, instance_token)
```

### Enviando Mensagens

#### Mensagem de Texto

```python
from evolutionapi.models.message import TextMessage, QuotedMessage

# Mensagem simples
message = TextMessage(
    number="5511999999999",
    text="Olá, como você está?",
    delay=1000  # delay opcional em ms
)

# Mensagem com menções
message = TextMessage(
    number="5511999999999",
    text="@everyone Olá a todos!",
    mentionsEveryOne=True,
    mentioned=["5511999999999", "5511888888888"]
)

# Mensagem com prévia de link
message = TextMessage(
    number="5511999999999",
    text="Confira este link: https://exemplo.com",
    linkPreview=True
)

# Mensagem com citação (reply)
quoted = QuotedMessage(
    key={
        "remoteJid": "5511999999999@s.whatsapp.net",
        "fromMe": False,
        "participant": "5511999999999@s.whatsapp.net",
        "id": "123456789",
        "owner": "5511999999999@s.whatsapp.net"
    }
)

message = TextMessage(
    number="5511999999999",
    text="Esta é uma resposta",
    quoted=quoted
)

response = client.messages.send_text(instance_id, message, instance_token)
```

#### Mensagem de Mídia

```python
from evolutionapi.models.message import MediaMessage, MediaType, QuotedMessage

# Mensagem com imagem
message = MediaMessage(
    number="5511999999999",
    mediatype=MediaType.IMAGE.value,
    mimetype="image/jpeg",
    caption="Minha imagem",
    media="base64_da_imagem_ou_url",
    fileName="imagem.jpg",
    delay=1000  # delay opcional
)

# Mensagem com vídeo
message = MediaMessage(
    number="5511999999999",
    mediatype=MediaType.VIDEO.value,
    mimetype="video/mp4",
    caption="Meu vídeo",
    media="base64_do_video_ou_url",
    fileName="video.mp4"
)

# Mensagem com documento
message = MediaMessage(
    number="5511999999999",
    mediatype=MediaType.DOCUMENT.value,
    mimetype="application/pdf",
    caption="Meu documento",
    media="base64_do_documento_ou_url",
    fileName="documento.pdf"
)

# Mensagem com menções
message = MediaMessage(
    number="5511999999999",
    mediatype=MediaType.IMAGE.value,
    mimetype="image/jpeg",
    caption="@everyone Olhem esta imagem!",
    media="base64_da_imagem",
    mentionsEveryOne=True,
    mentioned=["5511999999999", "5511888888888"]
)

response = client.messages.send_media(instance_id, message, instance_token)
```

#### Mensagem de Status (Stories)

```python
from evolutionapi.models.message import StatusMessage, StatusType, FontType

# Status de texto
message = StatusMessage(
    type=StatusType.TEXT,
    content="Meu status de texto",
    caption="Legenda opcional",
    backgroundColor="#FF0000",
    font=FontType.BEBASNEUE_REGULAR,
    allContacts=True
)

# Status de imagem
message = StatusMessage(
    type=StatusType.IMAGE,
    content="base64_da_imagem",
    caption="Minha imagem de status"
)

# Status de vídeo
message = StatusMessage(
    type=StatusType.VIDEO,
    content="base64_do_video",
    caption="Meu vídeo de status"
)

# Status de áudio
message = StatusMessage(
    type=StatusType.AUDIO,
    content="base64_do_audio",
    caption="Meu áudio de status"
)

response = client.messages.send_status(instance_id, message, instance_token)
```

#### Mensagem de Localização

```python
from evolutionapi.models.message import LocationMessage

message = LocationMessage(
    number="5511999999999",
    name="Localização",
    address="Endereço completo",
    latitude=-23.550520,
    longitude=-46.633308,
    delay=1000  # delay opcional
)

response = client.messages.send_location(instance_id, message, instance_token)
```

#### Mensagem de Contato

```python
from evolutionapi.models.message import ContactMessage, Contact

contact = Contact(
    fullName="Nome Completo",
    wuid="5511999999999",
    phoneNumber="5511999999999",
    organization="Empresa",
    email="email@exemplo.com",
    url="https://exemplo.com"
)

message = ContactMessage(
    number="5511999999999",
    contact=[contact]
)

response = client.messages.send_contact(instance_id, message, instance_token)
```

#### Mensagem de Reação

```python
from evolutionapi.models.message import ReactionMessage

message = ReactionMessage(
    key={
        "remoteJid": "5511999999999@s.whatsapp.net",
        "fromMe": False,
        "participant": "5511999999999@s.whatsapp.net",
        "id": "123456789",
        "owner": "5511999999999@s.whatsapp.net"
    },
    reaction="👍"
)

response = client.messages.send_reaction(instance_id, message, instance_token)
```

#### Mensagem de Enquete (Poll)

```python
from evolutionapi.models.message import PollMessage

message = PollMessage(
    number="5511999999999",
    name="Minha Enquete",
    selectableCount=1,  # número de opções que podem ser selecionadas
    values=["Opção 1", "Opção 2", "Opção 3"],
    delay=1000  # delay opcional
)

response = client.messages.send_poll(instance_id, message, instance_token)
```

#### Mensagem de Botão

```python
from evolutionapi.models.message import ButtonMessage, Button

# Botão de resposta simples
buttons = [
    Button(
        type="reply",
        displayText="Opção 1",
        id="1"
    ),
    Button(
        type="reply",
        displayText="Opção 2",
        id="2"
    )
]

# Botão com URL
buttons = [
    Button(
        type="url",
        displayText="Visitar Site",
        url="https://exemplo.com"
    )
]

# Botão com número de telefone
buttons = [
    Button(
        type="phoneNumber",
        displayText="Ligar",
        phoneNumber="5511999999999"
    )
]

# Botão com código de cópia
buttons = [
    Button(
        type="copyCode",
        displayText="Copiar Código",
        copyCode="ABC123"
    )
]

message = ButtonMessage(
    number="5511999999999",
    title="Título",
    description="Descrição",
    footer="Rodapé",
    buttons=buttons,
    delay=1000  # delay opcional
)

response = client.messages.send_buttons(instance_id, message, instance_token)
```

#### Mensagem de Lista

```python
from evolutionapi.models.message import ListMessage, ListSection, ListRow

rows = [
    ListRow(
        title="Item 1",
        description="Descrição do item 1",
        rowId="1"
    ),
    ListRow(
        title="Item 2",
        description="Descrição do item 2",
        rowId="2"
    )
]

section = ListSection(
    title="Seção 1",
    rows=rows
)

message = ListMessage(
    number="5511999999999",
    title="Título da Lista",
    description="Descrição da lista",
    buttonText="Clique aqui",
    footerText="Rodapé",
    sections=[section],
    delay=1000  # delay opcional
)

response = client.messages.send_list(instance_id, message, instance_token)
```

### Gerenciamento de Grupos

#### Criar Grupo

```python
from evolutionapi.models.group import CreateGroup

config = CreateGroup(
    subject="Nome do Grupo",
    participants=["5511999999999", "5511888888888"],
    description="Descrição do grupo"
)

response = client.group.create_group(instance_id, config, instance_token)
```

#### Atualizar Imagem do Grupo

```python
from evolutionapi.models.group import GroupPicture

config = GroupPicture(
    image="base64_da_imagem"
)

response = client.group.update_group_picture(instance_id, "group_jid", config, instance_token)
```

#### Atualizar Nome (Subject) do Grupo

```python
from evolutionapi.models.group import GroupSubject

config = GroupSubject(
    subject="Novo Nome do Grupo"
)

response = client.group.update_group_subject(instance_id, "group_jid", config, instance_token)
```

#### Atualizar Descrição do Grupo

```python
from evolutionapi.models.group import GroupDescription

config = GroupDescription(
    description="Nova descrição do grupo"
)

response = client.group.update_group_description(instance_id, "group_jid", config, instance_token)
```

#### Enviar Convite de Grupo

```python
from evolutionapi.models.group import GroupInvite

config = GroupInvite(
    groupJid="group_jid",
    description="Convite para o grupo",
    numbers=["5511999999999", "5511888888888"]
)

response = client.group.send_group_invite(instance_id, config, instance_token)
```

#### Gerenciar Participantes

```python
from evolutionapi.models.group import UpdateParticipant

# Adicionar participantes
config = UpdateParticipant(
    action="add",
    participants=["5511999999999", "5511888888888"]
)

# Remover participantes
config = UpdateParticipant(
    action="remove",
    participants=["5511999999999"]
)

# Promover a administrador
config = UpdateParticipant(
    action="promote",
    participants=["5511999999999"]
)

# Rebaixar de administrador
config = UpdateParticipant(
    action="demote",
    participants=["5511999999999"]
)

response = client.group.update_participant(instance_id, "group_jid", config, instance_token)
```

#### Atualizar Configurações de Grupo

```python
from evolutionapi.models.group import UpdateSetting

# Ativar modo anúncio (apenas admins falam)
config = UpdateSetting(
    action="announcement"
)

# Desativar modo anúncio
config = UpdateSetting(
    action="not_announcement"
)

# Bloquear grupo (impedir edição de dados do grupo)
config = UpdateSetting(
    action="locked"
)

# Desbloquear grupo
config = UpdateSetting(
    action="unlocked"
)

response = client.group.update_setting(instance_id, "group_jid", config, instance_token)
```

#### Alternar Mensagens Efêmeras (Temporárias)

```python
from evolutionapi.models.group import ToggleEphemeral

config = ToggleEphemeral(
    expiration=86400  # 24 horas em segundos
)

response = client.group.toggle_ephemeral(instance_id, "group_jid", config, instance_token)
```

### Gerenciamento de Perfil

#### Buscar Perfil

```python
from evolutionapi.models.profile import FetchProfile

config = FetchProfile(
    number="5511999999999"
)

response = client.profile.fetch_profile(instance_id, config, instance_token)
```

#### Atualizar Nome do Perfil

```python
from evolutionapi.models.profile import ProfileName

config = ProfileName(
    name="Novo Nome"
)

response = client.profile.update_profile_name(instance_id, config, instance_token)
```

#### Atualizar Status (Recado)

```python
from evolutionapi.models.profile import ProfileStatus

config = ProfileStatus(
    status="Novo status"
)

response = client.profile.update_profile_status(instance_id, config, instance_token)
```

#### Atualizar Foto de Perfil

```python
from evolutionapi.models.profile import ProfilePicture

config = ProfilePicture(
    picture="base64_da_imagem"
)

response = client.profile.update_profile_picture(instance_id, config, instance_token)
```

#### Configurar Privacidade

```python
from evolutionapi.models.profile import PrivacySettings

config = PrivacySettings(
    readreceipts="all",           # "all" ou "none"
    profile="contacts",           # "all", "contacts", "contact_blacklist" ou "none"
    status="contacts",            # "all", "contacts", "contact_blacklist" ou "none"
    online="all",                 # "all" ou "match_last_seen"
    last="contacts",              # "all", "contacts", "contact_blacklist" ou "none"
    groupadd="contacts"           # "all", "contacts" ou "contact_blacklist"
)

response = client.profile.update_privacy_settings(instance_id, config, instance_token)
```

### Operações de Chat

#### Verificar Números no WhatsApp

```python
from evolutionapi.models.chat import CheckIsWhatsappNumber

config = CheckIsWhatsappNumber(
    numbers=["5511999999999", "5511888888888"]
)

response = client.chat.check_is_whatsapp_numbers(instance_id, config, instance_token)
```

#### Marcar Mensagem como Lida

```python
from evolutionapi.models.chat import ReadMessage

message = ReadMessage(
    remote_jid="5511999999999@s.whatsapp.net",
    from_me=False,
    id="message_id"
)

response = client.chat.mark_message_as_read(instance_id, [message], instance_token)
```

#### Arquivar Chat

```python
from evolutionapi.models.chat import ArchiveChat

config = ArchiveChat(
    last_message={
        "key": {
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": False,
            "id": "message_id",
            "participant": "5511999999999@s.whatsapp.net"
        },
        "message": {
            "conversation": "Última mensagem"
        }
    },
    chat="5511999999999@s.whatsapp.net",
    archive=True  # True para arquivar, False para desarquivar
)

response = client.chat.archive_chat(instance_id, config, instance_token)
```

#### Marcar Chat como Não Lido

```python
from evolutionapi.models.chat import UnreadChat

config = UnreadChat(
    last_message={
        "key": {
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": False,
            "id": "message_id",
            "participant": "5511999999999@s.whatsapp.net"
        },
        "message": {
            "conversation": "Última mensagem"
        }
    },
    chat="5511999999999@s.whatsapp.net"
)

response = client.chat.unread_chat(instance_id, config, instance_token)
```

#### Obter Foto de Perfil do Chat

```python
from evolutionapi.models.chat import ProfilePicture

config = ProfilePicture(
    number="5511999999999"
)

response = client.chat.get_chat_profile_picture(instance_id, config, instance_token)
```

#### Baixar Mensagem de Mídia

```python
from evolutionapi.models.chat import MediaMessage

config = MediaMessage(
    message={
        "key": {
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": False,
            "id": "message_id",
            "participant": "5511999999999@s.whatsapp.net"
        },
        "message": {
            "imageMessage": {
                "jpegThumbnail": "base64_da_imagem"
            }
        }
    },
    convert_to_mp4=True  # opcional, para converter vídeos para MP4
)

response = client.chat.download_media_message(instance_id, config, instance_token)
```

#### Atualizar Mensagem

```python
from evolutionapi.models.chat import UpdateMessage

config = UpdateMessage(
    number="5511999999999",
    key={
        "remoteJid": "5511999999999@s.whatsapp.net",
        "fromMe": False,
        "id": "message_id",
        "participant": "5511999999999@s.whatsapp.net"
    },
    text="Mensagem atualizada"
)

response = client.chat.update_message(instance_id, config, instance_token)
```

#### Definir Presença (Digitando/Gravando)

```python
from evolutionapi.models.chat import Presence

config = Presence(
    number="5511999999999",
    delay=1000,  # delay em ms
    presence="composing"  # "composing", "recording", "paused"
)

response = client.chat.set_presence(instance_id, config, instance_token)
```

### Chamadas

#### Simular Chamada

```python
from evolutionapi.models.call import FakeCall

# Chamada de voz
config = FakeCall(
    number="5511999999999",
    isVideo=False,
    callDuration=30  # duração em segundos
)

# Chamada de vídeo
config = FakeCall(
    number="5511999999999",
    isVideo=True,
    callDuration=30  # duração em segundos
)

response = client.calls.fake_call(instance_id, config, instance_token)
```

### Etiquetas (Labels)

#### Gerenciar Etiquetas

```python
from evolutionapi.models.label import HandleLabel

# Adicionar etiqueta
config = HandleLabel(
    number="5511999999999",
    label_id="label_id",
    action="add"
)

# Remover etiqueta
config = HandleLabel(
    number="5511999999999",
    label_id="label_id",
    action="remove"
)

response = client.label.handle_label(instance_id, config, instance_token)
```

## WebSocket

O cliente Evolution API suporta conexão WebSocket para receber eventos em tempo real. Aqui está um
guia de como utilizá-lo:

### Pré-requisitos

Antes de usar o WebSocket, você precisa:

1. Ativar o WebSocket na sua Evolution API definindo a variável de ambiente:

```bash
WEBSOCKET_ENABLED=true
```

2. Configurar eventos de WebSocket para sua instância usando o serviço WebSocket:

```python
from evolutionapi.models.websocket import WebSocketConfig

# Configurar eventos de WebSocket
config = WebSocketConfig(
    enabled=True,
    events=[
        "APPLICATION_STARTUP",
        "QRCODE_UPDATED",
        "MESSAGES_SET",
        "MESSAGES_UPSERT",
        "MESSAGES_UPDATE",
        "MESSAGES_DELETE",
        "SEND_MESSAGE",
        "CONTACTS_SET",
        "CONTACTS_UPSERT",
        "CONTACTS_UPDATE",
        "PRESENCE_UPDATE",
        "CHATS_SET",
        "CHATS_UPSERT",
        "CHATS_UPDATE",
        "CHATS_DELETE",
        "GROUPS_UPSERT",
        "GROUP_UPDATE",
        "GROUP_PARTICIPANTS_UPDATE",
        "CONNECTION_UPDATE",
        "LABELS_EDIT",
        "LABELS_ASSOCIATION",
        "CALL",
        "TYPEBOT_START",
        "TYPEBOT_CHANGE_STATUS"
    ]
)

# Definir configuração de WebSocket
response = client.websocket.set_websocket(instance_id, config, instance_token)

# Obter configuração atual do WebSocket
websocket_info = client.websocket.find_websocket(instance_id, instance_token)
print(f"WebSocket ativado: {websocket_info.enabled}")
print(f"Eventos configurados: {websocket_info.events}")
```

### Configuração Básica

Existem duas maneiras de criar um gerenciador de WebSocket:

1. Usando o método auxiliar do cliente (recomendado):

```python
# Criar gerenciador de WebSocket usando o cliente
websocket = client.create_websocket(
    instance_id="test",
    api_token="seu_api_token",
    max_retries=5,        # Número máximo de tentativas de reconexão
    retry_delay=1.0       # Delay inicial entre tentativas em segundos
)
```

2. Criando o gerenciador diretamente:

```python
from evolutionapi.client import EvolutionClient
import logging

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Inicializar cliente
client = EvolutionClient(
    base_url="http://localhost:8081",
    api_token="seu-api-token"
)

# Criar gerenciador de WebSocket
websocket = client.create_websocket(
    instance_id="test",
    api_token="seu-api-token",
    max_retries=5,
    retry_delay=1.0
)
```

### Registrando Manipuladores de Eventos (Handlers)

Você pode registrar manipuladores para diferentes tipos de eventos:

```python
def handle_message(data):
    print(f"Nova mensagem recebida: {data}")

def handle_qrcode(data):
    print(f"QR Code atualizado: {data}")

# Registrando manipuladores
websocket.on("messages.upsert", handle_message)
websocket.on("qrcode.updated", handle_qrcode)
```

### Eventos Disponíveis

Os eventos disponíveis são:

#### Eventos de Instância

- `application.startup`: Disparado quando a aplicação inicia
- `instance.create`: Disparado quando uma nova instância é criada
- `instance.delete`: Disparado quando uma instância é deletada
- `remove.instance`: Disparado quando uma instância é removida
- `logout.instance`: Disparado quando uma instância faz logout

#### Eventos de Conexão e QR Code

- `qrcode.updated`: Disparado quando o QR Code é atualizado
- `connection.update`: Disparado quando o status da conexão muda
- `status.instance`: Disparado quando o status da instância muda
- `creds.update`: Disparado quando credenciais são atualizadas

#### Eventos de Mensagem

- `messages.set`: Disparado quando mensagens são definidas
- `messages.upsert`: Disparado quando novas mensagens são recebidas
- `messages.edited`: Disparado quando mensagens são editadas
- `messages.update`: Disparado quando mensagens são atualizadas
- `messages.delete`: Disparado quando mensagens são deletadas
- `send.message`: Disparado quando uma mensagem é enviada
- `messaging-history.set`: Disparado quando o histórico de mensagens é definido

#### Eventos de Contato

- `contacts.set`: Disparado quando contatos são definidos
- `contacts.upsert`: Disparado quando novos contatos são adicionados
- `contacts.update`: Disparado quando contatos são atualizados

#### Eventos de Chat

- `chats.set`: Disparado quando chats são definidos
- `chats.update`: Disparado quando chats são atualizados
- `chats.upsert`: Disparado quando novos chats são adicionados
- `chats.delete`: Disparado quando chats são deletados

#### Eventos de Grupo

- `groups.upsert`: Disparado quando grupos são criados/atualizados
- `groups.update`: Disparado quando grupos são atualizados
- `group-participants.update`: Disparado quando participantes do grupo são atualizados

#### Eventos de Presença

- `presence.update`: Disparado quando o status de presença é atualizado

#### Eventos de Chamada

- `call`: Disparado quando há uma chamada

#### Eventos Typebot

- `typebot.start`: Disparado quando um typebot inicia
- `typebot.change-status`: Disparado quando o status do typebot muda

#### Eventos de Etiqueta (Label)

- `labels.edit`: Disparado quando etiquetas são editadas
- `labels.association`: Disparado quando etiquetas são associadas/desassociadas

### Exemplo com Eventos Específicos

```python
def handle_messages(data):
    logger.info(f"Nova mensagem: {data}")

def handle_contacts(data):
    logger.info(f"Contatos atualizados: {data}")

def handle_groups(data):
    logger.info(f"Grupos atualizados: {data}")

def handle_presence(data):
    logger.info(f"Status de presença: {data}")

# Registrando manipuladores para diferentes eventos
websocket.on("messages.upsert", handle_messages)
websocket.on("contacts.upsert", handle_contacts)
websocket.on("groups.upsert", handle_groups)
websocket.on("presence.update", handle_presence)
```

### Exemplo Completo do WebSocket

```python
from evolutionapi.client import EvolutionClient
from evolutionapi.models.websocket import WebSocketConfig
import logging
import time

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def handle_message(data):
    logger.info(f"Nova mensagem recebida: {data}")

def handle_qrcode(data):
    logger.info(f"QR Code atualizado: {data}")

def handle_connection(data):
    logger.info(f"Status da conexão: {data}")

def main():
    # Inicializar cliente
    client = EvolutionClient(
        base_url="http://localhost:8081",
        api_token="seu-api-token"
    )

    # Configurar WebSocket
    websocket_config = WebSocketConfig(
        enabled=True,
        events=[
            "MESSAGES_UPSERT",
            "QRCODE_UPDATED",
            "CONNECTION_UPDATE"
        ]
    )

    # Definir configuração de WebSocket
    client.websocket.set_websocket("instance_id", websocket_config, "instance_token")

    # Criar gerenciador de WebSocket
    websocket = client.create_websocket(
        instance_id="instance_id",
        api_token="seu-api-token",
        max_retries=5,
        retry_delay=1.0
    )

    # Registrar manipuladores
    websocket.on("messages.upsert", handle_message)
    websocket.on("qrcode.updated", handle_qrcode)
    websocket.on("connection.update", handle_connection)

    try:
        # Conectar ao WebSocket
        websocket.connect()
        logger.info("Conectado ao WebSocket. Aguardando eventos...")

        # Manter o programa rodando
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Fechando conexão...")
        websocket.disconnect()
    except Exception as e:
        logger.error(f"Erro: {e}")
        websocket.disconnect()

if __name__ == "__main__":
    main()
```

### Recursos Adicionais

#### Reconexão Automática

O WebSocket Manager possui reconexão automática com backoff exponencial (espera gradual):

```python
websocket = client.create_websocket(
    instance_id="test",
    api_token="seu-api-token",
    max_retries=5,        # Número máximo de tentativas de reconexão
    retry_delay=1.0       # Delay inicial entre tentativas em segundos
)
```

#### Logs

O WebSocket Manager usa o sistema de logging do Python. Você pode ajustar o nível de log conforme
necessário:

```python
# Para mais detalhes
logging.getLogger("evolutionapi.services.websocket").setLevel(logging.DEBUG)
```

### Tratamento de Erros

O WebSocket Manager possui tratamento robusto de erros:

- Reconexão automática em caso de desconexão
- Logs de erro detalhados
- Tratamento de eventos inválidos
- Validação de dados

### Dicas de Uso

1. Sempre use try/except ao conectar ao WebSocket
2. Implemente manipuladores para todos os eventos que você precisa monitorar
3. Use logs para depuração e monitoramento
4. Considere implementar um mecanismo de "heartbeat" se necessário
5. Mantenha seu token de API seguro e não o exponha em logs
