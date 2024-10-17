##
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

##
from ...core import oauth2, config
from ...__ import prefix_



router = APIRouter(
    prefix=f'{prefix_}/uploads',
    tags=['Uploads'],
)

FILE_TYPES = {"image/jpeg", "image/png", "application/pdf"}

router.post('/', status_code=201)
def upload_doc(
        file: UploadFile=File(...),
        gfs=Depends(config.doc_upload),
        auth_user: dict=Depends(oauth2.current_user)
        ):
    if file.content_type not in FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail='Please upload a valid file type..'
        )
    try:
        content = file.read()
        gfs.put(content, filename=file.filename, content_type=file.content_type)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail='Unable to upload file, please try again..'
        )
    return {'message': 'File uploaded successfully..'}
