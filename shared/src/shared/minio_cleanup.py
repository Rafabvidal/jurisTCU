import re

from shared.constants import PDF_BUCKET
from shared.s3_client import S3Client, get_s3_client

VALID_PDF_OBJECT_NAME = re.compile(r"^\d+_\d+\.pdf$")


def cleanup_minio_pdf_objects(
    bucket_name: str = PDF_BUCKET,
    client: S3Client | None = None,
    dry_run: bool = False,
) -> dict:
    client = client or get_s3_client()
    objects = client.list_objects(bucket_name)

    seen: set[str] = set()
    removed_invalid: list[str] = []
    removed_duplicates: list[str] = []

    for obj in objects:
        object_name = obj.object_name

        if not VALID_PDF_OBJECT_NAME.match(object_name):
            removed_invalid.append(object_name)
            if not dry_run:
                client.delete_object(bucket_name, object_name)
            continue

        if object_name in seen:
            removed_duplicates.append(object_name)
            if not dry_run:
                client.delete_object(bucket_name, object_name)
            continue

        seen.add(object_name)

    return {
        "bucket": bucket_name,
        "total": len(objects),
        "removed": len(removed_invalid) + len(removed_duplicates),
        "invalid_removed": len(removed_invalid),
        "duplicate_removed": len(removed_duplicates),
        "invalid_objects": removed_invalid,
        "duplicate_objects": removed_duplicates,
        "dry_run": dry_run,
    }
