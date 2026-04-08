import logging
import os
import re

import markdown

from pagesController import ConfluenceClient

DISPLAY_CHILDREN_MACRO = '<ac:structured-macro ac:name="children" ac:schema-version="2"/>'


def _extract_images(line: str) -> tuple[str, list[str]]:
    """
    Replace local image markdown references with Confluence storage format.
    Returns (modified_line, list_of_filenames_to_attach).
    HTTP/HTTPS image links are left unchanged.
    """
    filenames: list[str] = []

    def _replace(m: re.Match) -> str:
        filename = os.path.basename(m.group(1))
        filenames.append(filename)
        logging.debug("Found file for attaching: %s", filename)
        return f'<ac:image><ri:attachment ri:filename="{filename}"/></ac:image>'

    modified = re.sub(r'!\[.*?]\((?!https?://)(.*?)\)', _replace, line)
    return modified, filenames


def _publish_markdown_file(
    entry: os.DirEntry,
    client: ConfluenceClient,
    images_root: str,
    parent_page_id,
) -> None:
    content_lines: list[str] = []
    files_to_upload: list[str] = []

    with open(entry.path, 'r', encoding="utf-8") as md_file:
        for line in md_file:
            modified_line, images = _extract_images(line)
            files_to_upload.extend(images)
            content_lines.append(modified_line)

    html_content = markdown.markdown(
        "".join(content_lines),
        extensions=['markdown.extensions.tables', 'fenced_code'],
    )
    page_id = client.create_page(
        title=entry.name,
        content=html_content,
        parent_page_id=parent_page_id,
    )

    for filename in files_to_upload:
        image_path = os.path.join(images_root, filename)
        if os.path.isfile(image_path):
            logging.info("Attaching file %s to page %s", image_path, page_id)
            with open(image_path, 'rb') as f:
                client.attach_file(page_id, f)
        else:
            logging.error("File %s not found, nothing to attach", image_path)


def publish_folder(
    folder: str,
    client: ConfluenceClient,
    images_root: str,
    parent_page_id=None,
) -> None:
    logging.info("Publishing folder: %s", folder)
    for entry in os.scandir(folder):
        if entry.is_dir():
            logging.info("Found directory: %s", entry.path)
            current_page_id = client.create_page(
                title=entry.name,
                content=DISPLAY_CHILDREN_MACRO,
                parent_page_id=parent_page_id,
            )
            publish_folder(entry.path, client, images_root, parent_page_id=current_page_id)

        elif entry.is_file():
            logging.info("Found file: %s", entry.path)
            if entry.path.lower().endswith('.md'):
                _publish_markdown_file(entry, client, images_root, parent_page_id)
            else:
                logging.info("File %s is not a MD file, skipping", entry.path)

        elif entry.is_symlink():
            logging.info("Found symlink: %s", entry.path)

        else:
            logging.info("Found unknown entry type (not file, dir, or symlink): %s", entry.path)
