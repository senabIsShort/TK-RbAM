# Ternary Kialo RbAM (TK-RbAM)

Ternary Kialo RbAM (TK-RbAM) is a dataset for Relation-based Argument Mining (RbAM) comprising pairs of arguments from the most active and best ranked Kialo.com debates.  

The pairs are categorized as either `support`, `attack` or `neutral`.  

## Usage

Create a virtual environment using your preferred method :

### Environment

#### Conda

You can use the `environment.yml` file provided in this repository. It'll create an environment using the name `tk-rbam`.

```sh
conda env create -f environment.yml
conda activate tk-rbam
```

#### Venv

You can use the `requirements.txt` file provided in this repository.  
Create and activate the environment using :

```sh
python -m .venv-tk-rbam
source .venv-tk-rbam/bin/activate
```

Then install the packages using pip :

```sh
pip install -r requirements.txt
```

### Scripts

After installing the necessary libraries in a virtual environment, simply run :

- **#1** : the [`getDebatesData.py`](getDebatesData.py) script to download the debates in text format and sort them by language
  - at the root of this repository, run `python getDebatesData.py`
  - this will create/update the [`kialo-url-ids.csv`](rawData/kialo/kialo-url-ids.csv) file that contains the URLs of all debates to be parsed. By default, the file is created inside the [rawData](rawData/) folder, while the debate text files are downloaded within a subfolder named [debates](rawData/debates/).

> Make sure you change the placeholder `kialoUsername` and `secret` variables at the top of the file. You may also change the `downloadPath` variable to a preferred target folder in which the text files will be downloaded.
>
> ```python
> kialoUsername  = "PLACEHOLDER"
> secret              = "PLACEHOLDER"
> downloadPath = os.path.abspath("rawData/debates")
> ```

- **#2** : the [`processData.py`](processData.py) script to parse, process and generate the dataset in csv file (`kialoPairs.csv`)
  - at the root of this repository, run `python processData.py`
  - this will generate two CSV files inside, by default, the [`processedData`](processedData/) directory
    - `kialoPairsRaw.csv` is a complete dataset containing unfiltered rows (around a million, with more neutral pairs)
    - `kialoPairs.csv` is the final TK-BRbM dataset obtained after filtering some of them (down to around 280k rows)

> You may change the `urlIdPath` and `debatesFolderPath` variables at the top of the file to a different source location for the `kialo-url-ids.csv` and kialo debates TXT exported files. `outputPath` is the preferred target folder in which the dataset CSV files will be saved.
>
> ```python
> urlIdPath = os.path.abspath("rawData/kialo-url-ids.csv")
> debatesFolderPath = os.path.abspath(os.path.join(urlIdPath, os.pardir, "debates", "en")) 
> outputPath = os.path.abspath("processedData/")
> ```

The following sections in this README describe the dataset and aim to explain the creation and transformation process.

### Dataset format

Both the `kialoPairs.csv` and `kialoPairsRaw.csv` datasets are comprised of the following 6 columns :

- `topic` : list of strings - all the tags attributed to the debate the argument pair is taken from;
- `argSrc` : string - the argument contained within the child node, attacking or supporting its parent node (or not if neutral);
- `argTrg` : string - the argument contained within the parent node, attacked or supported by a child node (or not if neutral);
- `relation` : string corresponding to the relation argSrc -> argTrg. Values are either `support`, `attack` or `neutral`;
- `sameTree` : boolean - whether or not the pair of arguments are from the same tree/debate;
- `similarity` : float - cosine similarity computed on embeddings produced by a language model.

## Sources

The neutral relations in this dataset have partly been generated following the idea of Sahitaj et al. in :

> SAHITAJ, Premtim, et al. "From Construction to Application: Advancing Argument Mining with the Large-Scale KIALOPRIME Dataset." Computational Models of Argument. IOS Press, 2024. 229-240.

The source code is an extension of the work from user [4mbroise](https://github.com/4mbroise) in their repository [ADC](https://github.com/4mbroise/ADC).

## Scraping

The debates are downloaded using [`Selenium`](https://www.selenium.dev/) and a Kialo account.  

Since not all the debates are in English, but a vast majority is, the debates are sorted depending on the detected language using [`langdetect`](https://github.com/Mimino666/langdetect). The files are copied into appropriate directories, but a move is possible by replacing `shutil.copy(file_path, new_file_path)` by `shutil.move(file_path, new_file_path)`.  

## Parsing

The debates are parsed into a tree structure using [`anytree`](https://anytree.readthedocs.io/en/latest/) and then manipulated to create appropriate pairs of neutral arguments.

## Neutral pair generation

A first attempt at generating pairs was to generate all possible pairs before selection.  
In order to make the process faster, only a desired amount of pairs are generated for each debate.

Unlike the KialoPrime dataset, this one also includes generated pairs from the same debates. This better reflects real debates where some arguments simply aren't related to each other because they attack or support different claims.  
The following section will explain the decision process for generatings these pairs.  

Note that all neutral pairs are symmetrical, i.e if `Arg 1 - Arg 2` is `neutral`, then the reverse pair `Arg 2 - Arg 1` is also included as `neutral` in the dataset.

### Neutral pairs from the same tree

This section describes the process for generating pairs of arguments deemed as `neutral` from the same debate (i.e. "same tree").

The intuition behind the generation of these pairs can be summed up as the following :

- Pick two nodes (arguments) at random in the tree (debate)
- Assert that the root is their only common ancestor
- Assert that the distance between the two nodes is higher than a custom threshold

This is the core idea behind it. Further adjustments have been implemented to make the process faster, such as computing only pairs of arguments from different branches of the debate. This reduces the number of pairs unnecessarily processed as well as guaranteeing that the root is the only common ancestor.  
After having all the pairs generated, we shuffle the list of pairs and verify distance between nodes of a pair, if the distance is higher than the set threshold, keep the pair and repeat until enough pairs have been generated this way.  

The number of pairs generated has been set to the number of nodes in a tree (biggest of the two for different trees).

The distance threshold was set to 10.

## Dataset processing

After generating the aformentionned pairs, each argument in a pair is encoded using a language model (`sentence-transformers/all-MiniLM-L6-v2` from the HuggingFace library [`Sentence Transformers`](https://www.sbert.net/)). The cosine similarity of these embeddings is then computed to estimate the quality of the pair : pairs with a similarity score of 0 should be most neutral.  

The dataset includes pairs in ascending similarity score.

Finally, the number of neutral rows kept is decided as the average between the number of support and attack relations, guaranteeing a balanced 33:33:33 split between all relations. Furthermore, the neutral relations are evenly split between pairs of arguments coming from the same debate and from different ones.

### Data cleanup

The data scraped from Kialo includes arguments in the form of `-> See 1.1.1.1.1.`, these arguments (e.g. A1) repeat previous ones (e.g. A2) and create a potential issues if kept. These have been left out of the dataset completely.

Aside from that, the arguments themselves contain source annotations in the form of numbers between brackets (e.g. `[34]`) and sometimes paragraph or page annotations such as `(p. i)`, `(p. 3)` or even `(p. 64-65)`. These annotations have been removed from arguments using regular expressions before computing the embeddings and cosine similarity of pairs.

In order, the regular expression used, in Python raw string format are :

- `r"-> See (\d\.)*"` for "See" arguments;
- `r"\s*\[\d+\]"` for source annotations between brackets;
- `r"\(\s*p\.\s*[\di]+(-\d+)*\s*\)"` for remaining paragraph/page annotations.

## Dataset statistics

The Ternary Kialo RBAM is characterized by the following :

### Table 1 : Distribution of each relation types in the dataset

|  | support | attack | neutral |
|-|-|-|-|
| Number of rows | 93 130 | 92 830 | 92 980 |
| Percentage of rows | 33.39% | 33.28% | 33.33% |

### Table 2 : Mean & standard deviation of argument length by column

|  | argSrc | argTrg |
|-|-|-|
| Mean length | 151.21 | 137.86 |
| Standard deviation | 76.17 | 73.36 |
