from Database import Database

if __name__ == '__main__':
    db_path = 'db/spider_test.db'
    print(f'Reading {db_path}.')
    database = Database(db_path)
    limit = 10
    with open('phase1-output/output/spider_result.txt', 'w', encoding='UTF-8') as f:
        database.cursor.execute("SELECT * FROM urlList WHERE title is not null")
        for row in database.cursor.fetchall():
            page_id = row[0]
            url = row[1]
            title = row[2]
            last_modified = row[3]
            content_length = row[4]
            f.write(f"{title}\n{url}\n{last_modified} {content_length}\n")
            count, forward_index_head = database.get_forward_index_head_cached(page_id)
            for i, (word, freq) in enumerate(forward_index_head.items()):
                if i >= limit:
                    break
                end = ' ' if i < limit-1 else '\n'
                f.write(f"{word}: {freq};{end}")
            for i, child_url in enumerate(database.get_child_cached(page_id)):
                if i >= limit:
                    break
                f.write(f"{child_url}\n")
            f.write(f"-----------------\n")
        f.close()
