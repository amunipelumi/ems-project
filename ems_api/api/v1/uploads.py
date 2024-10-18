##
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from gridfs import GridFS

##
from ...core import oauth2, config
from ...__ import prefix_

##
import os


MDB_NAME = str(os.getenv('MDB_NAME'))
MDB_COLL = str(os.getenv('MDB_COLL'))

router = APIRouter(
    prefix=f'{prefix_}/uploads',
    tags=['Uploads'],
)

FILE_TYPES = {"image/jpeg", "image/png"}

@router.post('/', status_code=201)
async def upload_doc(
        file: UploadFile=File(...),
        client = Depends(config.mongo_client),
        auth_user: dict=Depends(oauth2.current_user)
        ):
    gfs = GridFS(client[MDB_NAME])
    if file.content_type not in FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail='Please upload a valid file type..'
        )
    try:
        content = await file.read()
        gfs.put(content, filename=file.filename, content_type=file.content_type)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail='Unable to upload file, please try again..'
        )
    return {'message': f'{file.filename} uploaded successfully..'}
