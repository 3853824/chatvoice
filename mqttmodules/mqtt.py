
import paho.mqtt.client as mqtt

class MQTTSend:
    def __init__(self, IP, USER, PASS, TOPIC,ID=None):
        self.IP = IP
        self.USER = USER
        self.PASS = PASS
        self.TOPIC = TOPIC
        self.ID = ID

    def send_mqtt(self, message):
        if self.ID is None:
            client = mqtt.Client()
        else:
            client = mqtt.Client(client_id=self.ID)
        client.username_pw_set(self.USER, self.PASS)
        client.connect(self.IP, 1883, 60)
        client.publish(self.TOPIC, message)
        client.disconnect()

class MQTTClient:
    def __init__(self, IP, USER, PASS, ID=None, message_callback = None):
        self.ID = ID
        if self.ID is None:
            self.client = mqtt.Client()
        else:
            self.client = mqtt.Client(client_id=self.ID)
        self.IP = IP
        self.USER = USER
        self.PASS = PASS
        self.message_callback = message_callback if message_callback else self.default_message_callback

    def connect(self):
        self.client.username_pw_set(self.USER, self.PASS)
        self.client.on_connect = self.on_connect
        try:
            self.client.connect(self.IP, 1883, 60)
        #    self.client.loop_start()
        except Exception as err:
            print (f"MQTTClient连接失败,信息为: {err}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTTClient连接成功")
        else:
            print(f"MQTTClient连接失败,代码为: {rc}")

    def disconnect(self):
        self.client.disconnect()

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        self.message_callback(topic, payload)

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def start(self):
        # 设置MQTT回调函数
        self.client.on_message = self.on_message
        # 循环运行MQTT客户端
        self.client.loop_forever()

    def default_message_callback(self, topic, message):
        pass

if __name__ == '__main__':
    # 定义消息回调函数
    def display_message(topic, message):
        print("Received message: Topic={}, Payload={}".format(topic, message))

    # 创建MQTT客户端实例，并传入消息回调函数
    client = MQTTClient('192.168.1.1', 'mqtt', 'mqtt', 'id', message_callback = display_message)

    # 连接到MQTT服务器
    client.connect()

    # 订阅主题
    client.subscribe('your/topic')

    # 启动MQTT客户端
    client.start()