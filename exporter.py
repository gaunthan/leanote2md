#!/usr/bin/env python3

from pathlib import Path
import re
import sys

import lea
from utils import *

from anytree import Node, RenderTree

def _get_parent_node(nb_id, id_to_parent_id, id_to_node, id_to_title, root_node):
    """Get parent node of notebook @nb_id.
    """
    parent_id = id_to_parent_id.get(nb_id)
    if not parent_id:  # Without parent.
        return root_node

    if parent_id not in id_to_node: # Parent node not create yet.
        parent_node = Node(id_to_title[parent_id], parent=_get_parent_node(
            parent_id, id_to_parent_id, id_to_node, id_to_title, root_node
        ), id=parent_id)
        id_to_node[parent_id] = parent_node
    else:
        parent_node = id_to_node.get(parent_id)
    return parent_node

def get_notebooks_paths(notebooks):
    """Get local paths for notebooks.

    Args:
        notebooks: List of notebooks' info.
    
    Returns:
        Dict that maps a notebook's id to its path.
    """
    notebooks = [nb for nb in notebooks if not nb['IsDeleted']]

    # Get floders' tree
    id_to_title = {nb['NotebookId']: nb['Title'] for nb in notebooks}
    id_to_parent_id = {nb['NotebookId']: nb['ParentNotebookId'] for nb in notebooks}
    id_to_node = {}
    tree_root = Node('.')
    for nb_id in id_to_parent_id.keys():
        if nb_id not in id_to_node:
            node = Node(id_to_title[nb_id], parent=_get_parent_node(
                nb_id, id_to_parent_id, id_to_node, id_to_title, tree_root
            ), id=nb_id)
            id_to_node[nb_id] = node

    # Get paths of notebooks
    nb_id_to_paths = {}
    for node in tree_root.descendants:
        path = Path()
        for nd in node.path:
            path = path / nd.name.strip()
        nb_id_to_paths[node.id] = path
    return nb_id_to_paths

def save_image(url, img_path, forced_save=False):
    """Download image from @url and save it to @img_path.

    Args:
        url: Url of image.
        img_path: Path to save the image.
        forced_save: Force to save images if True.
        
    Returns:
        Filename
    """
    if '/api/file/getImage' in url:
        image_id = re.sub(r'.*fileId=(.*).*', r'\1', url) 
        filename = image_id + '.png'
        file_path = Path(img_path) / filename
        if not os.path.exists(file_path) or forced_save:
            img = lea.get_image(image_id)
            with open(file_path, 'wb') as f:
                f.write(img)
        return filename
    else:
        # FIXME: Deal with image from other places.
        return ''

def localize_image_link(content, img_path, img_link_path, forced_save=False):
    """Localize image links in @content.

    Download all images in content, change the link to local path.

    Args:
        content: Content to parse.
        img_path: Path to save the referenced images in note.
        img_link_path: Path to access image.
        forced_save: Force to save images if True.
    """
    mkdir_p(img_path)

    img_link_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')
    def _change_link(m):
        url = m.group(2)
        filename = save_image(url, img_path, forced_save)
        return '![{}]({})'.format(m.group(1), img_link_path + '/' + filename)

    return img_link_pattern.sub(_change_link, content)

def save_note_as_md(note, nb_id_to_paths, output_path='./', img_path='./images', 
                    img_link_path='./images', localize_image=True, 
                    forced_save=False, add_hexo_meta=True, only_blog=True):
    """Save note to $output_path and referenced images to $img_path.

    Args:
        note: Note to save.
        nb_id_to_paths: Dict that map notebook's id to its path.
        output_path: Path to save the Markdown note.
        img_path: Path to save the referenced images in note.
        img_link_path: Path to access image.
        localize_image: Save images to local storage and update note's iamge link if True.
        forced_save: Force to save images if True.
        add_hexo_meta: Add hexo meta header at the beginning of the note if True.
    """
    if note['IsTrash'] or not note['IsMarkdown']:
        return
    if only_blog and not note['IsBlog']:
        return

    title = note['Title']
    if note['Tags']:
        tags = ''.join(['\n- ' + t for t in note['Tags']])
    else:
        tags = ''
    created_time = note['CreatedTime']
    content = note['Content']

    hexo_meta_header = {
        'title': title,
        'date': created_time,
        'tags': tags,
    }
    
    final_path = Path(output_path) 
    folder = nb_id_to_paths.get(note['NotebookId'])
    if folder:
        final_path /= folder
    mkdir_p(final_path)

    title = title.strip()
    title = windows_filename_filter(title)
    title += '.md'
    filepath = final_path / title
    print('Saving note %s' % (filepath))

    if localize_image:
        content = localize_image_link(content, img_path, img_link_path, forced_save)

    try:
        with open(filepath, 'w', encoding='utf-8') as fd:
            fd.write('---\n')
            for h in hexo_meta_header:
                fd.write('%s: %s\n' % (h, hexo_meta_header[h]))
            fd.write('---\n')
            fd.write(content)
    except OSError as e:
        print(e)


if __name__ == '__main__':
    interactive = len(sys.argv) <= 1

    if interactive:
        email = input("Input account's email: ")
        pwd = input("Input account's password: ")

        output_path = input("Input path to save notes: ")
        only_blog = input("Only save blog notes? (True/False): ")
        only_blog = only_blog == 'True'

        localize_image = input("Need to save images of notes? (True/False): ")
        localize_image = localize_image == 'True'
        if localize_image:
            img_path = input("Input path to save images: ")
            img_link_path = input("Input path that image links references: ")
            forced_save = input("Force to save image even exitsed? (True/False): ")
            forced_save = forced_save == 'True'
        else:   # Set default values
            img_path = ''
            img_link_path = ''
            forced_save = False
    else:
        import config
        email = config.email
        pwd = config.pwd
        output_path = config.output_path
        only_blog = config.only_blog
        localize_image = config.localize_image
        img_path = config.img_path
        img_link_path = config.img_link_path
        forced_save = config.forced_save

    lea.login(email, pwd)
    notebooks = lea.get_notebooks()
    nb_id_to_paths = get_notebooks_paths(notebooks)

    for nb in notebooks:
        notes = lea.get_notes(nb['NotebookId'])
        for note in notes:
            note = lea.get_note(note['NoteId'])
            save_note_as_md(note, nb_id_to_paths, output_path=output_path,
                    img_path=img_path, img_link_path=img_link_path,
                    localize_image=True, forced_save=False, only_blog=only_blog)