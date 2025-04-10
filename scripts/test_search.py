from flask_app.Score import SearchEngine

if __name__ == '__main__':
    db_path = 'db/spider_test.db'
    search_engine = SearchEngine(db_path, pre_caching_size=0)

    # Handle KeyboardInterrupt
    try:
        # Loop to search
        while True:
            query = input(f"Type to search: ")
            results, _ = search_engine.search(query, match_in_title=False, raw_match_phrase=True, phrase_search_distance=1)
            print("\nResults:")
            if len(results) == 0:
                print("No results found.")
            for result in results[0:5]:
                for key, value in result.items():
                    if key not in ['parent_links','child_links']:
                        print(f"{key}: {value}")
                    else:
                        print(f"num_{key}: {len(value)}")
                print(f"{'-'*20}")
    except KeyboardInterrupt:
        print("\nExiting...")
        exit(0)

