import os

from plyer import notification

from assets import ICONS_ROOT_PATH


def show_notification(title: str, message: str, app_name='Trader', app_icon='', timeout=4):
    notification.notify(
        title=title,
        message=message,
        app_name=app_name,
        app_icon=os.path.join(ICONS_ROOT_PATH, app_icon) if app_icon else '',
        timeout=timeout,
    )
