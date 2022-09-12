import sys

import click

import deepdanbooru as dd

__version__ = "1.1.2"


@click.version_option(prog_name="DeepDanbooru", version=__version__)
@click.group()
def main():
    """
    AI based multi-label girl image classification system, implemented by using TensorFlow.
    """
    pass


@main.command("create-project")
@click.argument(
    "project_path",
    type=click.Path(exists=False, resolve_path=True, file_okay=False, dir_okay=True),
)
def create_project(project_path):
    dd.commands.create_project(project_path)

@main.command("download-image")
@click.option("--start-range", "-s", type=int, help="Start range of folder ID.")
@click.option("--end-range", "-e", type=int, default=999, help="End range of folder ID.")
@click.option("--threads", "-t", type=int, default=5, help="Number of threads.")
@click.argument(
    "download_path",
    type=str
)
def download_image(download_path, start_range, end_range, threads):
    dd.commands.download_image(download_path, start_range, end_range, threads)

@main.command("download-tags")
@click.option("--limit", default=10000, help="Limit for each category tag count.")
@click.option("--minimum-post-count", default=500, help="Minimum post count for tag.")
@click.option("--overwrite", help="Overwrite tags if exists.", is_flag=True)
@click.argument(
    "path",
    type=click.Path(exists=False, resolve_path=True, file_okay=False, dir_okay=True),
)
def download_tags(path, limit, minimum_post_count, overwrite):
    dd.commands.download_tags(path, limit, minimum_post_count, overwrite)

@main.command("create-database")
@click.option("--import-size", default=10, help="Import size for importing to sqlite3.")
@click.option("--skip-unique", default=False, help="Skip unique tags.", is_flag=True)
@click.option("--use-dbmem", default=False, help="Use database memory for importing to sqlite3.", is_flag=True)
@click.option("--create-new", default=False, help="Create new database.", is_flag=True)
@click.option("--insert-all", default=False, help="Insert all posts to database.", is_flag=True)
@click.argument(
    "json_path",
    type=click.Path(exists=True, resolve_path=True, file_okay=False, dir_okay=True),
    required=True
)
@click.argument(
    "project_path",
    type=click.Path(exists=True, resolve_path=True, file_okay=False, dir_okay=True),
)
def create_database(project_path, json_path, import_size, skip_unique, use_dbmem, create_new, insert_all):
    dd.commands.create_database(project_path, json_path, import_size, skip_unique, use_dbmem, create_new, insert_all)

@main.command("make-training-database")
@click.argument(
    "source_path",
    type=click.Path(exists=True, resolve_path=True, file_okay=True, dir_okay=False),
    nargs=1,
    required=True,
)
@click.argument(
    "output_path",
    type=click.Path(exists=False, resolve_path=True, file_okay=True, dir_okay=False),
    nargs=1,
    required=True,
)
@click.option(
    "--start-id",
    default=1,
    help="Start id.",
)
@click.option("--end-id", default=sys.maxsize, help="End id.")
@click.option("--use-deleted", help="Use deleted posts.", is_flag=True)
@click.option(
    "--chunk-size", default=5000000, help="Chunk size for internal processing."
)
@click.option("--overwrite", help="Overwrite tags if exists.", is_flag=True)
@click.option(
    "--vacuum", help="Execute VACUUM command after making database.", is_flag=True
)
def make_training_database(
    source_path,
    output_path,
    start_id,
    end_id,
    use_deleted,
    chunk_size,
    overwrite,
    vacuum,
):
    dd.commands.make_training_database(
        source_path,
        output_path,
        start_id,
        end_id,
        use_deleted,
        chunk_size,
        overwrite,
        vacuum,
    )

@main.command("move-to-md5")
@click.option("--use-threads", help="Use threads.", is_flag=True)
@click.option("--threads", default=5, help="Threads count.")
@click.argument(
    "source_path",
    type=click.Path(exists=True, resolve_path=True, file_okay=False, dir_okay=True),
)
@click.argument(
    "destination_path",
    type=click.Path(exists=False, resolve_path=True, file_okay=False, dir_okay=True),
)
def move_to_md5(source_path, destination_path ,use_threads, threads):
    dd.commands.move_to_md5(source_path, destination_path, use_threads, threads)

@main.command("train-project")
@click.option("--use-dbmem", default=False, help="Use database memory for importing to sqlite3.", is_flag=True)
@click.option("--load-as-md5", default=False, help="Load as md5.", is_flag=True)
@click.option("--no-md5-folder", default=False, help="Do not use md5 2 word folder.", is_flag=True)
@click.option("--load-as-id", default=False, help="Load as id.", is_flag=True)
@click.option("--use-one-folder", default=False, help="Load as one id folder.", is_flag=True)
@click.argument(
    "project_path",
    type=click.Path(exists=True, resolve_path=True, file_okay=False, dir_okay=True),
)
@click.option(
    "--source-model",
    type=click.Path(exists=True, resolve_path=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--gpu-memory-limit",
    default=0, help="GPU memory limit for training.", type=click.INT
)
def train_project(project_path, source_model, use_dbmem, load_as_md5, no_md5_folder, gpu_memory_limit, load_as_id, use_one_folder):
    dd.commands.train_project(project_path, source_model, use_dbmem, load_as_md5, no_md5_folder, gpu_memory_limit, load_as_id, use_one_folder)


@main.command(
    "evaluate-project",
    help="Evaluate the project. If the target path is folder, it evaulates all images recursively.",
)
@click.argument(
    "project_path",
    type=click.Path(exists=True, resolve_path=True, file_okay=False, dir_okay=True),
)
@click.argument(
    "target_path",
    type=click.Path(exists=True, resolve_path=True, file_okay=True, dir_okay=True),
)
@click.option("--threshold", help="Threshold for tag estimation.", default=0.5)
def evaluate_project(project_path, target_path, threshold):
    dd.commands.evaluate_project(project_path, target_path, threshold)


@main.command(
    "grad-cam", help="Experimental feature. Calculate activation map using Grad-CAM."
)
@click.argument(
    "project_path",
    type=click.Path(exists=True, resolve_path=True, file_okay=False, dir_okay=True),
)
@click.argument(
    "target_path",
    type=click.Path(exists=True, resolve_path=True, file_okay=True, dir_okay=True),
)
@click.argument(
    "output_path",
    type=click.Path(resolve_path=True, file_okay=False, dir_okay=True),
    default=".",
)
@click.option("--threshold", help="Threshold for tag estimation.", default=0.5)
def grad_cam(project_path, target_path, output_path, threshold):
    dd.commands.grad_cam(project_path, target_path, output_path, threshold)


@main.command("evaluate", help="Evaluate model by estimating image tag.")
@click.argument(
    "target_paths",
    nargs=-1,
    type=click.Path(exists=True, resolve_path=True, file_okay=True, dir_okay=True),
)
@click.option(
    "--project-path",
    type=click.Path(exists=True, resolve_path=True, file_okay=False, dir_okay=True),
    help="Project path. If you want to use specific model and tags, use --model-path and --tags-path options.",
)
@click.option(
    "--model-path",
    type=click.Path(exists=True, resolve_path=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--tags-path",
    type=click.Path(exists=True, resolve_path=True, file_okay=True, dir_okay=False),
)
@click.option("--threshold", default=0.5)
@click.option("--allow-gpu", default=False, is_flag=True)
@click.option("--compile/--no-compile", "compile_model", default=False)
@click.option(
    "--allow-folder",
    default=False,
    is_flag=True,
    help="If this option is enabled, TARGET_PATHS can be folder path and all images (using --folder-filters) in that folder is estimated recursively. If there are file and folder which has same name, the file is skipped and only folder is used.",
)
@click.option(
    "--folder-filters",
    default="*.[Pp][Nn][Gg],*.[Jj][Pp][Gg],*.[Jj][Pp][Ee][Gg],*.[Gg][Ii][Ff]",
    help="Glob pattern for searching image files in folder. You can specify multiple patterns by separating comma. This is used when --allow-folder is enabled. Default:*.[Pp][Nn][Gg],*.[Jj][Pp][Gg],*.[Jj][Pp][Ee][Gg],*.[Gg][Ii][Ff]",
)
@click.option("--verbose", default=False, is_flag=True)
def evaluate(
    target_paths,
    project_path,
    model_path,
    tags_path,
    threshold,
    allow_gpu,
    compile_model,
    allow_folder,
    folder_filters,
    verbose,
):
    dd.commands.evaluate(
        target_paths,
        project_path,
        model_path,
        tags_path,
        threshold,
        allow_gpu,
        compile_model,
        allow_folder,
        folder_filters,
        verbose,
    )


if __name__ == "__main__":
    main()
