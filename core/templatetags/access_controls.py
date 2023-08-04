from django import template

register = template.Library()


class OnlyAdminsNode(template.Node):
    """Restrict content to only admin or super admins"""
    def __init__(self, node_list):
        self.node_list = node_list

    def render(self, context):
        request = context.get("request")
        if request.user.is_admin() or request.user.is_super_admin():
            return self.node_list.render(context)
        return ""


class OnlySuperAdminsNode(template.Node):
    def __init__(self, node_list):
        self.node_list = node_list

    def render(self, context):
        request = context.get("request")
        if request.user.is_super_admin():
            return self.node_list.render(context)
        return ""


@register.tag(name="onlysuperadmins")
def only_super_admins(parser, token):
    node_list = parser.parse(("endonlysuperadmins", ))
    parser.delete_first_token()
    return OnlySuperAdminsNode(node_list)


@register.tag(name="onlyadmins")
def only_admins(parser, token):
    node_list = parser.parse(("endonlyadmins", ))
    parser.delete_first_token()
    return OnlyAdminsNode(node_list)
