from fastapi import APIRouter


router = APIRouter(
    tags=['Authentication']
)


@router.post('/signin')
def login():
    return {'message': 'successful'}

