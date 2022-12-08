import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )
    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Create a list of next pages and calculate the probability of choosing them
    # considering the damping factor
    next = list(corpus[page])
    if next != []:
        probability = round(damping_factor / len(next) + (1 - damping_factor) / (len(next) + 1), 4)
    # Handle if there are not any links
    else:
        probability = round(1 / len(corpus), 4)
        distribution = dict()
        for page in corpus:
            distribution[page] = probability
        return distribution

    # Assign the probability for each of the links in a dict "link" - "probability"
    distribution = dict()
    distribution[page] = round((1 - damping_factor) / (len(next) + 1), 4)
    for pagename in next:
        distribution[pagename] = probability

    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Calculate the probability distribution for each of the pages in the corpus
    # and store them in dict for further use
    model = dict()
    for page in corpus:
        model[page] = transition_model(corpus, page, damping_factor)

    # Sample pages choosing the next page based on the probability from the probability distribution
    pages = list(corpus.keys())
    pageRank = init_dict(pages)
    currPage = pages[random.randrange(0, len(pages) - 1)]
    for i in range(n):
        pageRank[currPage] += 1 / SAMPLES
        currPage = choose_page(currPage, model, pages)

    return(pageRank)


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Set initial values for each of the pages
    pageRank = dict()
    pages = list(corpus.keys())
    for page in pages:
        pageRank[page] = 1 / len(pages)

    # Iterate over all pages until no one changes by less than 0.001
    done = list()
    while True:
        if len(done) == len(pages):
            break
        for page in pages:
            oldRank = pageRank[page]
            newRank = new_pagerank(page, pageRank, corpus)
            pageRank[page] = newRank
            if difference(oldRank, newRank):
                if page not in done:
                    done.append(page)
    pageRank = fixPR(pageRank)
    return pageRank


def new_pagerank(page, pageRank, corpus):
    """
    Calculates the new pagerank for a page
    """
    linkPage = list()
    numLinks = dict()
    for key in corpus.keys():
        if page in corpus[key]:
            linkPage.append(key)
    if linkPage == list():
        linkPage = corpus.keys()
        for item in linkPage:
            numLinks[item] = len(linkPage)
    else:
        for item in linkPage:
            numLinks[item] = len(corpus[item])

    rank = 0
    for item in linkPage:
        rank += pageRank[item] / numLinks[item]
    rank = (DAMPING * rank) + (1 - DAMPING) / len(corpus.keys())
    return rank

def init_dict(pages):
    """
    Initial dict with starting value 0
    """
    initDict = dict()
    for page in pages:
        initDict[page] = 0
    return initDict


def choose_page(page, distribution, key):
    """
    Chooses a page with the given probability of each page
    """
    weightedPages = list(distribution[page])
    weightedValues = list()
    for item in weightedPages:
        weightedValues.append(distribution[page][item])
    nextPage = random.choices(weightedPages, weightedValues, k=1)
    return nextPage[0]


def difference(x, y):
    """
    Returns True if difference is less than 0.001
    """
    if x > y:
        if x - y < 0.001:
            return True
    else:
        if y - x < 0.001:
            return True
    return False


def fixPR(pageRank):
    """
    Fixes pagerank values so they add up to 1
    """
    total = 0
    for key in pageRank:
        total += pageRank[key]
    for key in pageRank:
        pageRank[key] = pageRank[key] / total

    return pageRank


if __name__ == "__main__":
    main()
