from sqlalchemy import select
from datetime import datetime

from users.models import UserFeedState, UserPlaceHistory


async def get_or_create_user_state(session, user_id):
    """Получаем или создаем состояние пользователя"""
    stmt = select(UserFeedState).where(UserFeedState.user_id == user_id)
    result = await session.execute(stmt)
    state = result.scalar_one_or_none()

    if not state:
        state = UserFeedState(user_id=user_id)
        session.add(state)
        await session.commit()

    return state


async def get_user_place_history(session, user_id, place_id):
    """Получаем историю взаимодействия с местом"""
    stmt = select(UserPlaceHistory).where(
        UserPlaceHistory.user_id == user_id,
        UserPlaceHistory.place_id == place_id
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def update_place_history(session, user_id, place_id, liked=False, disliked=False, saved=False):
    """Обновляем историю показа места"""
    history = await get_user_place_history(session, user_id, place_id)

    if not history:
        history = UserPlaceHistory(user_id=user_id, place_id=place_id)
        session.add(history)

    history.show_count += 1
    history.last_shown = datetime.now()

    if liked:
        history.liked = True
    if disliked:
        history.disliked = True
    if saved:
        history.saved = True

    await session.commit()
    return history
