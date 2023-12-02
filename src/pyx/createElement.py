
def createElement(tag, props, *children):
    return {
        '__type__': 'element',
        'tag': tag,
        'props': props,
        'children': children
    }

