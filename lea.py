#!/usr/bin/env python3
# Wrapper for Leanote API v1

import requests as req

LEANOTE_API_BASE = 'https://leanote.com/api'
token = ''

def login(email, pwd):
    """Login in Leanote.

    Args:
        email: Email of your account.
        pwd: Password of your account.

    Returns:
        A string represents your login token, empty if login failed.
    """
    payload = {
        'email': email,
        'pwd':   pwd,
    }
    r = req.get(LEANOTE_API_BASE + '/auth/login', params=payload)
    if r.status_code != req.codes.ok:
        print('Login fail, please try again.')

    data = r.json()
    print('Login success, welcome %s (%s).' %(data['Username'], data['Email']))
    global token
    token = data['Token']

def get_notebooks():
    """Get notebooks of logined account.

    Returns:
        A list that contains notebooks' info.
    """
    payload = {
        'token': token,
    }
    r = req.get(LEANOTE_API_BASE + '/notebook/getNotebooks', params=payload)
    if r.status_code != req.codes.ok:
        print('Failed to get notebooks, please try again.')
        return ''
    data = r.json()
    return data

def get_notes(nb_id):
    """Get notes of notebook @nb_id

    Args:
        nb_id: Id of notebook.

    Returns:
        A list that contains notes' info.
    """
    payload = {
        'token': token,
        'notebokkId': nb_id,
    }
    r = req.get(LEANOTE_API_BASE + '/note/getNotes', params=payload)
    if r.status_code != req.codes.ok:
        print('Failed to get notes, please try again.')
        return ''
    data = r.json()
    return data

def get_note(note_id):
    """Get note and its content.

    Args:
        note_id: Id of note.

    Returns:
        Note that contains meta-info and content.
    """
    payload = {
        'token': token,
        'noteId': note_id,
    }
    r = req.get(LEANOTE_API_BASE + '/note/getNoteAndContent', params=payload)
    if r.status_code != req.codes.ok:
        print('Failed to get note, please try again.')
        return ''
    data = r.json()
    return data

def get_image(image_id):
    """Get image by @image_id.

    Args:
        image_id: Id of image.

    Returns:
        Image bytes
    """
    payload = {
        'token': token,
        'fileId': image_id,
    }
    r = req.get(LEANOTE_API_BASE + '/file/getImage', params=payload)
    if r.status_code != req.codes.ok:
        print('Failed to get image, please try again.')
        return ''
    return r.content
    