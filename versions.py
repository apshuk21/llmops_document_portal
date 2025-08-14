import importlib.metadata

packages = [
    "langchain",
    "python-dotenv",
    "ipykernel",
    "langchain-openai",
    "langchain-community",
    "faiss-cpu",
    "structlog",
    "PyMuPDF",
    "pylint",
    "langchain-core",
    "pytest",
    "streamlit",
    "fastapi",
    "uvicorn",
    "python-multipart",
    "docx2txt",
]
for pkg in packages:
    try:
        version = importlib.metadata.version(pkg)
        print(f"{pkg}=={version}")
    except importlib.metadata.PackageNotFoundError:
        print(f"{pkg} (not installed)")

if __name__ == "__main__":
    for pkg in packages:
        try:
            version = importlib.metadata.version(pkg)
            print(f"{pkg}=={version}")
        except importlib.metadata.PackageNotFoundError:
            print(f"{pkg} (not installed)")
