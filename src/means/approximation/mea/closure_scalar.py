import sympy as sp
from means.util.sympyhelpers import substitute_all


class ClosureBase(object):

    _max_order = None
    _min_order = 1

    def __init__(self,max_order, multivariate=True):

        self._max_order = max_order
        self.__is_multivariate = multivariate
        if self._min_order > max_order:
            raise ValueError("This closure method requires `max_order` to be >= {0}".format(self._min_order))
    @property
    def is_multivariate(self):
        return self.__is_multivariate

    @property
    def max_order(self):
        return self._max_order

    def _compute_raw_moments(self, n_counter, k_counter):
        raise NotImplementedError("ParametricCloser is an abstract class.\
                                  `compute_closed_raw_moments()` is not implemented. ")

    def _compute_closed_central_moments(self, central_from_raw_exprs, n_counter, k_counter):
        r"""
        Replace raw moment terms in central moment expressions by parameters (e.g. mean, variance, covariances)
        parameters such as variance/covariance (i.e. central moments) and first order raw moment (i.e. means)

        :param central_from_raw_exprs: the expression of central moments in terms of raw moments
        :param k_counter: a list of :class:`~means.approximation.ode_problem.Moment`\s representing raw moments
        :return: the central moments where raw moments have been replaced by parametric expressions
        :rtype: sympy.Matrix
        """

        closed_raw_moments = self._compute_raw_moments(n_counter, k_counter)
        assert(len(central_from_raw_exprs) == len(closed_raw_moments))
        # raw moment lef hand side symbol
        raw_symbols = [raw.symbol for raw in k_counter if raw.order > 1]

        # we want to replace raw moments symbols with closed raw moment expressions (in terms of variances/means)
        substitution_pairs = zip(raw_symbols, closed_raw_moments)
        # so we can obtain expression of central moments in terms of low order raw moments
        closed_central_moments = substitute_all(central_from_raw_exprs, substitution_pairs)
        return closed_central_moments


    def close(self, mfk, central_from_raw_exprs, n_counter, k_counter):

        """
        In MFK, replaces symbol for high order (order == max_order+1) by parametric expressions.
        That is expressions depending on lower order moments such as means, variances, covariances and so on.

        :param mfk: the right hand side equations containing symbols for high order central moments
        :param central_from_raw_exprs: expressions of central moments in terms of raw moments
        :param n_counter: a list of :class:`~means.approximation.ode_problem.Moment`\s representing central moments
        :param k_counter: a list of :class:`~means.approximation.ode_problem.Moment`\s representing raw moments
        :return: the modified MFK
        """

        # we obtain expressions for central moments in terms of variances/covariances
        closed_central_moments = self._compute_closed_central_moments(central_from_raw_exprs, n_counter, k_counter)
        # set mixed central moment to zero iff univariate
        closed_central_moments = self.set_mixed_moments_to_zero(closed_central_moments, n_counter)

        # retrieve central moments from problem moment. Typically, :math: `[yx2, yx3, ...,yxN]`.

        # now we want to replace the new mfk (i.e. without highest order moment) any
        # symbol for highest order central moment by the corresponding expression (computed above)

        positive_n_counter = [n for n in n_counter if n.order > 0]
        substitutions_pairs = [(n.symbol, ccm) for n,ccm in
                               zip(positive_n_counter, closed_central_moments) if n.order > self.max_order]
        new_mfk = substitute_all(mfk, substitutions_pairs)

        return new_mfk

    def set_mixed_moments_to_zero(self, closed_central_moments, n_counter):
        '''
        In univariate case, set the cross-terms to 0.
        :param closed_central_moments: matrix of closed central moment
        :param n_counter: a list of moment symbols
        :return:  a matrix of new closed central moments with cross-terms equal to 0
        '''
        positive_n_counter = [n for n in n_counter if n.order > 1]
        if self.is_multivariate:
            return closed_central_moments
        else:
            return [0 if n.is_mixed else ccm for n,ccm in zip(positive_n_counter, closed_central_moments)]


class ScalarClosure(ClosureBase):

    def __init__(self,max_order,value=0):
        super(ScalarClosure, self).__init__(max_order, False)
        self.__value = value

    @property
    def value(self):
        return self.__value
    def _compute_closed_central_moments(self, central_from_raw_exprs, n_counter, k_counter):
        """
        Replace raw moment terms in central moment expressions by parameters (e.g. mean, variance, covariances)


        :param central_from_raw_exprs: the expression of central moments in terms of raw moments
        :param k_counter: a list of :class:`~means.approximation.ode_problem.Moment`\s representing raw moments
        :return: the central moments where raw moments have been replaced by parametric expressions
        :rtype: sympy.Matrix
        """

        closed_central_moments = sp.Matrix([sp.Integer(self.__value)] * len(central_from_raw_exprs))
        return closed_central_moments