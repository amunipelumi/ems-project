from fastapi import APIRouter


router = APIRouter(
    tags=['Events']
)


@router.post('/events')
def create_event():
    return {'message': 'successful'}