<template>
    <div class="row">
        <div class="input-group mb-3">
            <input type="text" v-model="query" @input="searchChanged" class="form-control" placeholder="Search members..."/>
            <div class="input-group-append" v-if="isLoading">
                <span class="input-group-text"><spinner></spinner></span>
            </div>
        </div>
    </div>
</template>

<script>
    import {throttle} from 'lodash';
    import Spinner from '../Spinner'

    export default {
        name: "Search",
        components: {
            Spinner,
        },
        data() {
            return {
                query: 'empty',
            }
        },
        computed: {
            isLoading() {
                return this.$store.state.memberSearch.loading;
            },
        },
        methods: {
            searchChanged: throttle(function () {
                this.$store.dispatch('memberSearch/search', this.query)
            }, 200)
        },
    }
</script>

<style scoped>

</style>