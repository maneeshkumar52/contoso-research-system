"""Saves research reports to Cosmos DB and Azure Blob Storage."""
import json
import structlog
from shared.config import get_settings
from shared.models import FinalReport

logger = structlog.get_logger(__name__)


async def store_report(report: FinalReport) -> str:
    """
    Store the final research report in Cosmos DB and Blob Storage.

    Args:
        report: The completed research report.

    Returns:
        Storage URL or Cosmos document ID.
    """
    settings = get_settings()
    doc_id = report.run_id

    # Store in Cosmos DB
    try:
        from azure.cosmos.aio import CosmosClient
        async with CosmosClient(url=settings.cosmos_endpoint, credential=settings.cosmos_key) as client:
            db = client.get_database_client(settings.cosmos_database)
            container = db.get_container_client(settings.cosmos_reports_container)

            doc = report.model_dump()
            doc["id"] = doc_id
            doc["created_at"] = doc["created_at"].isoformat()
            doc["synthesis"] = doc["synthesis"]

            await container.create_item(body=doc)
            logger.info("report_stored_cosmos", run_id=doc_id)
    except Exception as exc:
        logger.error("cosmos_store_failed", error=str(exc), run_id=doc_id)

    # Store in Blob Storage (as JSON)
    try:
        from azure.storage.blob.aio import BlobServiceClient
        conn_str = f"DefaultEndpointsProtocol=https;AccountName={settings.storage_account_name};AccountKey={settings.storage_account_key};EndpointSuffix=core.windows.net"
        async with BlobServiceClient.from_connection_string(conn_str) as blob_client:
            container = blob_client.get_container_client(settings.storage_container_name)
            blob_name = f"reports/{doc_id}.json"
            report_json = json.dumps(report.model_dump(), default=str, indent=2)
            await container.upload_blob(name=blob_name, data=report_json.encode(), overwrite=True)
            logger.info("report_stored_blob", blob_name=blob_name)
    except Exception as exc:
        logger.error("blob_store_failed", error=str(exc), run_id=doc_id)

    return doc_id
