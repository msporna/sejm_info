import codecs
import datetime
import os
import shutil


def delete_files_in_directory(dir_path):
    try:
        files = os.listdir(dir_path)
        for file in files:
            file_path = os.path.join(dir_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print(f"All files from {dir_path} deleted successfully.")
    except:
        print(f"Couldn't delete from {dir_path}. Probably already clean...")


def get_project_hashtags(project_id):
    path = f"generated_hashtags/{project_id}.txt"
    if os.path.isfile(path):
        with codecs.open(path, 'r', "utf-8") as f:
            hashtag_lines = f.readlines()
            for hsl in hashtag_lines:
                hsl = hsl.strip()
            hashtags = ' '.join(hashtag_lines)
            hashtags = hashtags.replace('\n', " ").strip()
            return hashtags


def get_project_metadata(project_id):
    dir = "metadata"
    for filename in os.listdir(dir):
        f = os.path.join(dir, filename)
        if os.path.isfile(f):
            print(f"processing metadata file: {f}")
            with codecs.open(f, 'r', "utf-8") as f:
                metadata_lines = f.readlines()
                for metadata in metadata_lines:
                    pid, title, process_id = metadata.split(";")
                    print(f"checking {pid} from metadata if matches [{project_id}]")
                    if pid == project_id:
                        return title, process_id


def copy(src, dst):
    shutil.copy(src, dst)
    print(f"copied {src} to {dst}")


def copytree(src, dst):
    shutil.copytree(src, dst)
    print(f"copied {src} to {dst}")


def delete_directories(dir_tree):
    try:
        shutil.rmtree(dir_tree)
    except:
        print(f"cannot remove tree {dir_tree} (directory probably alread does not exist)")


def delete_backup_temp():
    delete_files_in_directory("backup_temp")
    delete_directories("backup_temp/download/pending")
    delete_directories("backup_temp/download/processed")
    delete_directories("backup_temp/download/processed_txt_files_archive")
    delete_directories("backup_temp/download/raw_pdf")
    delete_directories("backup_temp/download/raw_pdf_already_done")
    delete_directories("backup_temp/download/twitter_lines")
    delete_directories("backup_temp/download")
    delete_directories("backup_temp/generated_hashtags")
    delete_directories("backup_temp/metadata")


def create_backup():
    print("starting backup preparation...")
    delete_backup_temp()

    # copy files to backup
    copy("sejminfo.db", "backup_temp/sejminfo.db")
    copytree("download/pending", "backup_temp/download/pending")
    copytree("download/processed", "backup_temp/download/processed")
    copytree("download/processed_txt_files_archive", "backup_temp/download/processed_txt_files_archive")
    copytree("download/raw_pdf", "backup_temp/download/raw_pdf")
    copytree("download/raw_pdf_already_done", "backup_temp/download/raw_pdf_already_done")
    copytree("download/twitter_lines", "backup_temp/download/twitter_lines")
    copytree("generated_hashtags", "backup_temp/generated_hashtags")
    copytree("metadata", "backup_temp/metadata")

    # zip
    print("preparing zip package for the backup files...")
    backup_archive_path = f'backup/backup_{datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")}'
    shutil.make_archive(backup_archive_path, 'zip',
                        'backup_temp')
    print(f"backup archive created at {backup_archive_path}")
    # clear original folders
    print("clearing previous process files...")
    delete_files_in_directory("download/pending")
    delete_files_in_directory("download/processed")
    delete_files_in_directory("download/processed_txt_files_archive")
    delete_files_in_directory("download/raw_pdf")
    delete_files_in_directory("download/raw_pdf_already_done")
    delete_files_in_directory("download/twitter_lines")
    delete_files_in_directory("generated_hashtags")
    delete_files_in_directory("metadata")
    delete_files_in_directory("img_ocr_temp")

    delete_backup_temp()

    print("backup finished")


def copy_sqlite_db_to_web():
    shutil.copy2("sejminfo.db", "../web/sejminfo.db")
