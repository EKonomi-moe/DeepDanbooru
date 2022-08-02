import os
import sqlite3
from json import loads
from gc import collect

import deepdanbooru as dd

def create_database(
    project_path, json_path, import_size=10, skip_unique = False, use_dbmem = False, create_new = False, insert_all = False
):
    """
    Create new database with posts from json file.
    """
    project_context_path = os.path.join(project_path)

    #get json_path dir list
    json_path_dir_list = dd.io.get_directory_list(json_path, "posts*")
    if json_path_dir_list == []:
        print("ERROR: No json file found.")
        return

    # Open Database
    if use_dbmem:
        print("Creating new database in memory...")
        conn = sqlite3.connect(":memory:")
        if not create_new:
            if os.path.exists(os.path.join(project_context_path, "metadata.db")):                    
                connsource = sqlite3.connect(os.path.join(project_path, "metadata.db"))

                print("DATABASE DISK --> MEMORY")
                connsource.backup(conn)
                print("DATABASE DISK --> MEMORY OK")
                connsource.close()
            else:
                print("WARNING: No database found. Creating new database.")
    else:
        conn = sqlite3.connect(os.path.join(project_path, "metadata.db"))
        

    cursor = conn.cursor()
    try:
        if insert_all:
            insert_sql = """INSERT INTO posts (id, md5, tag_string, tag_count, tag_string_general, tag_count_general, tag_string_artist, tag_count_artist, tag_string_character, tag_count_character, tag_string_copyright, tag_count_copyright, tag_string_meta, tag_count_meta, rating, score, is_deleted, is_banned, fav_count, file_ext, uploader_id, created_at, updated_at, image_width, image_height, has_children, has_active_children, has_visible_children, file_url, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            cursor.execute("""
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    md5 TEXT,
    tag_string TEXT,
    tag_count INTEGER,
    tag_string_general TEXT,
    tag_count_general INTEGER,
    tag_string_artist TEXT,
    tag_count_artist INTEGER,
    tag_string_character TEXT,
    tag_count_character INTEGER,
    tag_string_copyright TEXT,
    tag_count_copyright INTEGER,
    tag_string_meta TEXT,
    tag_count_meta INTEGER,
    rating TEXT,
    score INTEGER,
    is_deleted INTEGER,
    is_banned INTEGER,
    fav_count INTEGER,
    file_ext TEXT,
    uploader_id INTEGER,
    created_at TEXT,
    updated_at TEXT,
    image_width INTEGER,
    image_height INTEGER,
    has_children INTEGER,
    has_active_children INTEGER,
    has_visible_children INTEGER,
    file_url TEXT,
    source TEXT
)
            """)
        else:
            insert_sql = """INSERT INTO posts (id, md5, file_ext, tag_string, tag_count_general, rating, score, is_deleted, is_banned) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            cursor.execute("""
CREATE TABLE posts(
    id INTEGER PRIMARY KEY,
    md5 TEXT,
    file_ext TEXT,
    tag_string TEXT,
    tag_count_general INTEGER,
    rating TEXT,
    score INTEGER,
    is_deleted INTEGER,
    is_banned INTEGER
)
            """)
    except sqlite3.OperationalError:
        pass
    
    cursor.execute("""
CREATE UNIQUE INDEX posts_idx ON posts (id)
    """)
    for path in json_path_dir_list:
        nowfile = path.split("\\")[-1]
        f = open(path, "rb")
        
        count = 0
        insert = []
        
        for data in f:
            data = loads(data)

            try:
                if insert_all:
                    insert.append((int(data["id"]), data["md5"], data["tag_string"], int(data["tag_count"]), data["tag_string_general"], int(data["tag_count_general"]), data["tag_string_artist"], int(data["tag_count_artist"]), data["tag_string_character"], int(data["tag_count_character"]), data["tag_string_copyright"], int(data["tag_count_copyright"]), data["tag_string_meta"], int(data["tag_count_meta"]), data["rating"], int(data["score"]), int(data["is_deleted"]), int(data["is_banned"]), int(data["fav_count"]), data["file_ext"], int(data["uploader_id"]), data["created_at"], data["updated_at"], int(data["image_width"]), int(data["image_height"]), int(data["has_children"]), int(data["has_active_children"]), int(data["has_visible_children"]), data["file_url"], data["source"]))
                else:
                    insert.append((int(data["id"]), data["md5"], data["file_ext"], data["tag_string"], int(data["tag_count_general"]), data["rating"], int(data["score"]), int(data["is_deleted"]), int(data["is_banned"])))
            except KeyError:
                pass
            if len(insert) == import_size:
                try:
                    cursor.executemany(insert_sql, insert)
                    conn.commit()
                    print(f"{nowfile} :: {len(insert)} rows imported. {(len(insert) + import_size*count)}")
                    count += 1
                except sqlite3.IntegrityError as e:
                    if skip_unique:
                        print(f"{nowfile} :: SKIPPING: {e}, {(import_size*count)}")
                    else:
                        print(f"{nowfile} :: ERROR: {e}, {(import_size*count)}")
                        exit()
                insert = []
        
        f.close()

        if len(insert) > 0:
            try:
                cursor.executemany(insert_sql, insert)
                conn.commit()
                print(f"{nowfile} :: {len(insert)} rows imported. {(len(insert) + import_size*count)}")
            except sqlite3.IntegrityError as e:
                if skip_unique:
                    print(f"{nowfile} :: SKIPPING: {e}, {(import_size*count)}")
                else:
                    print(f"{nowfile} :: ERROR: {e}, {(import_size*count)}")
                    exit()

        try:
            del(insert)
            del(count)
            del(f)
        except:
            pass

        collect()
    

    if use_dbmem:
        connsource = sqlite3.connect(os.path.join(project_path, "metadata.db"))
        
        print("Database MEMORY --> DISK")
        conn.backup(connsource)
        print("Database MEMORY --> DISK OK")
        
        connsource.close()

    conn.close()


    