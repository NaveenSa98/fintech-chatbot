"""
Utility script to view and inspect ChromaDB vector store data.
Usage: python src/core/view_chroma_db.py (from project root)
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load .env file from project root
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

import chromadb
from chromadb.config import Settings as ChromaSettings
from src.core.config import settings, DEPARTMENT_COLLECTIONS
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
import json

console = Console()

class ChromaDBViewer:
    """View and inspect ChromaDB collections."""

    def __init__(self):
        """Initialize ChromaDB client."""
        # Use absolute path to project root's data folder
        self.persist_directory = str(project_root / settings.CHROMA_DB_DIR)
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        console.print(f"[green]Connected to ChromaDB at: {self.persist_directory}[/green]\n")

    def list_all_collections(self):
        """List all collections in ChromaDB."""
        collections = self.client.list_collections()

        if not collections:
            console.print("[yellow]No collections found in the database.[/yellow]")
            return

        table = Table(title="ChromaDB Collections", show_header=True, header_style="bold magenta")
        table.add_column("Collection Name", style="cyan")
        table.add_column("Document Count", justify="right", style="green")
        table.add_column("Department", style="yellow")

        # Reverse mapping for departments
        collection_to_dept = {v: k for k, v in DEPARTMENT_COLLECTIONS.items()}

        for collection in collections:
            count = collection.count()
            dept = collection_to_dept.get(collection.name, "Unknown")
            table.add_row(collection.name, str(count), dept)

        console.print(table)

    def view_collection_details(self, collection_name: str, limit: int = 5):
        """View detailed information about a specific collection."""
        try:
            collection = self.client.get_collection(collection_name)
            count = collection.count()

            console.print(Panel(
                f"[bold cyan]Collection:[/bold cyan] {collection_name}\n"
                f"[bold cyan]Total Documents:[/bold cyan] {count}",
                title="Collection Details",
                border_style="blue"
            ))

            if count == 0:
                console.print("[yellow]This collection is empty.[/yellow]")
                return

            # Get sample documents
            results = collection.get(limit=limit, include=["documents", "metadatas", "embeddings"])

            # Display documents
            for i, (doc_id, document, metadata) in enumerate(zip(
                results['ids'],
                results['documents'],
                results['metadatas']
            ), 1):
                console.print(f"\n[bold]Document {i}:[/bold]")
                console.print(f"[cyan]ID:[/cyan] {doc_id}")
                console.print(f"[cyan]Content:[/cyan] {document[:200]}..." if len(document) > 200 else f"[cyan]Content:[/cyan] {document}")
                console.print(f"[cyan]Metadata:[/cyan] {json.dumps(metadata, indent=2)}")
                console.print("-" * 80)

        except ValueError as e:
            console.print(f"[red]Error: Collection '{collection_name}' does not exist.[/red]")
            console.print("[yellow]Tip: Use option 1 or 2 to see available collections.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error viewing collection: {str(e)}[/red]")

    def search_in_collection(self, collection_name: str, query: str, n_results: int = 3):
        """Search for similar documents in a collection."""
        try:
            collection = self.client.get_collection(collection_name)

            # Need to get embeddings for the query
            from src.vectorstore.embeddings import get_embedding_function
            embedding_function = get_embedding_function()
            query_embedding = embedding_function.embed_query(query)

            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )

            console.print(Panel(
                f"[bold cyan]Query:[/bold cyan] {query}\n"
                f"[bold cyan]Collection:[/bold cyan] {collection_name}\n"
                f"[bold cyan]Results:[/bold cyan] {len(results['ids'][0])}",
                title="Search Results",
                border_style="green"
            ))

            # Display results
            for i, (doc_id, document, metadata, distance) in enumerate(zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ), 1):
                console.print(f"\n[bold]Result {i}:[/bold] (Distance: {distance:.4f})")
                console.print(f"[cyan]ID:[/cyan] {doc_id}")
                console.print(f"[cyan]Content:[/cyan] {document[:300]}..." if len(document) > 300 else f"[cyan]Content:[/cyan] {document}")
                console.print(f"[cyan]Metadata:[/cyan] {json.dumps(metadata, indent=2)}")
                console.print("-" * 80)

        except ValueError as e:
            console.print(f"[red]Error: Collection '{collection_name}' does not exist.[/red]")
            console.print("[yellow]Tip: Use option 1 or 2 to see available collections.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error searching collection: {str(e)}[/red]")

    def get_collection_stats(self):
        """Get statistics for all department collections."""
        table = Table(title="Department Collection Statistics", show_header=True, header_style="bold magenta")
        table.add_column("Department", style="cyan")
        table.add_column("Collection Name", style="yellow")
        table.add_column("Document Count", justify="right", style="green")
        table.add_column("Status", style="blue")

        for dept, coll_name in DEPARTMENT_COLLECTIONS.items():
            try:
                collection = self.client.get_collection(coll_name)
                count = collection.count()
                status = "Active" if count > 0 else "Empty"
                table.add_row(dept, coll_name, str(count), status)
            except Exception:
                table.add_row(dept, coll_name, "0", "Not Created")

        console.print(table)


def main():
    """Main menu for ChromaDB viewer."""
    viewer = ChromaDBViewer()

    while True:
        console.print("\n[bold cyan]ChromaDB Viewer - Main Menu[/bold cyan]")
        console.print("1. List all collections")
        console.print("2. View department statistics")
        console.print("3. View collection details")
        console.print("4. Search in collection")
        console.print("5. Exit")

        choice = console.input("\n[yellow]Enter your choice (1-5):[/yellow] ")

        if choice == "1":
            viewer.list_all_collections()

        elif choice == "2":
            viewer.get_collection_stats()

        elif choice == "3":
            collection_name = console.input("[yellow]Enter collection name:[/yellow] ").strip()
            limit = console.input("[yellow]Number of documents to view (default 5):[/yellow] ").strip() or "5"
            viewer.view_collection_details(collection_name, int(limit))

        elif choice == "4":
            collection_name = console.input("[yellow]Enter collection name:[/yellow] ").strip()
            query = console.input("[yellow]Enter search query:[/yellow] ").strip()
            n_results = console.input("[yellow]Number of results (default 3):[/yellow] ").strip() or "3"
            viewer.search_in_collection(collection_name, query, int(n_results))

        elif choice == "5":
            console.print("[green]Goodbye![/green]")
            break

        else:
            console.print("[red]Invalid choice. Please try again.[/red]")


if __name__ == "__main__":
    main()
