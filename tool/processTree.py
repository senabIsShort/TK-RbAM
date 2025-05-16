import random
from anytree import PreOrderIter, PostOrderIter, Walker
from anytree.util import commonancestors
from tqdm import tqdm
from itertools import product, combinations

def pickRandomNodePair(tree):
    nodes = [node.name for node in PreOrderIter(tree['1.'])]
    # Remove root from list of choices
    nodes.pop(0)
    node1_name, node2_name = random.sample(nodes, 2)
    return node1_name, node2_name

def getCommonAncestor(tree, node1_name, node2_name):
    return commonancestors(tree[node1_name], tree[node2_name])

def distanceBetweenPair(tree, node1_name, node2_name):
    walker = Walker()
    path = walker.walk(tree[node1_name], tree[node2_name])
    upwards, _, downwards = path
    return len(upwards) + len(downwards)

def getNeutralPair(tree, threshold):
    """From given tree, pick 2 nodes that are at least `threshold` distance apart and have the root as their only common ancestor (i.e. arguments that aren't directly related)

    Args:
        tree (dict): dictionary of nodes
        threshold (int): minimum distance between nodes

    Raises:
        LookupError: Raised if a pair of nodes that satisfy the conditions cannot be found after 1000 attempts

    Returns:
        tuple(str, str): Pair of node names
    """
    attempt_limit = 1000
    for _ in range(attempt_limit):
        n1, n2 = pickRandomNodePair(tree)
        rootIsOnlyCommonAncestor = len(getCommonAncestor(tree, n1, n2)) == 1
        if not rootIsOnlyCommonAncestor:
            continue
        # First version used a tree walk to compute distance
        # distance = distanceBetweenPair(tree, n1, n2)
        # Use the already set 'level' attribute of the node to compute it instead
        distance = tree[n1].level + tree[n2].level
        if distance < threshold:
            continue
        return n1, n2
    raise LookupError(f"Could not find a pair of nodes that satisfy the conditions after {attempt_limit} attempts")

def getAllNeutralPairsFromSameTree(tree, threshold):
    """Get all pairs of nodes that are at least `threshold` distance apart and have the root as their only common ancestor (i.e. arguments that aren't directly related)

    Args:
        tree (dict): dictionary of nodes representing the tree
        threshold (int): minimum distance between nodes

    Returns:
        list(tuple(str, str)): List of pairs of node names
    """
    root = tree['1.']
    if root.children is None:
        return []

    branches = []
    for child in root.children:
        # generate list of nodes for each 
        branches.append([node.name for node in PostOrderIter(child)])

    nodePairs = []    
    for branchPair in combinations(branches, 2):
        # generate combination of each node in each branch
        nodePairs += list(product(branchPair[0], branchPair[1]))
    
    neutralPairs = []
    for n1, n2 in tqdm(nodePairs, desc="Finding neutral pairs"):
        if n1 == n2:
            continue
        if (n1, n2) in neutralPairs:
            continue
        rootIsOnlyCommonAncestor = len(getCommonAncestor(tree, n1, n2)) == 1
        if not rootIsOnlyCommonAncestor:
            continue
        # First version used a tree walk to compute distance
        # distance = distanceBetweenPair(tree, n1, n2)
        # Use the already set 'level' attribute of the node to compute it instead
        distance = tree[n1].level + tree[n2].level
        if distance < threshold:
            continue
        # Here, could add test via embedding similarity
        neutralPairs.append((n1, n2))
    return neutralPairs

def getAllNeutralPairsFromDiffTrees(t1, t2):
    """Get all pairs of nodes that are from different trees (i.e. arguments that aren't directly related)

    Args:
        t1 (dict): dictionnary of nodes for the first tree
        t2 (dict): dictionnary of nodes for the second tree

    Returns:
        list[tuple[str, str]]: List of pairs of node names
    """
    nodes1 = [node.name for node in PostOrderIter(t1['1.'])]
    nodes2 = [node.name for node in PostOrderIter(t2['1.'])]
    # Remove roots from lists of choices
    nodes1.pop()
    nodes2.pop()
    neutralPairs = list(product(nodes1, nodes2))
    return neutralPairs

def getNNeutralPairsFromSameTrees(tree, threshold, n = 1000):
    """Get `n` pairs of nodes that are at least `threshold` distance apart and have the root as their only common ancestor (i.e. arguments that aren't directly related)

    Args:
        t1 (dict): dictionnary of nodes
        threshold (int): minimum distance between nodes
        n (int, optional): Number of pairs to generate. Defaults to 1000.

    Returns:
        list[tuple[str, str]]: List of pairs of node names
    """
    root = tree['1.']
    if root.children is None:
        return []

    # Only generate pairs of arguments that are in different branches
    # This guarantees that the root is the only common ancestor
    branches = []
    for child in root.children:
        # generate list of nodes for each 
        branches.append([node.name for node in PostOrderIter(child)])

    nodePairs = []
    for branchPair in combinations(branches, 2):
        # generate combination of each node in each branch
        # same as [(x,y) for x in branchPair[0] for y in branchPair[1]]
        nodePairs += list(product(branchPair[0], branchPair[1]))
    
    # Shuffle the list of pairs to avoid bias
    random.shuffle(nodePairs)
    neutralPairs = []
    # Keep generating pairs until we have enough
    while len(neutralPairs) < n and nodePairs:
        n1, n2 = nodePairs.pop()
        # The three tests below are redundant, but kept just in case
        if n1 == n2:
            continue
        if (n1, n2) in neutralPairs:
            continue
        rootIsOnlyCommonAncestor = len(getCommonAncestor(tree, n1, n2)) == 1
        if not rootIsOnlyCommonAncestor:
            continue
        # First version used a tree walk to compute distance
        # distance = distanceBetweenPair(tree, n1, n2)
        # Use the already set 'level' attribute of the node to compute it instead
        distance = tree[n1].level + tree[n2].level
        if distance < threshold:
            continue
        # Here, could add test via embedding similarity
        neutralPairs.append((n1, n2))
    
    return neutralPairs

def getNNeutralPairsFromDiffTrees(t1, t2, n = 1000):
    """Get `n` pairs of nodes that are from different trees (i.e. arguments that aren't directly related)

    Args:
        t1 (dict): dictionnary of nodes for the first tree
        t2 (dict): dictionnary of nodes for the second tree
        n (int, optional): Number of pairs to generate. Defaults to 1000.

    Returns:
        list[tuple[str, str]]: List of pairs of node names
    """
    allNeutralPairs = getAllNeutralPairsFromDiffTrees(t1, t2)
    neutralPairs = random.sample(allNeutralPairs, n)
    return neutralPairs



def argumentTree2argumentPairTree(node, domains):    
    pairs = []
    
    if len(node.children) == 0:
        return pairs
    elif node.children != None:
        for child in node.children:
            if node.name != "1.":
                pair = {
                    "topArgument"       :   node.toneInput,
                    "subArgument"       :   child.toneInput,
                    "subject"           :   child.subject,
                    "subArgumentLevel"  :   child.level,
                    "domain"            :   domains,
                    "sameTree"        :   True
                }
                if child.stance == "Con":
                    pair["relation"] = "attack"
                else:
                    pair["relation"] = "support"
                pairs.append(pair)

            pairs += argumentTree2argumentPairTree(child, domains)
        
    return pairs


def nodePair2NeutralArgPair(node1, node2, domains_n1, domains_n2, same_tree):
    pair = {
            "topArgument"  :   node1.toneInput,
            "subArgument"  :   node2.toneInput,
            "relation"          :   "neutral"
        }

    if same_tree:
        pair["subject"] = node1.subject
        pair["domain"] = domains_n1
        pair["sameTree"] = True
    else:
        pair["subject"] = node1.subject + " & " + node2.subject
        pair["domain"] = domains_n1 + " & " + domains_n2 if domains_n2 else domains_n1
        pair["sameTree"] = False

    return pair

def namePairs2NeutralArgPairs(tree, nodes, domains_n1, tree2=None, domains_n2=None, same_tree=True):
    pairs = []
    for nodeName1, nodeName2 in nodes:
        node1 = tree[nodeName1]
        if same_tree:
            node2 = tree[nodeName2]
        else:
            node2 = tree2[nodeName2]

        pair = nodePair2NeutralArgPair(node1, node2, domains_n1, domains_n2, same_tree)
        pairs.append(pair)

        if same_tree:
            domains_n2 = domains_n1
        reverse_pair = nodePair2NeutralArgPair(node2, node1, domains_n2, domains_n1, same_tree)
        pairs.append(reverse_pair)

    return pairs