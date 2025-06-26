from datetime import datetime
from typing import Optional

from src.config.settings import db
from src.models.exceptions import ServiceException
from src.services.firebase.schemas.comparison_schema import ComparisonSchema


async def create_comparison_doc(
    comparison_instance: ComparisonSchema,
) -> str:
    try:
        doc_ref = db.collection("comparisons")
        new_doc = doc_ref.add(comparison_instance.to_dict())
        return new_doc[1].id
    except Exception as e:
        raise ServiceException(
            f"比較データの作成中にエラーが発生しました: {str(e)}", "external_api"
        )


async def update_comparison_doc(
    comparison_id: str, comparison_instance: ComparisonSchema
) -> None:
    try:
        doc_ref = db.collection("comparisons").document(comparison_id)
        doc_ref.update(comparison_instance.to_dict())
    except Exception as e:
        raise ServiceException(
            f"比較データの更新中にエラーが発生しました: {str(e)}", "external_api"
        )


async def read_comparison_doc(
    comparison_id: str,
) -> Optional[ComparisonSchema]:
    try:
        doc_ref = db.collection("comparisons").document(comparison_id)
        doc = doc_ref.get()
        if doc.exists:
            return ComparisonSchema.from_dict(doc.to_dict())
        return None
    except Exception as e:
        raise ServiceException(
            f"比較データの読み込み中にエラーが発生しました: {str(e)}", "external_api"
        )


async def read_comparison_docs(
    comparison_ids: list[str],
) -> list[ComparisonSchema]:
    try:
        if not comparison_ids:
            raise ServiceException("比較データIDが指定されていません", "validation")

        docs = (
            await db.collection("comparisons")
            .where("__name__", "in", comparison_ids)
            .get()
        )
        comparisons = []
        for doc in docs:
            comparisons.append(ComparisonSchema.from_dict(doc.to_dict()))
        return comparisons
    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(
            f"比較データの一括読み込み中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def update_comparison_doc_on_is_selected_new(
    comparison_id: str, is_selected_new: str
) -> None:
    try:
        now = datetime.now()
        doc_ref = db.collection("comparisons").document(comparison_id)
        doc_ref.update({"isSelectedNew": is_selected_new, "updatedAt": now})
    except Exception as e:
        raise ServiceException(
            f"比較データの更新中にエラーが発生しました: {str(e)}", "external_api"
        )
