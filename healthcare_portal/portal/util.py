from textblob import TextBlob


def determine_sentiment(question, answer, question_weight=0.2):
    """
    Determine the weighted sentiment based on the question and answer.

    Args:
    - question (str): The text of the question.
    - answer (str): The text of the answer.
    - question_weight (float): The weight assigned to the sentiment of the question.
                              The weight for the answer sentiment is (1 - question_weight).
                              Defaults to 0.2.

    Returns:
    - float: The weighted sentiment value.
    """

    question_sentiment = TextBlob(question).sentiment.polarity
    answer_sentiment = TextBlob(answer).sentiment.polarity

    weighted_sentiment = (question_weight * question_sentiment) + (
        (1 - question_weight) * answer_sentiment
    )
    return weighted_sentiment
