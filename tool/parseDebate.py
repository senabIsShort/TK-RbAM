import json, re
from anytree import Node

def group_arguments(tableau):
    argGroup = tableau[0]
    i = 1

    while True:

        if i > len(tableau) - 1:
            # Return if you reach the end of tableau
            return [argGroup]

        stance = re.search(r"(Con|Pro)(?::)", tableau[i])
        if stance == None:
            argGroup = argGroup + " " + tableau[i]
            i+=1
        else:
            return [argGroup] + group_arguments(tableau[i:]) 



def rawKialo2Json(input_file):
    """Uses kialoParser script to parse the Kialo file and convert it to a json file.
    script by Edoardo Guido
    edoardo.guido.93@gmail.com
    https://edoardoguido.com

    Args:
        input_file (str): Filename of the Kialo debate downloaded as txt.

    Returns:
        dict: dictionnary containing information about each node, accessible by the node id.
    """
    with open(input_file, 'r') as fi:
        lines = []
        for line in fi:
            if line.startswith("Sources:"):
                break
            lines.append(line.strip())

        lines = [x for x in lines if x]

        # list containing each parsed comment
        result = []

        # we remove the first two lines of the text
        # as we don't need the header
        header = []
        for line in range(0, 4):
            header.append(lines.pop(0))

        subject = header[1]

        lines = group_arguments(lines)

        ##                                            ##
        ##                 REGEDITS              ##
        ##                                            ##
        # iterate every row in the text file
        counter = 1
        for line in lines:

            # find the tree position the comment is in
            tree =  re.search(r"^(\d{1,}.)+", line)

            # find if the comment is Pro or Con
            stance = re.search(r"(Con|Pro)(?::)", line)

            # find the text of the comment
            content = re.search(r"((Con|Pro)(?::\s))(.*)", line)

            # define the hierarchy of the current comment
            # which is based on the tree structure

            parsed = re.findall(r"(\d{1,}(?=\.))+", tree.group())
            level = len(parsed)-1

            # make a dictionary with the single entry
            # and put it at the end of the list
            result.append({
                "Tree": tree.group(),
                "Level": level,
                "Stance": stance.group(1),
                "ToneInput": content.group(3),
                "node_id":subject.replace(" ","_")+"_"+str(counter)
            })

            counter+=1
        
        to_write = json.dumps(result, sort_keys=True, indent=4, separators=(',', ': '))

    trees = [x["Tree"] for x in result]
    trees = ['1.'] + trees

    resultAsDict = { x["Tree"]: x for x in result }

    id2Node = {}


    for idNode in trees:
        if idNode == '1.':
            id2Node[idNode] = Node(idNode, node_id=-1)
        else:
            parentId = idNode[:idNode[:-1].rfind(".")+1]
            id2Node[idNode] = Node(idNode,
                                    parent=id2Node[parentId],
                                    tree=resultAsDict[idNode]["Tree"], 
                                    level=resultAsDict[idNode]["Level"], 
                                    stance=resultAsDict[idNode]["Stance"], 
                                    toneInput=resultAsDict[idNode]["ToneInput"], 
                                    subject=subject,
                                    node_id=resultAsDict[idNode]["node_id"]
    )

    return id2Node