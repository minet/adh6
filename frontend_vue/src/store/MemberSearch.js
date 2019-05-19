import {MemberGateway} from '@/openapi'

export default {
    namespaced: true,
    state: {
        query: '',
        loading: false,
        result: [],
    },
    mutations: {
        setQuery(state, q) {
            state.query = q;
        },
        setLoading(state, l) {
            state.loading = l;
        },
        setResult(state, r) {
            state.result = r;
        }
    },
    actions: {
        async search(context, query) {

            context.commit('setLoading', true);
            context.commit('setQuery', query);

            const result = await MemberGateway.memberGet({terms: query});

            context.commit('setLoading', false);
            context.commit('setResult', result);
        }
    }
};