from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

class MyConsumer(JsonWebsocketConsumer):
    groups = ["broadcast"]

    def connect(self):
        self.accept()

    def receive(self, text_data=None, bytes_data=None):

        print("Websocket message recieved")

        # Broadcast the information to the group
        async_to_sync(self.channel_layer.group_send)(
            "broadcast",
            {
                "type" : "broadcast_message", 
                "text" : text_data,
                "sender" : self.channel_name
            }
        )


    def disconnect(self, close_code):
        # Called when the socket closes
        pass


    def broadcast_message(self,event):

        print("Broadcast Message recieved")

        if(event["sender"] != self.channel_name):

            self.send_json(
                {
                    "type": "websocket.send",
                    "text" : event["text"]
                }
            )
