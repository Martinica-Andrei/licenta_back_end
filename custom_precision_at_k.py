from scipy.sparse import coo_matrix
import numpy as np
def custom_precision_at_k(model, test_interactions, train_interactions=None, k=10, user_features=None, 
                          item_features=None, num_threads=1, check_intersections=True):
    """
    The difference between this and the lightfm precision_at_k is for users that have less reviews than k.
    The precision for these user is the number of true positive predictions divided by the count of total true positives.
    """
    # computes rank only for interactions that are positive and not in train_interactions
    csr_ranks = model.predict_rank(
        test_interactions=test_interactions,
        train_interactions=train_interactions,
        item_features=item_features,
        user_features=user_features,
        num_threads=num_threads,
        check_intersections=check_intersections
    )
    # convert to coo_matrix to take rows
    coo_ranks = coo_matrix(csr_ranks)
    # np.unique returns rows in ascending order, take only rows that have at least one value.
    p_csr_ranks = csr_ranks[np.unique(coo_ranks.row)]
    # convert to coo_matrix to take rows from p_csr_ranks
    p_coo_ranks = coo_matrix(p_csr_ranks)
    # get number of values in each row
    row_count = p_csr_ranks.getnnz(axis=1)
    # clip row count to k
    row_count_clipped = np.clip(row_count, a_min=None, a_max=k)
    # get corresponding number of top ratings required for each row (user)
    each_value_row_count = row_count_clipped[p_coo_ranks.row]

    p1_csr_ranks = p_csr_ranks.copy()
    # compare each rating if it is in top ratings
    p1_csr_ranks.data = (p1_csr_ranks.data < each_value_row_count)
    # take the sum for each row (user) and divide by the required top ratings
    precision_each_row = np.squeeze(np.array(p1_csr_ranks.sum(axis=1))) / row_count_clipped
    return precision_each_row