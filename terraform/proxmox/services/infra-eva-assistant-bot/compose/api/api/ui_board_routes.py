"""Card operations for the authenticated EVA web application."""

import re

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse

from api.ui_session_routes import require_ui_owner
from core.config import CONTENT_BOARD_ID, FOCALBOARD_BOARD_ID
from integrations import focalboard_client

router = APIRouter(
    prefix="/ui/board/v2/boards",
    tags=["eva-ui"],
    dependencies=[Depends(require_ui_owner)],
)
block_id = re.compile(r"[A-Za-z0-9]{1,64}")


def require_board(board_id: str) -> None:
    if not block_id.fullmatch(board_id) or board_id not in (FOCALBOARD_BOARD_ID, CONTENT_BOARD_ID):
        raise HTTPException(404, "Tablero no disponible")


async def request_cards(method: str, board_id: str, card_id=None, payload=None):
    try:
        status, body = await focalboard_client.request_board_cards(method, board_id, card_id, payload)
    except focalboard_client.BoardAccessError:
        raise HTTPException(502, "Focalboard no disponible") from None
    if status == 404:
        raise HTTPException(404, "Tarjeta o tablero no encontrado")
    return status, body


async def require_card(board_id: str, card_id: str) -> None:
    if not block_id.fullmatch(card_id):
        raise HTTPException(404, "Tarjeta no encontrada")
    _, cards = await request_cards("GET", board_id)
    if not isinstance(cards, list):
        raise HTTPException(502, "Respuesta inválida de Focalboard")
    if not any(isinstance(card, dict) and card.get("id") == card_id and
               card.get("type") == "card" and card.get("boardId") == board_id for card in cards):
        raise HTTPException(404, "Tarjeta no encontrada")


@router.get("/{board_id}/blocks")
async def list_cards(board_id: str):
    require_board(board_id)
    _, cards = await request_cards("GET", board_id)
    if not isinstance(cards, list):
        raise HTTPException(502, "Respuesta inválida de Focalboard")
    return cards


@router.post("/{board_id}/blocks")
async def create_card(board_id: str, payload: list[dict]):
    require_board(board_id)
    if len(payload) != 1:
        raise HTTPException(422, "Se requiere una tarjeta")
    card = payload[0]
    if (card.get("type") != "card" or card.get("boardId") != board_id or
            card.get("parentId") != board_id or
            not isinstance(card.get("id"), str) or not block_id.fullmatch(card["id"])):
        raise HTTPException(422, "Tarjeta inválida para el tablero")
    status, body = await request_cards("POST", board_id, payload=payload)
    return JSONResponse(content=body, status_code=status)


@router.patch("/{board_id}/blocks/{card_id}", status_code=204)
async def update_card(board_id: str, card_id: str, payload: dict):
    require_board(board_id)
    fields = payload.get("updatedFields", {})
    if (not payload or payload.keys() - {"title", "updatedFields"} or
            not isinstance(fields, dict) or fields.keys() - {"title", "properties"}):
        raise HTTPException(422, "Cambios de tarjeta inválidos")
    await require_card(board_id, card_id)
    await request_cards("PATCH", board_id, card_id, payload)
    return Response(status_code=204)


@router.delete("/{board_id}/blocks/{card_id}", status_code=204)
async def delete_card(board_id: str, card_id: str):
    require_board(board_id)
    await require_card(board_id, card_id)
    await request_cards("DELETE", board_id, card_id)
    return Response(status_code=204)
