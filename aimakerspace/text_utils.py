import os
import re
from typing import List, Dict, Any, Optional


class TextFileLoader:
    def __init__(self, path: str, encoding: str = "utf-8"):
        self.documents = []
        self.path = path
        self.encoding = encoding

    def load(self):
        if os.path.isdir(self.path):
            self.load_directory()
        elif os.path.isfile(self.path) and self.path.endswith(".txt"):
            self.load_file()
        else:
            raise ValueError(
                "Provided path is neither a valid directory nor a .txt file."
            )

    def load_file(self):
        with open(self.path, "r", encoding=self.encoding) as f:
            self.documents.append(f.read())

    def load_directory(self):
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.endswith(".txt"):
                    with open(
                        os.path.join(root, file), "r", encoding=self.encoding
                    ) as f:
                        self.documents.append(f.read())

    def load_documents(self):
        self.load()
        return self.documents


class PDFFileLoader:
    """Loader for PDF files using PyPDF2."""
    
    def __init__(self, path: str):
        self.documents = []
        self.path = path

    def load(self):
        if os.path.isdir(self.path):
            self.load_directory()
        elif os.path.isfile(self.path) and self.path.endswith(".pdf"):
            self.load_file()
        else:
            raise ValueError(
                "Provided path is neither a valid directory nor a .pdf file."
            )

    def load_file(self):
        try:
            import PyPDF2
        except ImportError:
            raise ImportError("PyPDF2 is required to load PDF files. Install with: pip install PyPDF2")
        
        with open(self.path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            self.documents.append(text)

    def load_directory(self):
        try:
            import PyPDF2
        except ImportError:
            raise ImportError("PyPDF2 is required to load PDF files. Install with: pip install PyPDF2")
        
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.endswith(".pdf"):
                    filepath = os.path.join(root, file)
                    with open(filepath, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() + "\n"
                        self.documents.append(text)

    def load_documents(self):
        self.load()
        return self.documents


class DirectoryLoader:
    """Load all supported files from a directory (txt and pdf)."""
    
    def __init__(self, path: str, encoding: str = "utf-8"):
        self.documents = []
        self.metadata = []  # Track source file info
        self.path = path
        self.encoding = encoding

    def load(self):
        if not os.path.isdir(self.path):
            raise ValueError(f"Provided path is not a valid directory: {self.path}")
        
        for root, _, files in os.walk(self.path):
            for file in files:
                filepath = os.path.join(root, file)
                if file.endswith(".txt"):
                    with open(filepath, "r", encoding=self.encoding) as f:
                        content = f.read()
                        self.documents.append(content)
                        self.metadata.append({"source": filepath, "type": "txt"})
                elif file.endswith(".pdf"):
                    try:
                        import PyPDF2
                        with open(filepath, "rb") as f:
                            reader = PyPDF2.PdfReader(f)
                            text = ""
                            for page in reader.pages:
                                text += page.extract_text() + "\n"
                            self.documents.append(text)
                            self.metadata.append({"source": filepath, "type": "pdf"})
                    except ImportError:
                        print(f"Warning: PyPDF2 not installed, skipping {file}")

    def load_documents(self):
        self.load()
        return self.documents
    
    def load_documents_with_metadata(self):
        self.load()
        return list(zip(self.documents, self.metadata))


class CharacterTextSplitter:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        assert (
            chunk_size > chunk_overlap
        ), "Chunk size must be greater than chunk overlap"

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> List[str]:
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunks.append(text[i : i + self.chunk_size])
        return chunks

    def split_texts(self, texts: List[str]) -> List[str]:
        chunks = []
        for text in texts:
            chunks.extend(self.split(text))
        return chunks


if __name__ == "__main__":
    loader = TextFileLoader("data/KingLear.txt")
    loader.load()
    splitter = CharacterTextSplitter()
    chunks = splitter.split_texts(loader.documents)
    print(len(chunks))
    print(chunks[0])
    print("--------")
    print(chunks[1])
    print("--------")
    print(chunks[-2])
    print("--------")
    print(chunks[-1])
