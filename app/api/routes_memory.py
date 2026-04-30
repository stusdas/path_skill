from fastapi import APIRouter
from controllers.memory_controller import MemoryController

router = APIRouter()
controller = MemoryController()

@router.get('/memory')
def get_memory():
    return controller.get_all()

@router.delete('/memory/dynamic/{item_id}')
def delete_dynamic(item_id: str):
    return controller.delete_dynamic(item_id)
