from scipy import spatial


def getEmbeddingSimilarity(arg1, arg2):
    return 1 - spatial.distance.cosine(arg1, arg2)

def getEmbeddingsFromArgs(args, model):
    # For nomic models with prompt prefix
    # prompt_prefix = 'clustering: '    
    prompt_prefix = ''    
    sentences = []
    for arg in list(args):
        sentence = prompt_prefix+arg
        sentences.append(sentence)
    embeddings = model.encode(sentences)
    return embeddings

def computeRowCosineSimilarity(row, model):
    embeddings = getEmbeddingsFromArgs([row["argSrc"], row["argTrg"]], model)
    return getEmbeddingSimilarity(embeddings[0], embeddings[1])