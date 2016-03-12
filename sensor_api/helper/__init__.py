from sensor_api import login_manager, models


class ValueTypeMapper(object):
    value_types = {
        1: {
            "name": "temperature",
            "short_name": "temp"
        },
        2: {
            "name": "humidity",
            "short_name": "hum"
        }
    }

    def get_id(self, name):
        for i, v in self.value_types.items():
            if v.get("name") == name:
                return i
        return None

    def get_name(self, id):
        v = self.value_types.get(id, {})
        return v.get("name")

    def get_short_name(self, id):
        v = self.value_types.get(id, {})
        return v.get("short_name")


@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

value_types = ValueTypeMapper()
