import Vue from 'vue'
import Vuex from 'vuex'
import MemberSearchStore from '@/store/MemberSearch'

Vue.use(Vuex);

export default new Vuex.Store({
    modules: {
        memberSearch: MemberSearchStore,
    },
    state: {},
    mutations: {},
    actions: {}
})
