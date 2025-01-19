from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def activate_table_trigger():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "table_updates",
        {
            "type": "table_update",
            "message": "Banco de dados alterado!",
        },
    )
