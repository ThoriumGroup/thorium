def allNodes(filter=None, group=nuke.root(), recurseGroups=False):
    """ Wraps nuke.allNodes to allow filtering and recursing

    Args:
        filter=None : (str)
            A Nuke node name to filter for. Must be exact match.

        group=nuke.root() : (<nuke.nodes.Group>)
            A Nuke node of type `Group` to search within. If not provided, will
            begin the search at the root level.

        recurseGroups=False : (bool)
            If we should continue our search into any encountered group nodes.

    Returns:
        [<nuke.Node>]
            A list of any Nuke nodes found whose Class matches the given filter.

    Raises:
        N/A

    """
    # First we'll check if we need to execute our custom allNodes function.
    # If we don't have a filter AND recurseGroups=True, `nuke.allNodes` will
    # do the job fine.
    if filter and recurseGroups:
        # Search for every node, then filter using a list comprehension.
        # Faster than searching for all groups, then searching again
        # for the filter.
        all_nodes = nuke.allNodes(group, recurseGroups=True)

        return [node for node in all_nodes if node.Class() == filter]

    else:
        # We just need to execute Nuke's `nuke.allNodes` function.
        # But we need to modify our list of keyword arguments and remove
        # the filter argument if it wasn't passed, otherwise Nuke chokes.
        kwargs = {
            'filter': filter,
            'group': group,
            'recurseGroups': recurseGroups
        }

        # Remove empty arguments
        if not filter:
            del kwargs['filter']

        return nuke.allNodes(**kwargs)
