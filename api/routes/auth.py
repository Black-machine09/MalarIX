from fastapi import APIRouter

from api.schemas.response import LoginRequest, LoginResponse, RegisterRequest

router = APIRouter(tags=["auth"])


@router.post("/auth/login")
def login(body: LoginRequest) -> LoginResponse:
    return LoginResponse(
        token="jwt-token-aqui",
        user={
            "name": "Dr. Ana Costa",
            "specialty": "Hematologista",
            "avatar": None,
        },
    )


@router.post("/auth/register")
def register(body: RegisterRequest) -> dict:
    return {"status": "ok", "message": "Usuário registrado com sucesso."}
