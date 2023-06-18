
def get(context):
    print(__name__.split('.')[0])
    return context.preferences.addons[__name__.split('.')[0]].preferences
