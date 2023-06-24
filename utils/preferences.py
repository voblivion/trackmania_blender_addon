
def get(context):
    return context.preferences.addons[__name__.split('.')[0]].preferences
