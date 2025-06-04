"""
多提供商语音识别客户端
支持本地 Whisper、OpenAI、腾讯云、阿里云、百度云等多个语音识别服务
"""

import os
import logging
from typing import Optional
from abc import ABC, abstractmethod
from config import Config

logger = logging.getLogger(__name__)

class SpeechRecognitionProvider(ABC):
    """语音识别提供商基类"""
    
    @abstractmethod
    def transcribe(self, audio_file_path: str) -> Optional[str]:
        """转录音频文件为文本"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """测试连接是否正常"""
        pass

class LocalWhisperProvider(SpeechRecognitionProvider):
    """本地 Whisper 提供商"""
    
    def __init__(self):
        try:
            import whisper
            self.whisper = whisper
            logger.info(f"加载本地 Whisper 模型：{Config.WHISPER_MODEL}")
            self.model = whisper.load_model(Config.WHISPER_MODEL)
            logger.info("本地 Whisper 模型加载成功")
        except ImportError:
            logger.error("未安装 openai-whisper，请运行: pip install openai-whisper")
            raise
        except Exception as e:
            logger.error(f"加载本地 Whisper 模型失败：{str(e)}")
            raise
    
    def transcribe(self, audio_file_path: str) -> Optional[str]:
        try:
            result = self.model.transcribe(
                audio_file_path,
                language=Config.SPEECH_LANGUAGE.split('-')[0] if Config.SPEECH_LANGUAGE else None,
                fp16=False
            )
            
            text = result.get('text', '').strip()
            if text:
                logger.info(f"本地 Whisper 转录成功：{text[:50]}...")
                return text
            else:
                logger.warning("本地 Whisper 返回空文本")
                return None
                
        except Exception as e:
            logger.error(f"本地 Whisper 转录失败：{str(e)}")
            return None
    
    def test_connection(self) -> bool:
        return self.model is not None

class OpenAIProvider(SpeechRecognitionProvider):
    """OpenAI Whisper API 提供商"""
    
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("使用 OpenAI API 需要设置 OPENAI_API_KEY")
        
        try:
            import openai
            self.openai = openai
            openai.api_key = Config.OPENAI_API_KEY
            logger.info("OpenAI Whisper API 初始化成功")
        except ImportError:
            logger.error("未安装 openai，请运行: pip install openai")
            raise
    
    def transcribe(self, audio_file_path: str) -> Optional[str]:
        try:
            with open(audio_file_path, 'rb') as audio_file:
                response = self.openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    language=Config.SPEECH_LANGUAGE.split('-')[0] if Config.SPEECH_LANGUAGE else None
                )
            
            text = response.get('text', '').strip()
            if text:
                logger.info(f"OpenAI API 转录成功：{text[:50]}...")
                return text
            else:
                logger.warning("OpenAI API 返回空文本")
                return None
                
        except Exception as e:
            logger.error(f"OpenAI API 转录失败：{str(e)}")
            return None
    
    def test_connection(self) -> bool:
        try:
            # 简单的 API 测试
            models = self.openai.Model.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI API 连接测试失败：{str(e)}")
            return False

class TencentProvider(SpeechRecognitionProvider):
    """腾讯云语音识别提供商"""
    
    def __init__(self):
        if not Config.TENCENT_SECRET_ID or not Config.TENCENT_SECRET_KEY:
            raise ValueError("使用腾讯云 API 需要设置 TENCENT_SECRET_ID 和 TENCENT_SECRET_KEY")
        
        try:
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
            from tencentcloud.asr.v20190614 import asr_client, models
            
            self.credential = credential.Credential(Config.TENCENT_SECRET_ID, Config.TENCENT_SECRET_KEY)
            self.http_profile = HttpProfile()
            self.http_profile.endpoint = "asr.tencentcloudapi.com"
            
            self.client_profile = ClientProfile()
            self.client_profile.httpProfile = self.http_profile
            
            self.client = asr_client.AsrClient(self.credential, Config.TENCENT_REGION, self.client_profile)
            self.models = models
            
            logger.info("腾讯云语音识别 API 初始化成功")
        except ImportError:
            logger.error("未安装腾讯云 SDK，请运行: pip install tencentcloud-sdk-python")
            raise
    
    def transcribe(self, audio_file_path: str) -> Optional[str]:
        try:
            import base64
            
            # 读取音频文件并转换为 base64
            with open(audio_file_path, 'rb') as f:
                audio_data = f.read()
            
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 创建请求
            req = self.models.CreateRecTaskRequest()
            params = {
                "EngineModelType": "16k_zh",
                "ChannelNum": 1,
                "ResTextFormat": 0,
                "SourceType": 1,
                "Data": audio_base64
            }
            req.from_json_string(str(params).replace("'", '"'))
            
            # 发送请求
            resp = self.client.CreateRecTask(req)
            
            # 解析响应
            if resp.Data and resp.Data.Result:
                text = resp.Data.Result.strip()
                if text:
                    logger.info(f"腾讯云 API 转录成功：{text[:50]}...")
                    return text
            
            logger.warning("腾讯云 API 返回空文本")
            return None
            
        except Exception as e:
            logger.error(f"腾讯云 API 转录失败：{str(e)}")
            return None
    
    def test_connection(self) -> bool:
        try:
            # 简单的连接测试
            req = self.models.DescribeTaskStatusRequest()
            req.TaskId = 0  # 使用无效 ID 测试连接
            self.client.DescribeTaskStatus(req)
            return True
        except Exception as e:
            # 预期会失败，但如果是认证错误则说明连接有问题
            if "AuthFailure" in str(e):
                logger.error(f"腾讯云 API 认证失败：{str(e)}")
                return False
            return True  # 其他错误说明连接正常

class AliyunProvider(SpeechRecognitionProvider):
    """阿里云语音识别提供商"""
    
    def __init__(self):
        if not Config.ALIYUN_ACCESS_KEY_ID or not Config.ALIYUN_ACCESS_KEY_SECRET:
            raise ValueError("使用阿里云 API 需要设置 ALIYUN_ACCESS_KEY_ID 和 ALIYUN_ACCESS_KEY_SECRET")
        
        try:
            import alibabacloud_nls_meta20190103
            from alibabacloud_tea_openapi import models as open_api_models
            
            config = open_api_models.Config(
                access_key_id=Config.ALIYUN_ACCESS_KEY_ID,
                access_key_secret=Config.ALIYUN_ACCESS_KEY_SECRET
            )
            config.endpoint = 'nls-meta.cn-shanghai.aliyuncs.com'
            
            self.client = alibabacloud_nls_meta20190103.Client(config)
            logger.info("阿里云语音识别 API 初始化成功")
        except ImportError:
            logger.error("未安装阿里云 SDK，请运行: pip install alibabacloud_nls_meta20190103")
            raise
    
    def transcribe(self, audio_file_path: str) -> Optional[str]:
        try:
            # 阿里云语音识别实现
            # 注意：这里需要根据阿里云的具体 API 文档实现
            logger.warning("阿里云语音识别暂未完全实现，请参考官方文档")
            return None
        except Exception as e:
            logger.error(f"阿里云 API 转录失败：{str(e)}")
            return None
    
    def test_connection(self) -> bool:
        return False  # 暂未实现

class BaiduProvider(SpeechRecognitionProvider):
    """百度云语音识别提供商"""
    
    def __init__(self):
        if not Config.BAIDU_API_KEY or not Config.BAIDU_SECRET_KEY:
            raise ValueError("使用百度云 API 需要设置 BAIDU_API_KEY 和 BAIDU_SECRET_KEY")
        
        try:
            from aip import AipSpeech
            
            self.client = AipSpeech(
                "your_app_id",  # 需要在配置中添加
                Config.BAIDU_API_KEY,
                Config.BAIDU_SECRET_KEY
            )
            logger.info("百度云语音识别 API 初始化成功")
        except ImportError:
            logger.error("未安装百度 SDK，请运行: pip install baidu-aip")
            raise
    
    def transcribe(self, audio_file_path: str) -> Optional[str]:
        try:
            # 读取音频文件
            with open(audio_file_path, 'rb') as f:
                audio_data = f.read()
            
            # 调用百度 API
            result = self.client.asr(audio_data, 'wav', 16000, {
                'dev_pid': 1537,  # 中文普通话
            })
            
            if result.get('err_no') == 0 and result.get('result'):
                text = ''.join(result['result']).strip()
                if text:
                    logger.info(f"百度云 API 转录成功：{text[:50]}...")
                    return text
            
            logger.warning("百度云 API 返回空文本")
            return None
            
        except Exception as e:
            logger.error(f"百度云 API 转录失败：{str(e)}")
            return None
    
    def test_connection(self) -> bool:
        try:
            # 简单的连接测试
            result = self.client.asr(b'', 'wav', 16000, {})
            return True
        except Exception as e:
            logger.error(f"百度云 API 连接测试失败：{str(e)}")
            return False

class SpeechRecognitionClient:
    """语音识别客户端工厂"""

    def __init__(self):
        self.provider = self._create_provider()

    def _create_provider(self) -> SpeechRecognitionProvider:
        """根据配置创建对应的提供商"""
        provider_name = Config.SPEECH_PROVIDER.lower()

        try:
            if provider_name == 'local_whisper':
                return LocalWhisperProvider()
            elif provider_name == 'openai':
                return OpenAIProvider()
            elif provider_name == 'tencent':
                return TencentProvider()
            elif provider_name == 'aliyun':
                return AliyunProvider()
            elif provider_name == 'baidu':
                return BaiduProvider()
            else:
                logger.warning(f"未知的语音识别提供商：{provider_name}，使用本地 Whisper")
                return LocalWhisperProvider()
        except Exception as e:
            logger.error(f"创建语音识别提供商失败：{str(e)}")
            logger.info("回退到本地 Whisper")
            return LocalWhisperProvider()

    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """转录音频文件"""
        try:
            if not os.path.exists(audio_file_path):
                logger.error(f"音频文件不存在：{audio_file_path}")
                return None

            logger.info(f"使用 {Config.SPEECH_PROVIDER} 进行语音识别")
            text = self.provider.transcribe(audio_file_path)

            return text

        except Exception as e:
            logger.error(f"音频转录失败：{str(e)}")
            return None
        finally:
            # 清理临时音频文件
            self._cleanup_audio_file(audio_file_path)

    def test_connection(self) -> bool:
        """测试连接"""
        try:
            return self.provider.test_connection()
        except Exception as e:
            logger.error(f"连接测试失败：{str(e)}")
            return False

    def _cleanup_audio_file(self, audio_file_path: str):
        """清理临时音频文件"""
        try:
            if not Config.SAVE_AUDIO_FILES and os.path.exists(audio_file_path):
                os.remove(audio_file_path)
                logger.debug(f"已删除临时音频文件：{audio_file_path}")
        except Exception as e:
            logger.warning(f"删除临时音频文件失败：{str(e)}")

    def get_provider_info(self) -> dict:
        """获取当前提供商信息"""
        return {
            'provider': Config.SPEECH_PROVIDER,
            'language': Config.SPEECH_LANGUAGE,
            'model': getattr(Config, 'WHISPER_MODEL', None) if Config.SPEECH_PROVIDER == 'local_whisper' else None,
            'connected': self.test_connection()
        }
