import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4



def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    # Read data from the file   
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader)
        
        # Append data into a evidence and label list
        evidence = list()
        labels = list()
        for row in reader:
            evidence.append(
                list(nameToValue(cell) for cell in zip(row[:17], range(17)))
            )
            labels.append(1 if row[17] == "TRUE" else 0)

    return evidence, labels
    

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    nPos, nNeg, pPos, pNeg = 0, 0, 0, 0
    for tuple in zip(labels, predictions):
        if tuple[0] == 1:
            nPos += 1
            if tuple[1] == 1:
                pPos += 1
        else:
            nNeg += 1
            if tuple[1] == 0:
                pNeg += 1
    return pPos / nPos, pNeg / nNeg
        


def nameToValue(cell):
    """
    Returns the value of the give name so it can be stored in evidence correctly
    """
    intValues = [0, 2, 4, 11, 12, 13, 14]
    floatValues = [1, 3, 5, 6, 7, 8, 9]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "June", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    # Check if cell already is a int or float value
    if cell[1] in intValues:
        return int(cell[0])
    elif cell[1] in floatValues:
        return float(cell[0])
    elif cell[1] == 15:
        return 1 if cell[0] == "Returning_Visitor" else 0
    elif cell[1] == 16:
        return 1 if cell[0] == "TRUE" else 0
    else:
        for month in zip(months, range(12)):
            if cell[0] == month[0]:
                return month[1] 
    

if __name__ == "__main__":
    main()
