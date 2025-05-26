from typing import Optional, Tuple

from src.config.settings import db
from src.services.firestore.schemas.comparison_schema import ComparisonSchema


async def create_comparison_doc(
    comparison_instance: ComparisonSchema,
) -> Tuple[bool, Optional[str], Optional[str]]:
    try:
        doc_ref = db.collection("comparisons")
        new_doc = await doc_ref.add(comparison_instance.to_dict())
        return True, None, new_doc[1].id
    except Exception as e:
        error_message = f"比較データの作成中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None


async def update_comparison_doc(
    comparison_id: str, comparison_instance: ComparisonSchema
) -> Tuple[bool, Optional[str]]:
    try:
        doc_ref = db.collection("comparisons").document(comparison_id)
        await doc_ref.update(comparison_instance.to_dict())
        return True, None
    except Exception as e:
        error_message = f"比較データの更新中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message


async def read_comparison_doc(
    comparison_id: str,
) -> Tuple[Optional[ComparisonSchema], Optional[str]]:
    try:
        doc_ref = db.collection("comparisons").document(comparison_id)
        doc = await doc_ref.get()
        if doc.exists:
            return ComparisonSchema.from_dict(doc.to_dict()), None
        return None, "指定された比較データが見つかりません"
    except Exception as e:
        error_message = f"比較データの読み込み中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return None, error_message


async def read_comparison_docs(
    comparison_ids: list[str],
) -> Tuple[list[ComparisonSchema], Optional[str]]:
    try:
        if not comparison_ids:
            return [], "比較データIDが指定されていません"

        docs = (
            await db.collection("comparisons")
            .where("__name__", "in", comparison_ids)
            .get()
        )
        comparisons = []
        for doc in docs:
            comparisons.append(ComparisonSchema.from_dict(doc.to_dict()))
        return comparisons, None
    except Exception as e:
        error_message = f"比較データの一括読み込み中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return [], error_message
