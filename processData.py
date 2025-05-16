import sys, os
import pandas as pd
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from tool.processTree import argumentTree2argumentPairTree, getNNeutralPairsFromSameTrees, getNNeutralPairsFromDiffTrees, namePairs2NeutralArgPairs
from tool.parseDebate import rawKialo2Json
from tool.pairEmbedding import computeRowCosineSimilarity

sys.setrecursionlimit(100000)

urlIdPath = os.path.abspath("rawData/kialo-url-ids.csv")
debatesFolderPath = os.path.abspath(os.path.join(urlIdPath, os.pardir, "debates", "en")) 
outputPath = os.path.abspath("processedData/")

for path in [outputPath, urlIdPath, debatesFolderPath]:
  if not os.path.exists(path):
    if path == outputPath:
      os.makedirs(path)
    else:
      raise FileNotFoundError(f"File or folder not found at {path}. Please check the path and try again.")

kialoUrlIds = pd.read_csv(urlIdPath, index_col=0)
pairs = []

prev_d = None
prev_kialoUrlId = None
prev_t = None

for i, x in tqdm(kialoUrlIds.iterrows(), total=kialoUrlIds.shape[0]):
  try:
    d = x.tags
    kialoUrlId = x.kialoUrlId

    t = rawKialo2Json(os.path.join(debatesFolderPath, kialoUrlId +".txt"))
    
    pairs = pairs + argumentTree2argumentPairTree(t['1.'], d)
    
    neutralPairsSameTree = getNNeutralPairsFromSameTrees(t, 10, len(t))

    pairs = pairs + namePairs2NeutralArgPairs(t, neutralPairsSameTree, d)
    
    if prev_d is not None and prev_t is not None:
      neutralPairsDiffTree = getNNeutralPairsFromDiffTrees(t, prev_t, max(len(t), len(prev_t)))
      
      pairs = pairs + namePairs2NeutralArgPairs(t, neutralPairsDiffTree, d, prev_t, prev_d, same_tree=False)

    prev_d = d
    prev_kialoUrlId = kialoUrlId
    prev_t = t
  except Exception as e:
    continue


argSrc = [x["subArgument"] for x in pairs]
argTrg = [x["topArgument"] for x in pairs]
topic = [x["domain"] for x in pairs]
relations = [x["relation"] for x in pairs]
sameTree = [x["sameTree"] for x in pairs]

pairsDf = pd.DataFrame.from_dict({
  "topic": topic,
  "relation" : relations,
  "argSrc" : argSrc,
  "argTrg" : argTrg,
  "sameTree" : sameTree,
})

# Clean up 
# The arguments still contain some sources, noted by `[124]` for example. We want to remove those.  
# Ideally, we should also remove leftover artifacts like mentions of a page number or stuff like `(p. i.)` but that is another hassle for another day. 

# Remove rows with "See" in either argument
pattern = r"-> See (\d\.)*"
pairsDf = pairsDf[~pairsDf['argSrc'].str.contains(pattern)]
pairsDf = pairsDf[~pairsDf['argTrg'].str.contains(pattern)]

# Remove sources from argSrc and argTrg
pattern = r"\s*\[\d+\]"
pairsDf['argSrc'] = pairsDf['argSrc'].str.replace(pattern, "", regex=True)
pairsDf['argTrg'] = pairsDf['argTrg'].str.replace(pattern, "", regex=True)

# Remove artifacts like (p. 1), (p. i), (p. ii), (p. 65-66), etc.
pattern = r"\(\s*p\.\s*[\di]+(-\d+)*\s*\)"
pairsDf['argSrc'] = pairsDf['argSrc'].str.replace(pattern, "", regex=True)
pairsDf['argTrg'] = pairsDf['argTrg'].str.replace(pattern, "", regex=True)

# Compute Cosine similarity from embeddings
# The intuition being that neutral arguments would tend to have orthogonal embeddings, and thus a cosine similarity of 0.

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", trust_remote_code=True)

tqdm.pandas(desc="Computing similarity for all pairs")

pairsDf['similarity'] = pairsDf.progress_apply(lambda row: computeRowCosineSimilarity(row, model), axis=1)

supp = pairsDf[pairsDf['relation'] == 'support']
att = pairsDf[pairsDf['relation'] == 'attack']
neut_sameTree = pairsDf[(pairsDf['relation'] == 'neutral') & (pairsDf['sameTree'] == True)]
neut_diffTree = pairsDf[(pairsDf['relation'] == 'neutral') & (pairsDf['sameTree'] == False)]
neut = pd.concat([neut_sameTree, neut_diffTree], ignore_index=True)

pairsDf.to_csv(os.path.join(outputPath, "kialoPairsRaw.csv"), index=False)

# # Post processing
# The idea here is to keep only the pairs of neutral arguments that are most neutral, by using the computed Cosine similarity between their embeddings.

kp = pd.read_csv(os.path.join(outputPath, "kialoPairsRaw.csv"))

kp_neut_sameTree= kp[(kp['relation'] == 'neutral') & (kp['sameTree'] == True)]
kp_neut_diffTree= kp[(kp['relation'] == 'neutral') & (kp['sameTree'] == False)]

# ### Filter out neutral rows
# 
# The objective is to have roughly 100k neutrals with a 50:50 split between sameTree and !sameTree in order to have a balanced dataset to sample from.  
# Using the conclusion from the previous exploration, we can determine that it is safe to keep only the most dissimilar pairs (i.e. based on the similarity score in ascending order).

nb_supp = kp.value_counts('relation')['support']
nb_att = kp.value_counts('relation')['attack']

target_nb_neut = (nb_supp + nb_att)//2

# Sort by similarity and keep enough rows to reach target_nb_neut
kp_neut_sameTree.sort_values('similarity', inplace=True)
kp_neut_sameTree = kp_neut_sameTree[:target_nb_neut//2]

kp_neut_diffTree.sort_values('similarity', inplace=True)
kp_neut_diffTree = kp_neut_diffTree[:target_nb_neut//2]

# Concatenate enough neutrals to create a balanced dataset

kp_supp = kp[kp['relation'] == 'support']
kp_att = kp[kp['relation'] == 'attack']

kp_final = pd.concat([kp_supp, kp_att, kp_neut_sameTree, kp_neut_diffTree], ignore_index=True)

kp_final.value_counts('relation')

# Save the final Dataset

kp_final.to_csv(os.path.join(outputPath, "kialoPairs.csv"), index=False)
