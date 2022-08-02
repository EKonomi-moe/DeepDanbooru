import os
from pathlib import Path
import sqlite3
from gc import collect


def load_tags(tags_path):
    with open(tags_path, "r") as tags_stream:
        tags = [tag for tag in (tag.strip() for tag in tags_stream) if tag]
        return tags


def load_image_records(sqlite_path, minimum_tag_count, use_dbmem, load_as_md5, no_md5_folder, load_as_id, use_one_folder):
    if not os.path.exists(sqlite_path):
        raise Exception(f"SQLite database is not exists : {sqlite_path}")
    if use_dbmem:
        connection = sqlite3.connect(":memory:")

        connection_disk = sqlite3.connect(sqlite_path)
        print("DATABASE DISK --> MEMORY")
        connection_disk.backup(connection)
        print("DATABASE DISK --> MEMORY OK")
        connection_disk.close()
    else:
        connection = sqlite3.connect(sqlite_path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    image_folder_path = os.path.join(os.path.dirname(sqlite_path), "images")
    
    typ = ""
    paths = []

    if load_as_md5:
        typ = "md5"
        rows = []
        for filename in os.listdir(image_folder_path):
            if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
                cursor.execute(
                    "SELECT md5, file_ext, tag_string FROM posts WHERE (file_ext = 'png' OR file_ext = 'jpg' OR file_ext = 'jpeg') AND (md5 = '{md5}') AND (tag_count_general >= {count})".format(md5=filename.split(".")[0], count=minimum_tag_count)
                )
                rows.append(cursor.fetchone())
        #        data.append((filename.split(".")[0], minimum_tag_count))
        #cursor.executemany(
        #    "SELECT md5, file_ext, tag_string FROM posts WHERE (file_ext = 'png' OR file_ext = 'jpg' OR file_ext = 'jpeg') AND (md5 = ?) AND (tag_count_general >= ?)",
        #    data
        #)
    elif load_as_id:
        typ = "id"
        rows = []
        
        for filename in Path(image_folder_path).glob("**/*"):
            if filename.is_file():
                #check endwith
                if filename.suffix == ".jpg" or filename.suffix == ".png" or filename.suffix == ".jpeg":
                    paths.append(filename.stem)
                    cursor.execute(
                        "SELECT id, file_ext, tag_string FROM posts WHERE (file_ext = 'png' OR file_ext = 'jpg' OR file_ext = 'jpeg') AND (id = ?) AND (tag_count_general >= ?)",
                        (filename.stem, minimum_tag_count)
                    )
                    rows.append(cursor.fetchone())
        pass
    else:
        typ = "md5"
        cursor.execute(
            "SELECT md5, file_ext, tag_string FROM posts WHERE (file_ext = 'png' OR file_ext = 'jpg' OR file_ext = 'jpeg') AND (tag_count_general >= ?) ORDER BY id",
            (minimum_tag_count,),
        )

        rows = cursor.fetchall()

    image_records = []

    print("Loaded all database records.")
    count = 0
    for row in rows:
        try:
            check = row[typ]
            extension = row["file_ext"]
            if no_md5_folder:
                image_path = os.path.join(image_folder_path, f"{check}.{extension}")
            elif load_as_id:
                if use_one_folder:
                    image_path = os.path.join(image_folder_path, f"{check}.{extension}")
                else:
                    image_path = os.path.join(image_folder_path, f"{str(check)[-3:].zfill(4)}", f"{check}.{extension}")
            else:
                image_path = os.path.join(image_folder_path, check[0:2], f"{check}.{extension}")
            tag_string = row["tag_string"]

            image_records.append((image_path, tag_string))
        except:
            if paths == []:
                print("Error in row:", row)
            else:
                print("Error in row:", row, "with path:", paths[count])
        
        count += 1

    connection.close()
    print(f"Loaded {len(image_records)}/{len(rows)} images.")
    del(connection)
    del(rows)
    collect()

    return image_records
