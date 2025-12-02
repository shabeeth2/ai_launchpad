from data import loader, preprocessor, chunker

raw_docs = loader.load("paper.pdf")   #  .md, .txt, .json, url
for doc in raw_docs:
    doc["text"] = preprocessor.clean(doc["text"])
    chunks = chunker.recursive_split(doc["text"])
    for c in chunks:
        llm_index.add(c, metadata=doc["meta"])