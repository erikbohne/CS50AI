import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probabilities = list()

    for person in people:
        parent = haveParents(person, people)
        personGenes = 1 if person in one_gene else 2 if person in two_genes else 0
        currP = 1

        # If person does not have parents
        if not parent:
            currP *= PROBS["gene"][personGenes]

        else:
            fatherGenes = nGenes(people[person]["father"], one_gene, two_genes)
            motherGenes = nGenes(people[person]["mother"], one_gene, two_genes)

            if personGenes == 2:
                # Only way is getting 1 from each parent
                currP *= fromParent(fatherGenes, True) * fromParent(motherGenes, True)
            elif personGenes == 1:
                # Only way is getting from father and not from mother, or not from father and from mother
                currP *= (fromParent(fatherGenes, True) * fromParent(motherGenes, False)
                + fromParent(fatherGenes, False) * fromParent(motherGenes, True))
            else:
                # Only way is getting not getting the gene from either
                currP *= fromParent(fatherGenes, False) * fromParent(motherGenes, False)

        # Multiply by chance of having/not having the trait given n genes
        currP *= PROBS["trait"][personGenes][True if person in have_trait else False]

        probabilities.append(currP)


    return product(probabilities)


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        probabilities[person]["trait"][True if person in have_trait else False] += p
        probabilities[person]["gene"][nGenes(person, one_gene, two_genes)] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        total = 0
        for value in probabilities[person]["gene"]:
            total += probabilities[person]["gene"][value]
        for value in probabilities[person]["gene"]:
            probabilities[person]["gene"][value] = probabilities[person]["gene"][value] / total

        total = 0
        for value in probabilities[person]["trait"]:
            total += probabilities[person]["trait"][value]
        for value in probabilities[person]["trait"]:
            probabilities[person]["trait"][value] = probabilities[person]["trait"][value] / total


def haveParents(person, people):
    """
    Checks if person has parents and returns True if so
    """
    if people[person]["mother"] == None and people[person]["father"] == None:
        return False
    else:
        return True


def nGenes(person, one_gene, two_genes):
    """
    Returns number of genes the person has
    """
    if person in one_gene:
        return 1
    elif person in two_genes:
        return 2
    else:
        return 0


def product(list):
    """
    Returns the product of all values in a list
    """
    product = 1
    for x in list:
        product = x * product
    return product


def fromParent(genesParent, giveGene):
    """
    Returns porbability that the gene comes from this parent
    """
    if genesParent == 2:
        if giveGene:
            return 1 - PROBS["mutation"]
        else:
            return PROBS["mutation"]
    elif genesParent == 1:
        if giveGene:
            return 0.5
        else:
            return 0.5
    else:
        if giveGene:
            return PROBS["mutation"]
        else:
            return 1 - PROBS["mutation"]


if __name__ == "__main__":
    main()
