"""
サービス層で使用する例外クラス
"""


class ServiceException(Exception):
    """
    サービス層でのビジネスロジックエラーを表現する例外クラス
    
    Attributes:
        message (str): エラーメッセージ
        error_type (str): エラータイプ
    """
    
    def __init__(self, message: str, error_type: str = "general"):
        """
        ServiceExceptionを初期化する
        
        Args:
            message (str): エラーメッセージ
            error_type (str): エラータイプ。以下のいずれかを指定:
                - "not_found": リソースが見つからない (404)
                - "validation": バリデーションエラー (400)
                - "permission": 権限エラー (403)
                - "conflict": 競合エラー (409)
                - "external_api": 外部APIエラー (502)
                - "general": 一般的な内部エラー (500)
        """
        super().__init__(message)
        self.message = message
        self.error_type = error_type

    def __str__(self) -> str:
        return f"[{self.error_type}] {self.message}"

    def __repr__(self) -> str:
        return f"ServiceException(message='{self.message}', error_type='{self.error_type}')"