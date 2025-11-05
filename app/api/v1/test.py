from fastapi import APIRouter

router = APIRouter(prefix="/test")

# 메모리 저장 (간단한 테스트용)
fake_users = []

@router.get("/")
def list_users():
    return "hello"
