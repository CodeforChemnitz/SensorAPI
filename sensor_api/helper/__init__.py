from sensor_api import login_manager, models


@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))
