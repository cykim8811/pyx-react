
def renderObject(obj, user):
    if hasattr(obj, '__render__'):
        return obj.__render__(user)
    elif isinstance(obj, list):
        return renderList(obj, user)
    elif isinstance(obj, dict):
        return renderDict(obj, user)
    elif isinstance(obj, str):
        return renderString(obj, user)
    elif isinstance(obj, int) or isinstance(obj, float):
        return renderNumber(obj, user)
    elif isinstance(obj, bool):
        return renderBool(obj, user)
    elif obj is None:
        return renderNone(obj, user)
    else:
        return obj


def renderList(obj, user):
    return (
        <div style={{display: 'flex', flexDirection: 'row'}}>
            
        </div>
    )
