from typing import Optional, Tuple

from src.config.settings import db
from src.models.types import TemplatesResponse
from src.services.firebase.schemas.prompt_template_schema import PromptTemplateSchema


async def create_prompt_template_doc(
    template_instance: PromptTemplateSchema,
) -> Tuple[bool, Optional[str], Optional[str]]:
    try:
        doc_ref = db.collection("prompt_templates")
        new_doc = doc_ref.add(template_instance.to_dict())
        return True, None, new_doc[1].id
    except Exception as e:
        error_message = (
            f"プロンプトテンプレートの作成中にエラーが発生しました: {str(e)}"
        )
        print(f"\n{error_message}")
        return False, error_message, None


async def update_prompt_template_doc(
    template_id: str, template_instance: PromptTemplateSchema
) -> Tuple[bool, Optional[str]]:
    try:
        doc_ref = db.collection("prompt_templates").document(template_id)
        doc_ref.update(template_instance.to_dict())
        return True, None
    except Exception as e:
        error_message = (
            f"プロンプトテンプレートの更新中にエラーが発生しました: {str(e)}"
        )
        print(f"\n{error_message}")
        return False, error_message


async def read_prompt_template_doc(
    template_id: str,
) -> Tuple[Optional[PromptTemplateSchema], Optional[str]]:
    try:
        doc_ref = db.collection("prompt_templates").document(template_id)
        doc = doc_ref.get()
        if doc.exists:
            return PromptTemplateSchema.from_dict(doc.to_dict()), None
        return None, "指定されたプロンプトテンプレートが見つかりません"
    except Exception as e:
        error_message = (
            f"プロンプトテンプレートの読み込み中にエラーが発生しました: {str(e)}"
        )
        print(f"\n{error_message}")
        return None, error_message


async def read_prompt_template_docs() -> Tuple[list[TemplatesResponse], Optional[str]]:
    try:
        docs = db.collection("prompt_templates").get()
        templates = [
            TemplatesResponse.from_dict({**doc.to_dict(), "template_id": doc.id})
            for doc in docs
        ]
        return templates, None
    except Exception as e:
        error_message = (
            f"プロンプトテンプレートの一括読み込み中にエラーが発生しました: {str(e)}"
        )
        print(f"\n{error_message}")
        return [], error_message
