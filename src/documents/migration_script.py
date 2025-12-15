"""
Migration script to convert existing PDF and DOCX documents to Markdown format.

Usage:
    python -m src.documents.migration_script

This script:
    1. Queries all documents with file_type = 'pdf' or 'docx'
    2. Converts them to markdown format
    3. Updates database records with conversion metadata
    4. Logs progress and errors
"""

import os
from pathlib import Path
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal, engine
from src.documents.models import Document
from src.documents.converters import get_document_converter
from src.core.config import settings
from src.core.logging_config import get_logger
from datetime import datetime

logger = get_logger("migration")


def migrate_documents_to_markdown():
    """
    Migrate all existing PDF and DOCX documents to Markdown format.

    Process:
        1. Find all documents with file_type in ['pdf', 'docx']
        2. For each document:
            - Load original file from disk
            - Convert to markdown
            - Save markdown file
            - Update database record
        3. Log progress and results
    """
    db = SessionLocal()
    converter = get_document_converter()

    try:
        # Query all documents that need conversion
        documents_to_convert = db.query(Document).filter(
            Document.file_type.in_(["pdf", "docx"])
        ).all()

        total_count = len(documents_to_convert)
        logger.info(f"Found {total_count} documents to convert to Markdown")

        if total_count == 0:
            logger.info("No documents to migrate. Exiting.")
            return

        success_count = 0
        failed_count = 0
        skipped_count = 0

        for idx, doc in enumerate(documents_to_convert, 1):
            logger.info(f"\n[{idx}/{total_count}] Processing: {doc.original_filename}")

            # Construct original file path
            original_file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)

            # Check if original file exists
            if not os.path.exists(original_file_path):
                logger.warning(f"Original file not found on disk: {original_file_path}")
                skipped_count += 1
                continue

            # Generate markdown filename
            md_filename = f"{doc.filename.rsplit('.', 1)[0]}.md"
            md_path = os.path.join(settings.UPLOAD_DIR, md_filename)

            # Skip if markdown already exists
            if os.path.exists(md_path):
                logger.info(f"Markdown file already exists, skipping: {md_filename}")
                # Update database record if needed
                if doc.file_type != "md" or doc.converted_from is None:
                    doc.file_type = "md"
                    doc.converted_from = doc.file_type
                    doc.source_file_type = "pdf" if doc.filename.endswith(".pdf") else "docx"
                    db.commit()
                    logger.info(f"Updated database record for {doc.original_filename}")
                skipped_count += 1
                continue

            # Convert file to markdown
            original_type = doc.file_type.lower()
            success, error, file_to_use = converter.convert_with_fallback(
                file_path=original_file_path,
                file_type=original_type,
                output_path=md_path
            )

            if success:
                # Update database record
                try:
                    doc.file_type = "md"
                    doc.source_file_type = original_type
                    doc.converted_from = original_type
                    db.commit()
                    logger.info(f"✓ Successfully converted and updated: {doc.original_filename}")
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to update database for {doc.original_filename}: {str(e)}")
                    db.rollback()
                    failed_count += 1
            else:
                logger.warning(f"✗ Conversion failed for {doc.original_filename}: {error}")
                failed_count += 1

        # Print summary
        logger.info("\n" + "="*70)
        logger.info("MIGRATION SUMMARY")
        logger.info("="*70)
        logger.info(f"Total documents processed: {total_count}")
        logger.info(f"Successfully converted: {success_count}")
        logger.info(f"Failed conversions: {failed_count}")
        logger.info(f"Skipped (already converted): {skipped_count}")
        logger.info("="*70)

        if failed_count == 0:
            logger.info("✓ Migration completed successfully!")
        else:
            logger.warning(f"⚠ Migration completed with {failed_count} failures. Review logs above.")

    except Exception as e:
        logger.error(f"Critical error during migration: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def rollback_migration():
    """
    Rollback migration: revert markdown conversions back to original formats.

    Note: This only updates the database records. Physical files are not deleted.
    """
    db = SessionLocal()

    try:
        # Find all documents that were converted
        converted_documents = db.query(Document).filter(
            Document.converted_from.isnot(None)
        ).all()

        total_count = len(converted_documents)
        logger.info(f"Found {total_count} converted documents to rollback")

        if total_count == 0:
            logger.info("No converted documents to rollback. Exiting.")
            return

        for doc in converted_documents:
            doc.file_type = doc.converted_from
            doc.converted_from = None
            db.commit()
            logger.info(f"Rolled back: {doc.original_filename}")

        logger.info(f"✓ Rollback completed for {total_count} documents")
        logger.info("Note: Markdown files on disk were NOT deleted. Delete them manually if needed.")

    except Exception as e:
        logger.error(f"Error during rollback: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    logger.info("="*70)
    logger.info("Document Migration Script - PDF/DOCX to Markdown Conversion")
    logger.info("="*70)

    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        logger.info("Running in ROLLBACK mode...")
        rollback_migration()
    else:
        logger.info("Running migration to convert PDF/DOCX to Markdown...")
        migrate_documents_to_markdown()
