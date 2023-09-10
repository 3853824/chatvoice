
class Config:

    REPLYING: bool = False

    # 唤醒配置
    PICOVOICE_API_KEY = "pcPCgVi24x1PlBNvRftPfEX6jFbR7hkrCImS0vdGnNREIlfs9OzTzg=="
    keyword_path = './speechmodules/hi-moss_en_raspberry-pi_v2_2_0.ppn'

    # 百度ASR配置
    BD_APP_ID = '34381280'
    BD_API_KEY = 'yUurDA7RPw31mPKRPpuw9HPm'
    BD_SECRET_KEY = 'Iu3TBTqGtgkr5swQG3SuZ6PDzxQqMSbV'

    # TTS配置
    voice = "zh-CN-XiaoyiNeural"

    #mqtt配置
    MQTT_ENABLE = True
    SEND_TO_MQTT = False
    MQTT_IP = "10.10.10.61"
    MQTT_USER = "jsfer888"
    MQTT_PASS = "wuguibing888"
    MQTT_TOPIC = "pytest/keting"
    MQTT_ID = "pytest"

    # OPENAI配置
    OPENAI_API_KEY = "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"
    OPENAI_API_BASE = "https://api.openai-sb.com/v1"
    OPENAI_PREVIOUS_MESSAGES_COUNT: int = 5  # 0 means no contextual conversation
    OPENAI_PREVIOUS_MESSAGES_SAVE_REPLY = True
    OPENAI_SYSTEM_PROMPT = "你叫MOSS，我叫小桂，你是我的好朋友，请使用简洁的语音来回复我"
