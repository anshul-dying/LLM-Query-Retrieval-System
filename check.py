# Adjust these paths as needed
QUERY_ANSWER_FILE = "Docs/query_answer.txt"
LOG_FILE = "queries.log"
OUTPUT_FILE = "missing_queries.txt"

def extract_queries_from_answers(file_path):
    queries = set()
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            parts = [part.strip() for part in line.split('|')]
            # print(parts)

            queries.add(parts[1].lower())
    return queries

def extract_queries_from_log(file_path):
    queries = set()
    doc_query_pairs = []  # (doc_name, query)
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            parts = [part.strip() for part in line.split('|')]
            query = parts[3].lower()
            queries.add(query)
            doc_name = parts[1]
            doc_query_pairs.append((doc_name, query))
            # print(query)
    return queries, doc_query_pairs

def main():
    answer_queries = extract_queries_from_answers(QUERY_ANSWER_FILE)
    log_queries, doc_query_pairs = extract_queries_from_log(LOG_FILE)

    missing = log_queries - answer_queries

    print(f"Total queries in log: {len(log_queries)}")
    print(f"Total queries in answer file: {len(answer_queries)}")
    print(f"Missing queries: {len(missing)}")
    if missing:
        print(f"\nWriting missing queries to {OUTPUT_FILE}...")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
            out.write("doc_name|missing_query\n")
            for doc_name, query in doc_query_pairs:
                if query in missing:
                    out.write(f"{doc_name}|{query}\n")
        print(f"Done. Check {OUTPUT_FILE} for details.")
    else:
        print("No missing queries!")

if __name__ == "__main__":
    main()