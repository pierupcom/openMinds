import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
import mimetypes


from open_webui.apps.webui.models.folders import (
    FolderForm,
    FolderItemsUpdateForm,
    FolderModel,
    Folders,
)
from open_webui.apps.webui.models.chats import Chats

from open_webui.config import UPLOAD_DIR
from open_webui.env import SRC_LOG_LEVELS
from open_webui.constants import ERROR_MESSAGES


from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse


from open_webui.utils.utils import get_admin_user, get_verified_user

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])


router = APIRouter()


############################
# Get Folders
############################


@router.get("/", response_model=list[FolderModel])
async def get_folders(user=Depends(get_verified_user)):
    folders = Folders.get_folders_by_user_id(user.id)
    return folders


############################
# Create Folder
############################


@router.post("/")
def create_folder(form_data: FolderForm, user=Depends(get_verified_user)):
    folder = Folders.get_folder_by_parent_id_and_user_id_and_name(
        None, user.id, form_data.name
    )

    if folder:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT("Folder already exists"),
        )

    try:
        folder = Folders.insert_new_folder(user.id, form_data.name)
        return folder
    except Exception as e:
        log.exception(e)
        log.error("Error creating folder")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT("Error creating folder"),
        )


############################
# Get Folders By Id
############################


@router.get("/{id}", response_model=Optional[FolderModel])
async def get_folder_by_id(id: str, user=Depends(get_verified_user)):
    folder = Folders.get_folder_by_id_and_user_id(id, user.id)
    if folder:
        return folder
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# Update Folder Name By Id
############################


@router.post("/{id}/update")
async def update_folder_name_by_id(
    id: str, form_data: FolderForm, user=Depends(get_verified_user)
):
    folder = Folders.get_folder_by_id_and_user_id(id, user.id)
    if folder:
        existing_folder = Folders.get_folder_by_parent_id_and_user_id_and_name(
            folder.parent_id, user.id, form_data.name
        )
        if existing_folder:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("Folder already exists"),
            )

        try:
            folder = Folders.update_folder_name_by_id_and_user_id(
                id, user.id, form_data.name
            )
            return folder
        except Exception as e:
            log.exception(e)
            log.error(f"Error updating folder: {id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("Error updating folder"),
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# Update Folder Name By Id
############################


class FolderParentIdForm(BaseModel):
    parent_id: str


@router.post("/{id}/update/parent")
async def update_folder_parent_id_by_id(
    id: str, form_data: FolderParentIdForm, user=Depends(get_verified_user)
):
    folder = Folders.get_folder_by_id_and_user_id(id, user.id)
    if folder:
        existing_folder = Folders.get_folder_by_parent_id_and_user_id_and_name(
            form_data.parent_id, user.id, folder.name
        )

        if existing_folder:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("Folder already exists"),
            )

        try:
            folder = Folders.update_folder_parent_id_by_id_and_user_id(
                id, user.id, form_data.parent_id
            )
            return folder
        except Exception as e:
            log.exception(e)
            log.error(f"Error updating folder: {id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("Error updating folder"),
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# Update Folder Items By Id
############################


@router.post("/{id}/update/items")
async def update_folder_items_by_id(
    id: str, form_data: FolderItemsUpdateForm, user=Depends(get_verified_user)
):
    folder = Folders.get_folder_by_id_and_user_id(id, user.id)
    if folder:
        try:
            folder = Folders.update_folder_items_by_id_and_user_id(
                id, user.id, form_data.items
            )
            return folder
        except Exception as e:
            log.exception(e)
            log.error(f"Error updating folder: {id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("Error updating folder"),
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# Delete Folder By Id
############################


@router.delete("/{id}")
async def delete_folder_by_id(id: str, user=Depends(get_verified_user)):
    folder = Folders.get_folder_by_id_and_user_id(id, user.id)
    if folder:
        try:
            result = Folders.delete_folder_by_id_and_user_id(id, user.id)
            return result
        except Exception as e:
            log.exception(e)
            log.error(f"Error deleting folder: {id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("Error deleting folder"),
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )