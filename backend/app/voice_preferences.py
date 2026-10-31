"""Preferencias de voz guardadas en Turso: qué documentos nuevos se leen solos."""

from typing import Annotated, Final, Literal

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from app.api import CurrentIdentity, Users
from app.database import ConnectionFactory, database_operation
from app.errors import ApiError, ErrorCode

AutoReadMode = Literal['off', 'agent', 'all']

# Sin fila guardada, la lectura automática está apagada.
DEFAULT_AUTO_READ_MODE: Final[AutoReadMode] = 'off'

FIND_MODE: Final = '''
    SELECT auto_read_mode
    FROM app_voice_preferences
    WHERE user_id = ?
'''

SAVE_MODE: Final = '''
    INSERT INTO app_voice_preferences (
        user_id,
        auto_read_mode
    ) VALUES (?, ?)
    ON CONFLICT (user_id)
    DO UPDATE SET auto_read_mode = excluded.auto_read_mode
'''

router = APIRouter(tags=['preferencias de voz'])


class VoicePreferencesBody(BaseModel):
    model_config = ConfigDict(extra='forbid')
    auto_read_mode: AutoReadMode = Field(alias='autoReadMode')


class VoicePreferences:
    def __init__(self, connect: ConnectionFactory) -> None:
        self._connect = connect

    def auto_read_mode(self, owner: str) -> AutoReadMode:
        with database_operation(self._connect) as connection:
            row = connection.execute(FIND_MODE, (owner,)).fetchone()
        return row[0] if row else DEFAULT_AUTO_READ_MODE

    def set_auto_read_mode(self, owner: str, mode: AutoReadMode) -> None:
        with database_operation(self._connect) as connection:
            connection.execute(SAVE_MODE, (owner, mode))
            connection.commit()


def voice_preferences(request: Request) -> VoicePreferences:
    preferences = request.app.state.voice_preferences
    if preferences is None:
        raise ApiError(ErrorCode.PROVIDER_UNAVAILABLE)
    return preferences


Preferences = Annotated[VoicePreferences, Depends(voice_preferences)]


@router.get('/voice/preferences')
def read_voice_preferences(identity: CurrentIdentity, users: Users,
                           preferences: Preferences, response: Response):
    owner = existing_owner(identity, users)
    response.headers['Cache-Control'] = 'no-store'
    return {'autoReadMode': preferences.auto_read_mode(owner)}


@router.put('/voice/preferences')
def update_voice_preferences(body: VoicePreferencesBody, identity: CurrentIdentity,
                             users: Users, preferences: Preferences):
    owner = existing_owner(identity, users)
    preferences.set_auto_read_mode(owner, body.auto_read_mode)
    return {'autoReadMode': body.auto_read_mode}


def existing_owner(identity: CurrentIdentity, users: Users) -> str:
    # El perfil se crea al entrar en la web; sin perfil no hay preferencias.
    user = users.find(identity)
    if user is None:
        raise ApiError(ErrorCode.NOT_FOUND)
    return user.id
