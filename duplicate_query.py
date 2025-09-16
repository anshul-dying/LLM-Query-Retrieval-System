QUERY_ANSWER = 'Docs/query_answer.txt'

queries = set()
dup_queries = []
query_line_map = {}
count = 1

with open(QUERY_ANSWER, encoding='utf-8') as f:
    for line in f:
        parts = [part.strip() for part in line.split('|')]
        query = parts[1].lower()

        if query in queries:
            first_line = query_line_map[query]
            print(f"Duplicate Query found on line {count} (first seen on line {first_line}): {query}")
            dup_queries.append(query)
        else:
            queries.add(query)
            query_line_map[query] = count

        count += 1

print(f"Total Queries:      {len(queries)}")
print(f"Duplicate Queries:  {len(dup_queries)}")
