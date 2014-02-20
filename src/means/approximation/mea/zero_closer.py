import sympy as sp
from means.util.sympyhelpers import substitute_all

class CloserBase(object):

    _n_moments = None
    def __init__(self,n_moments):
        self._n_moments = n_moments
    @property
    def n_moments(self):
        return self._n_moments

    def close(self,central_moments_exprs, dmu_over_dt, central_from_raw_exprs, species, n_counter, k_counter):
        raise NotImplementedError("CloserBase is an abstract class. `close()` is not implemented. ")

    def generate_problem_left_hand_side(self, n_counter, k_counter):
        # concatenate the symbols for first order raw moments (means)
        prob_moments_over_dt = [k for k in k_counter if k.order == 1]
        # and the higher order central moments (variances, covariances,...)
        prob_moments_over_dt += [n for n in n_counter if n.order > 1]
        return prob_moments_over_dt

    def generate_mass_fluctuation_kinetics(self, central_moments, dmu_over_dt, n_counter):
        """
        :param central_moments:
        :param n_counter:
        :param dmu_over_dt:
        :return: the right hand side of the final ODEs
        """
        # symbols for central moments
        central_moments_symbols = sp.Matrix([n.symbol for n in n_counter])
        # try to simplify an expression. returns the original expression if fail
        # # todo remove this when we do not need it anymore
        def try_to_simplify(expr):
            try:
                return sp.simplify(expr)
            except:
                pass
            return expr

        # rhs for the first order raw moment
        mfk = [e for e in dmu_over_dt * central_moments_symbols]
        # rhs for the higher order raw moments
        mfk += [(sp.Matrix(cm).T * central_moments_symbols)[0] for cm in central_moments.tolist()]

        mfk = sp.Matrix(mfk)
        mfk = mfk.applyfunc(try_to_simplify)

        return mfk


class ParametricCloser(CloserBase):

    def __init__(self,n_moments, multivariate=True):
        super(ParametricCloser, self).__init__(n_moments)
        self.__is_multivariate = multivariate

    @property
    def is_multivariate(self):
        return self.__is_multivariate

    def set_mixed_moments_to_zero(self, closed_central_moments,prob_moments):
        '''
        In univariate case, set the cross-terms to 0.
        :param closed_central_moments: matrix of closed central moment
        :param prob_moments: moment matrix
        :return:  a matrix of new closed central moments with cross-terms equal to 0
        '''
        n_counter = [n for n in prob_moments if n.order > 1]
        if self.is_multivariate:
            return closed_central_moments
        else:
            return [0 if n.is_mixed else ccm for n,ccm in zip(n_counter, closed_central_moments)]


    def compute_raw_moments(self, problem_moment):
        raise NotImplementedError("ParametricCloser is an abstract class.\
                                  `compute_closed_raw_moments()` is not implemented. ")

    def compute_closed_central_moments(self, central_from_raw_exprs, k_counter, problem_moments):
        """
        Replace raw moment terms in central moment expressions by parameters (e.g. mean, variance, covariances)

        :param closed_raw_moments: the expression of all raw moments (expect 0th) in terms of
        parameters such as variance/covariance (i.e. central moments) and first order raw moment (i.e. means)
        :param central_from_raw_exprs: the expression of central moments in terms of raw moments
        :param k_counter: a list of `Moment` object corresponding to raw moment symbols an descriptors
        :return: the central moments where raw moments have been replaced by parametric expressions
        :rtype: sympy.Matrix
        """
        closed_raw_moments = self.compute_raw_moments(problem_moments)
        # raw moment lef hand side symbol
        raw_symbols = [raw.symbol for raw in k_counter if raw.order > 1]
        # we want to replace raw moments symbols with closed raw moment expressions (in terms of variances/means)
        substitution_pairs = zip(raw_symbols, closed_raw_moments)
        # so we can obtain expression of central moments in terms of low order raw moments
        closed_central_moments = substitute_all(central_from_raw_exprs, substitution_pairs)
        return closed_central_moments

    def close(self,central_moments_exprs, dmu_over_dt, central_from_raw_exprs, species, n_counter, k_counter):

        mfk = self.generate_mass_fluctuation_kinetics(central_moments_exprs, dmu_over_dt, n_counter)

        prob_lhs = self.generate_problem_left_hand_side(n_counter, k_counter)

        mfk, prob_lhs = self.parametric_closer_wrapper(mfk, central_from_raw_exprs, k_counter, prob_lhs)

        return mfk, prob_lhs

    def parametric_closer_wrapper(self, mfk, central_from_raw_exprs, k_counter, prob_lhs):
        n_moments = self.n_moments
        # we obtain expressions for central moments in terms of variances/covariances
        closed_central_moments = self.compute_closed_central_moments(central_from_raw_exprs, k_counter, prob_lhs)
        # set mixed central moment to zero iff univariate
        closed_central_moments = self.set_mixed_moments_to_zero(closed_central_moments,prob_lhs)
        # we remove ODEs of highest order in mfk
        new_mfk = sp.Matrix([mfk for mfk, pm in zip(mfk, prob_lhs) if pm.order < n_moments])

        # retrieve central moments from problem moment. Typically, :math: `[yx2, yx3, ...,yxN]`.
        n_counter = [n for n in prob_lhs if n.order > 1]
        # now we want to replace the new mfk (i.e. without highest order moment) any
        # symbol for highest order central moment by the corresponding expression (computed above)
        substitutions_pairs = [(n.symbol, ccm) for n,ccm in zip(n_counter, closed_central_moments) if n.order == n_moments]
        new_mfk = substitute_all(new_mfk, substitutions_pairs)
        # we also update problem moments (aka lhs) to match remaining rhs (aka mkf)
        new_prob_moments = [pm for pm in prob_lhs if pm.order < n_moments]
        return new_mfk, new_prob_moments

class ZeroCloser(CloserBase):
    def close(self,central_moments_exprs, dmu_over_dt, central_from_raw_exprs, species, n_counter, k_counter):
        mfk = self.generate_mass_fluctuation_kinetics(central_moments_exprs, dmu_over_dt, n_counter)
        prob_lhs = self.generate_problem_left_hand_side(n_counter, k_counter)
        return mfk, prob_lhs