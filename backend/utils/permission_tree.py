from typing import Any


def build_permission_tree(permissions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    构建权限树形结构
    
    Args:
        permissions: 权限列表，每个权限包含 id, parent_id, name, code, type 等字段
    
    Returns:
        树形结构的权限列表
    """
    permission_map = {perm["id"]: perm.copy() for perm in permissions}
    
    for perm in permission_map.values():
        perm["children"] = []
    
    tree = []
    
    for perm in permission_map.values():
        parent_id = perm.get("parent_id")
        if parent_id is None:
            tree.append(perm)
        else:
            parent = permission_map.get(parent_id)
            if parent:
                parent["children"].append(perm)
            else:
                tree.append(perm)
    
    return _sort_tree(tree)


def _sort_tree(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """按ID排序权限树节点"""
    nodes.sort(key=lambda x: x.get("id", 0))
    for node in nodes:
        if node.get("children"):
            node["children"] = _sort_tree(node["children"])
    return nodes


def flatten_permission_tree(tree: list[dict[str, Any]]) -> list[int]:
    """
    展平权限树，返回所有权限ID列表
    
    Args:
        tree: 权限树
    
    Returns:
        所有权限ID列表
    """
    result = []
    
    def _flatten(nodes: list[dict[str, Any]]):
        for node in nodes:
            result.append(node["id"])
            if node.get("children"):
                _flatten(node["children"])
    
    _flatten(tree)
    return result


def get_all_descendant_ids(permission_id: int, permissions: list[dict[str, Any]]) -> list[int]:
    """
    获取权限的所有子孙权限ID
    
    Args:
        permission_id: 权限ID
        permissions: 所有权限列表
    
    Returns:
        子孙权限ID列表（包含自己）
    """
    result = [permission_id]
    permission_map = {perm["id"]: perm for perm in permissions}
    
    def _find_children(pid: int):
        for perm in permissions:
            if perm.get("parent_id") == pid:
                result.append(perm["id"])
                _find_children(perm["id"])
    
    _find_children(permission_id)
    return result


def filter_permissions_by_codes(
    permissions: list[dict[str, Any]],
    allowed_codes: set[str],
) -> list[dict[str, Any]]:
    """
    根据权限编码过滤权限列表
    
    Args:
        permissions: 所有权限列表
        allowed_codes: 允许的权限编码集合
    
    Returns:
        过滤后的权限列表
    """
    return [perm for perm in permissions if perm["code"] in allowed_codes]


def build_user_permission_tree(
    all_permissions: list[dict[str, Any]],
    user_permission_codes: set[str],
) -> list[dict[str, Any]]:
    """
    构建用户的权限树（只包含用户有权限的节点）
    
    Args:
        all_permissions: 所有权限列表
        user_permission_codes: 用户拥有的权限编码集合
    
    Returns:
        用户的权限树
    """
    filtered_perms = filter_permissions_by_codes(all_permissions, user_permission_codes)
    return build_permission_tree(filtered_perms)
