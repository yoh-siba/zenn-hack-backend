from typing import Optional

from src.config.settings import db
from src.models.exceptions import ServiceException
from src.models.types import TemplatesResponse
from src.services.firebase.schemas.prompt_template_schema import PromptTemplateSchema


async def create_prompt_template_doc(
    template_instance: PromptTemplateSchema,
) -> str:
    try:
        doc_ref = db.collection("prompt_templates")
        new_doc = doc_ref.add(template_instance.to_dict())
        return new_doc[1].id
    except Exception as e:
        raise ServiceException(
            f"プロンプトテンプレートの作成中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def update_prompt_template_doc(
    template_id: str, template_instance: PromptTemplateSchema
) -> None:
    try:
        doc_ref = db.collection("prompt_templates").document(template_id)
        doc_ref.update(template_instance.to_dict())
    except Exception as e:
        raise ServiceException(
            f"プロンプトテンプレートの更新中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def read_prompt_template_doc(
    template_id: str,
) -> Optional[PromptTemplateSchema]:
    try:
        doc_ref = db.collection("prompt_templates").document(template_id)
        doc = doc_ref.get()
        if doc.exists:
            return PromptTemplateSchema.from_dict(doc.to_dict())
        return None
    except Exception as e:
        raise ServiceException(
            f"プロンプトテンプレートの読み込み中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def read_prompt_template_docs() -> list[TemplatesResponse]:
    try:
        docs = db.collection("prompt_templates").get()
        templates = [
            TemplatesResponse.from_dict({**doc.to_dict(), "template_id": doc.id})
            for doc in docs
        ]
        return templates
    except Exception as e:
        raise ServiceException(
            f"プロンプトテンプレートの一括読み込み中にエラーが発生しました: {str(e)}",
            "external_api",
        )
